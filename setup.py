from setuptools import setup

setup(
    author = "Carlos Silva",
    author_email = "carlos.miguel.silva@protonmail.com",
    name = "Tasker",
    description = "Run pipelines on your own computer for better automation",
    version = "0.0.1",
    packages = [ "Tasker" ],
    entry_points = {
        "console_scripts": [
            "tasker = Tasker.__main__:main"
        ]
    },
    install_requires = [

    ]
)