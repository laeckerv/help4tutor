#!/usr/bin/env python

from setuptools import setup, find_packages # Always prefer setuptools over distutils

name="help4tutors"

def get_version(relpath="__init__.py"):
	"""read version info from file without importing it"""
	from os.path import dirname, join
	for line in open(join(dirname(__file__), name, relpath)):
		if '__version__' in line:
			if '"' in line:
				return line.split('"')[1]
			elif "'" in line:
				return line.split("'")[1]

setup(
	name=name,
	description='A utility that make the life of a tutor easier.',
	version=get_version(),
	author='Lars Eckervogt',
	author_email='code@eckervogt.eu',
	packages=find_packages(),
	keywords='tutor, gitlab, helper',
	entry_points={
		'console_scripts': [
			'help4tutor=help4tutor:main',
		],
	},
	classifierts=[
		'Environment :: Console',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: Utilities',
	],
)

