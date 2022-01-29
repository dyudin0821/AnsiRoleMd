# ansirolemd
A python script to generate Markdown table from [Ansible](https://github.com/ansible/ansible) role for documentation.

## Prerequisites
1. python3
2. [jinja2](https://jinja.palletsprojects.com/en/3.0.x/)
3. yaml

## Installation
1.Install the needed python packages
  
  ``` shell
  pip3 install -r requirements.txt
  ```
2.Add a execution permissions to the script

  ```shell
  sudo chmod +x ansirolemd.py
  ```

3. Run the script!

## Running the script
To run the script all you need is to run the command in this format:
```shell
./ansirolemd.py -src=/path/to/role -dst=/path/to/save/README.md -desc="Description of the role"
```


