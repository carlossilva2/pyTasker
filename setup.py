import os
import sys

from setuptools import find_packages, setup
from Tasker.__version__ import __version__

if sys.argv[-1] == "build":
    os.system("python setup.py sdist")
    sys.exit()

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist")
    os.system("twine upload dist/*")
    sys.exit()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="Carlos Silva",
    author_email="carlos.miguel.silva@protonmail.com",
    name="pyTasker",
    description="Run pipelines on your own computer for better automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=__version__,
    url="https://github.com/carlossilva2/pyTasker",
    packages=find_packages(),
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["tasker = Tasker.__main__:main"]},
    install_requires=["requests", "pychalk", "questionary", "validators", "pywin32", "typing_extensions"],
    package_data={},
    project_urls={
        "Source": "https://github.com/carlossilva2/pyTasker",
        "Documentation": "https://cmsilva.gitbook.io/pytasker/",
    },
)
