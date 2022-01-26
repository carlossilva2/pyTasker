from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author = "Carlos Silva",
    author_email = "carlos.miguel.silva@protonmail.com",
    name = "pyTasker",
    description = "Run pipelines on your own computer for better automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version = "0.1.0",
    url="https://gitlab.com/carlossilva2/tasker",
    packages = find_packages(),
    license="MIT",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
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
    }
)