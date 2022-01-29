import re
import collections
from pprint import pprint

from jinja2 import Environment, PackageLoader
from typing import Optional
from ansirolemd.markdown import TableMarkdown
from ansirolemd.exception import AnsiRoleMdException


def clear_ansible_vars(table: dict) -> None:
    """ Remove from the table the unneccesery ansible variables like:
        - ansible_*
        - item/item.*
        - hostvars
        - lookup
    Args:
        :param table:  Dictionary which the key is string and the key is Entry structure.
    Returns: None
    Raises:
        AnsiRoleMdException: An error occurred accessing the big table.Table object.
    """
    invalid_keys = []
    # Check that the table is ok
    if type(table) is None:
        raise AnsiRoleMdException("The table is null or empty!")

    for key in table.keys():
        # Check if the variable is known ansible/jinja variables
        if (key == "item" or "lookup(" in key or
                bool(re.findall("^ansible_.*", key)) or
                bool(re.findall("^hostvars.*", key)) or
                bool(re.findall("^item:.*", key))):
            invalid_keys.append(key)

    # Remove invalid entries
    for key in invalid_keys:
        del table[key]


def build_readme(role_name: str,
                 role_description: Optional[str] = None,
                 role_vars: Optional[dict] = None,
                 role_platform: Optional[dict] = None) -> str:
    """ Rendering a File Template
    :param role_name: Ansible role name
    :param role_description: Ansible role description from meta/main.yml
    :param role_vars: Table of role variables with description
    :param role_platform: Table of operating systems with version supporting the role
    :param role_author: Role author from meta/main.yml
    :param role_license: Role license from meta/main.yml
    :return:
    """
    clear_ansible_vars(role_vars)
    order_vars = collections.OrderedDict(sorted(role_vars.items()))
    # order_os = collections.OrderedDict(sorted(role_platform.items()))
    os_matrix = []
    variable_matrix = []
    for _, value in order_vars.items():
        variable_matrix += [
            [str(value.m_name), value.m_description, value.m_required, str(value.m_default), value.m_value, value.m_example]
        ]
    for _, os in role_platform.items():
        os_matrix += [[os.os, str(os.version)]]

    table_vars = TableMarkdown(["Name", "Description", "Required", "Default", "Values", "Examples"], variable_matrix)
    table_os = TableMarkdown(["OS", "Version"], os_matrix)
    variable_table = table_vars.render()
    platform_table = table_os.render()
    env = Environment(loader=PackageLoader('ansirolemd', '.'))
    template = env.get_template('template/README.md.j2')
    return template.render(role_name=role_name, role_description=role_description, variable_table=variable_table,
                           platform_table=platform_table)

