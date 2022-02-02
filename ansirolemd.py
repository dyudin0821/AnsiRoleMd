#!/usr/bin/env python3
import sys
import os
import argparse
from typing import Tuple, Any

from ansirolemd.parser import parse_tasks, parse_defaults, parse_support_platform
from ansirolemd.build_md import build_readme


def init_args() -> Tuple[Any, Any, Any]:
    parser = argparse.ArgumentParser(description="Generate readme for Ansible Role")
    parser.add_argument('-src', type=str, help="The path to the ansbile role")
    parser.add_argument('-dst', type=str, help="The path to save the README.md")
    parser.add_argument('-desc', type=str, help="Description of the role")
    args = parser.parse_args()

    if len(sys.argv) < 2:
        sys.exit(parser.print_help())

    return args.src, args.dst, args.desc


def main() -> None:
    vars_table = {}
    support_os_table = {}
    src, dst, desc = init_args()

    if os.path.exists(dst):
        print("The output destination already exists.")
        exit(-1)

    if not os.path.exists(src):
        raise Exception("{} does not exists.".format(src))

    # Parse all the default files in the role
    if os.path.exists(src + "/defaults"):
        for subdir, dirs, files in os.walk(src + "/defaults"):
            for file in files:
                parse_defaults((os.path.join(subdir, file)), vars_table)
                print(f"Defualt {os.path.join(subdir, file)}")

    # Parse main.yml task recursively, if main.yml exists
    if os.path.exists(src + "/tasks"):
        scanned_files, registered_vars = parse_tasks(file_path=os.path.join(src, "tasks/main.yml"), table=vars_table,
                                                     recursive=True)
        print("Files scanned:\n\t\t" + '\n\t\t'.join(scanned_files))
    else:
        raise Exception(f"{src}/task/main.yml does not exists.")

    # Parse all supported OS into a role
    if os.path.exists(src + "/meta/main.yml"):
        parse_support_platform(file_path=os.path.join(src, "meta/main.yml"), table=support_os_table)
        print(f"Defualt {os.path.join(src, 'meta/main.yml')}")
    else:
        raise Exception(f"{src}/meta/main.yml does not exists.")

    with open(dst, "w") as readme_file:
        # Generate the markdown table from the collected variables
        readme_file.write(build_readme(os.path.basename(src), role_description=desc, role_vars=vars_table, role_platform=support_os_table))


if __name__ == "__main__":
    sys.exit(main())
