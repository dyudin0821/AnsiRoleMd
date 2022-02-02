#!/usr/bin/env python3
from setuptools import setup


setup(name='ansirolemd',
      version='0.1.0',
      description='Script to generate md  Ansible role',
      author='Denis Yudin',
      author_email='dyudin@intermedia.com',
      license='Apache License 2.0',
      packages=['ansirolemd'],
      install_requires=open('requirements.txt').readlines(),
    )
