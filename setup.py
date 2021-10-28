from setuptools import setup

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='ModulesToGoogle',
    version='0.1',
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    url='',
    license='https://creativecommons.org/licenses/by/3.0/',
    author='Jay van Schyndel',
    author_email='jay.vanschyndel@monash.edu',
    description='ModulesToGoogle, upload a .csv file to a Google Sheet',
    install_requires=[
                       "google-api-python-client",
                       "PyYAML",
                       "dateutils>=0.6.6"
                   ],
    entry_points={
        "console_scripts": [
            "modules-to-google=ModulesToGoogle.__main__:main",
        ],
        "gui_scripts": [],
    },
)
