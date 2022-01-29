from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='ansirolemd',
      version='0.1',
      description='Script to generate md  Ansible role',
      url='https://github.com/dyudin0821/AnsiRoleMd',
      author='dyudin0821',
      author_email='denistu2191@gmail.com',
      license='MIT',
      packages=['ansirolemd'],
      install_requires=required,
      zip_safe=False)
