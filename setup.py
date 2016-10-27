#!/usr/bin/env python
"""
Install wagtailtranslations using setuptools
"""
import sys

from setuptools import find_packages, setup

with open('wagtailtranslations/version.py', 'r') as f:
    version = None
    exec(f.read())

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='wagtailtranslations',
    version=version,
    description='Page translation plugin for Wagtail',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@takeflight.com.au',
    url='https://github.com/takeflight/wagtailtranslations/',

    install_requires=['wagtail>=1.7'],
    zip_safe=False,
    license='BSD License',

    packages=find_packages(exclude=['tests*']),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
