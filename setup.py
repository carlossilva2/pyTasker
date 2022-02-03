import os
import sys

from setuptools import setup, find_packages

if sys.argv[-1] == 'build':
    os.system('python setup.py sdist')
    sys.exit()

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist')
    os.system('twine upload dist/*')
    sys.exit()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author = "Carlos Silva",
    author_email = "carlos.miguel.silva@protonmail.com",
    name = "pyTasker",
    description = "Run pipelines on your own computer for better automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version = "0.2.0",
    url="https://gitlab.com/carlossilva2/tasker",
    packages = find_packages(),
    license="GPLv3",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
        'Typing :: Typed'
    ],
    python_requires='>=3.9',
    entry_points = {
        "console_scripts": [
            "tasker = Tasker.__main__:main"
        ]
    },
    install_requires = [

    ],
    package_data={
        "static": ["*"]
    },
    project_urls={
        "Source": "https://gitlab.com/carlossilva2/tasker"
    }
)