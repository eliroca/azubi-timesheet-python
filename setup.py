#!/usr/bin/env python3

from setuptools import setup, find_packages

REQUIRES="requirements.txt"


def requires(filename='requirements.txt'):
    """Returns a list of all pip requirements
    :param filename: the Pip requirement file
    (usually 'requirements.txt')
    :return: list of modules
    :rtype: list
    """
    with open(filename, 'r+t') as pipreq:
        for line in pipreq:
            line = line.strip()
            if not line or line[0:2].strip() in ("#", "##", "-r"):
                continue
            yield line


setup(
    name="azubi-timesheet-python",
    version="0.9",
    author="Elisei Roca",
    author_email="",
    url="https://github.com/eliroca/azubi-timesheet-python",
    license="MIT",
    project_urls={
        "Bug Tracker": "https://github.com/eliroca/azubi-timesheet-python/issues",
        "Documentation": "https://github.com/eliroca/azubi-timesheet-python/blob/master/README.md",
        "Source Code": "https://github.com/eliroca/azubi-timesheet-python",
        },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        ],
    keywords="azubi timesheet python hours",

    # setup_requires="",
    install_requires=list(requires(REQUIRES)),

    scripts=["azubi-timesheet.py"],
    packages=find_packages("."),
)

