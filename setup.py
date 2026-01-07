from setuptools import setup
from setuptools.config import read_configuration

config = read_configuration('pyproject.toml')
setup(**config['tool']['setuptools'])
