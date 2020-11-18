from setuptools import setup
import ast
import sys

setup_requires = ['setuptools >= 30.3.0']
if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requires.append('pytest-runner')


setup(description="pylogstash",
      long_description=open('README.md').read(),
      version="0.1.15",
      setup_requires=setup_requires)
