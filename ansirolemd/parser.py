#!/usr/bin/env python3
import os
import re
import yaml

from typing import Optional, Any
from jinja2 import FileSystemLoader, Environment, meta
from ansirolemd.exception import AnsiRoleMdException
from ansirolemd.types import Varible, SupportPlatform


def parse_dict_variable(var_name: str, var_values: dict, table_vars: dict) -> None:
    """ Parse Ansible hashmap values.
        Retrieves the hashmap variable and add
        him and all sub-variable to the table.
        Args:
            :param var_name:  the name of the variable.
            :param var_values: The sub-variables needed parsing.
            :param table_vars: The table to fill with the variables.
        Raise:
            AnsiRoleMdException: An Error while parsing the default files.
    """
    # Run on each sub-variable
    for sub_key, sub_value in var_values.items():
        # Append to variable name the sub-variable name
        full_key = "{}:{}".format(var_name, sub_key)

        # Check that there is no duplications in declaration
        if full_key in table_vars:
            raise AnsiRoleMdException("There are duplications in the variables names.")
        # Check if the sub-variable is hashmap also
        if type(sub_value) is dict:
            # Closures
            parse_dict_variable(full_key, sub_value, table_vars)
        else:
            table_vars[full_key] = Varible(full_key, "No", sub_value)


def parse_defaults(file_path: str, table: dict) -> None:
    """ Parse Ansible default file.
        Retrieves file path and table to fill with the Ansible role variables.
        Args:
        :param file_path:  The path to the yaml task file.
        :param table: The table to fill with the variables.
    """
    # Open default file
    with open(file_path, "r") as stream:
        try:
            # Parse defaults with yaml parser
            defaults = yaml.safe_load(stream) or {}
            # Run on each default key
            for key, value in defaults.items():
                # Check if there is duplication of variable default declaration
                if key in table:
                    raise AnsiRoleMdException("There are duplications in the variables names.")
                # Check if the value is  dictionary to parse sub variables
                elif type(value) is dict:
                    parse_dict_variable(key, value, table)
                # Check if there is default or lookup function in use
                elif "default" in str(value) and "lookup" in str(value):
                    clean_value = value[value.find("default"):-2].strip()
                    clean_value = clean_value[len("default") + 1:value[value.find("default"):-2].find(",")]
                    table[key] = Varible(key, "No", clean_value)
                else:
                    table[key] = Varible(key, "No", value)
        except yaml.YAMLError as err:
            print(err)


def parse_used_variable(used_var: str) -> str:
    """ Parse Ansible variable that in use.
        Retrieves used variable string and return only the variable name.
        Example:
            receive - {{ some_var.out }}
            return - some_var
        Args:
            :param used_var:  The used variable string
    Returns:
       Return the variable name.
    """
    # Remove double curly brackets
    clean_var = used_var[2:-2].strip()

    # Check if variable 'function' is used, if yes remove usage
    if clean_var.find(".") != -1:
        clean_var = clean_var[:clean_var.find(".")]
    # Check if variable used as dictionary, if yes remove usage
    if clean_var.find("[") != -1:
        clean_var = clean_var.replace("[", ":").replace("]", "").replace("\'", "")
    return clean_var


def scan_variables(line: str, table: dict, registered_vars: list) -> None:
    """ Scan for used variables ansible task file.
       Retrieves a line and add to table all used variables.
       Args:
            :param line:  The line to Scan.
            :param table: The table to fill with the variables.
            :param registered_vars: A list to add the facts to
       Returns:
          None.
       """
    # Check if there is a variable used in the current line
    match_obj = re.findall("{{[A-Za-z0-9 -_.|]*}}", line)
    if match_obj:
        # Run on each founded variable
        for match in match_obj:
            # Get the variable name without the using syntax
            clean_value = parse_used_variable(match)
            # Add to the table if its not already in it and not in the resisted variables
            if clean_value and clean_value not in registered_vars and clean_value not in table:
                table[clean_value] = Varible(clean_value, "Yes", "-")


def parse_tasks(file_path: str,
                table: dict,
                recursive: Optional[bool] = False,
                registered_vars: Optional[dict] = None) -> Any:
    """ Parse Ansible task file.
    Retrieves file path and table to fill with the Ansible role variables.
    Args:
        :param file_path:  The path to the yaml task file.
        :param table: The table to fill with the variables.
        :param recursive: Run recursively on every include of other ansible task that included.
        :param registered_vars: List of registered variables.
    Returns:
       A list of the files the function ran on.
       A list of registered variables
    """
    if registered_vars is None:
        registered_vars = []

    scanned_files = [file_path]
    sub_task = None
    index = 0

    lines = [line.rstrip('\n') for line in open(file_path)]

    # Run on each line in the task
    while index < len(lines):
        line = lines[index]
        vars_check = True

        # check if there is register declaration
        register = re.search("register: .*", line)

        if register:
            # Get the variable that registered and saved it in the registered list
            clean_value = register.group().replace("register:", "").strip()
            registered_vars.append(clean_value)
            vars_check = False
        elif recursive:
            # Check if there is include declaration
            sub_task = re.search("include: .*", line)

        if sub_task:
            # Get the included file save it and parse it
            sub_task_path = "{}/{}".format(os.path.dirname(file_path),
                                           sub_task.group().replace("include:", "").strip())
            if os.path.exists(sub_task_path):
                sc_files, reg_vars = parse_tasks(file_path=sub_task_path, table=table)
                scanned_files += sc_files
                registered_vars += reg_vars
            else:
                print("The file {} did not found.".format(sub_task_path))
                vars_check = False
        elif vars_check:
            scan_variables(line, table, registered_vars)
        # Move to the next line
        index += 1

    return scanned_files, registered_vars


def parse_templates(file_path: str, table: dict, registered_vars: Optional[list] = None) -> None:
    """ Parse Ansible template file.
        Retrieves file path and table to fill with the Ansible used variables.
        Args:
            :param file_path:  The path to the yaml task file.
            :param table: The table to fill with the variables.
            :param registered_vars: A list of variable registered in runtime.
    """
    # Initialize the registered variable list if not initialized already
    if registered_vars is None:
        registered_vars = []

    # Build a Jinja2 environment
    env = Environment(autoescape=False, loader=FileSystemLoader(os.path.dirname(file_path)))
    template_source = env.loader.get_source(env, os.path.basename(file_path))[0]

    # Parse the content of the template
    parsed_content = env.parse(template_source)

    # Get undeclared variable that in use
    undec_vars = meta.find_undeclared_variables(parsed_content)
    for value in undec_vars:
        if value not in registered_vars and value not in table:
            table[value] = Varible(value, "Yes", "-")


def parse_support_platform(file_path: str, table: dict) -> None:
    """ Parse Ansible meta file.
        Retrieves a file path and a table to populate with a list of supported operating systems and their versions
    :param file_path:  The path to the meta/main.yml file.
    :param table: The table to fill with the information.
    """
    with open(file_path, 'r') as stream:
        try:
            meta = yaml.safe_load(stream) or {}
            for key, value in meta.items():
                if "galaxy_info" in key:
                    for sub_key, sub_value in value.items():
                        if type(sub_value) is list and sub_key == "platforms":
                            for platforms in sub_value:
                                for version in platforms.get('versions'):
                                    table[version] = SupportPlatform(platforms.get('name'), version)
        except yaml.YAMLError as err:
            print(err)