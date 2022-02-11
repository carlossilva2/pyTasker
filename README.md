# Tasker

<a href="https://github.com/carlossilva2/pyTasker/blob/main/LICENSE" target="blank"><img src="https://img.shields.io/github/license/carlossilva2/pytasker?style=round-square&color=green" alt="pyTasker License" /></a>
[![Downloads](https://pepy.tech/badge/pytasker/month)](https://pepy.tech/project/pytasker)
[![Supported Versions](https://img.shields.io/pypi/pyversions/pytasker.svg)](https://pypi.org/project/pytasker)
<a href="https://www.buymeacoffee.com/cmsilva" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="23" width="100" style="border-radius:5px" />

You know [Ansible](https://github.com/ansible/ansible) right? Well, this works kind of the same way, except you create tasks to automate your local computer.

How? You're in luck. Just create an InstructionSet (you can use the CLI command `tasker create` to get started) and let your life get easier!


## Index

- [Tasker](#tasker)
  - [Index](#index)
  - [Installation](#installation)
  - [Reference System](#reference-system)
  - [Key Features](#key-features)
    - [Copy Action](#copy-action)
    - [Zip Action](#zip-action)
    - [Delete Action](#delete-action)
    - [Move Action](#move-action)
    - [Input Action](#input-action)
    - [Echo Action](#echo-action)
    - [Request Action](#request-action)
  - [Usage](#usage)
  - [Roadmap](#roadmap)
    - [Actions in Pipeline](#actions-in-pipeline)
    - [General Improvements](#general-improvements)
  - [Support](#support)

## Installation

There are 2 ways of installation:

  1. Via source files available at [GitHub](https://github.com/carlossilva2/pyTasker).
  2. Using Pip

```console
$ pip install pyTasker
```

## Reference System

Tasker includes a reference system which allows the user to access values from a previous step and/or value, like the [Input Action](#input-action). References are a way to simplify the InstructionSets.

To get started with references simply use `$<Step Number>` or `$<Step Number>.<Field Name>` on a field. If no additional data is appended to the reference, like `$0`, the system will fallback to the key where reference was invoked.

Example:

```json
{
    "name": "<Step Name>",
    "step": 0,
    "operation": "input",
    "question": "<Question Value>"
},
{
    "name": "<Step Name>",
    "step": 1,
    "operation": "zip",
    "target": "*",
    "rename": "$0.value",
    "!deflate": true,
    "!destination": "<Destination Path>",
    "subfolders": true
}
```

## Key Features

For extra information use `tasker help`

### Copy Action

```json
{
    "name": "<Name of Step>",
    "step": 0,
    "operation": "copy",
    "target": "<File(s) or File Type>",
    "origin": "<Location Path>",
    "destination": "<Location End Path>",
    "subfolders": false //Should Tasker also include subfolders inside main location
}
```

### Zip Action

```json
{
    "name": "<Name of Step>",
    "step": 0,
    "operation": "zip",
    "target": "<Location Path>",
    "rename": "<Name of Zip file>",
    "!destination": "<Name of Zip file>",
    "!deflate": false, //When Zip is created should the Folder structure be with current system Path or just the pretended folder
    "subfolders": true //Should Tasker also include subfolders inside main location
}
```

### Delete Action

**Warning: This permanently deletes the file(s) from computer**

```json
{
    "name": "<Name of Step>",
    "step": 0,
    "operation": "delete",
    "target": "<File(s) or File Type>" //Can use location + file name/type
}
```

### Move Action

```json
{
    "name": "<Name of Step>",
    "step": 0,
    "operation": "move",
    "origin": "<File(s) or File Type>", //Can use location + file name/type
    "destinaton": "<File(s) or File Type>", //Can use location + file name/type
    "target": "<File(s) or File Type>" //Can use location + file name/type
}
```

### Input Action

> This action stores the Answer in the `value` variable

```json
{
    "name": "<Name of Step>",
    "step": 0,
    "operation": "input",
    "question": "<Question to prompt the user>"
}
```

### Echo Action

```json
{
    "name": "<Name of Step>",
    "step": 0,
    "operation": "input",
    "value": "<Value to output to console>"
}
```

### Request Action

> This action stores the Response in the `response` variable

```json
{
    "name": "<Name of Step>",
    "step": 0,
    "operation": "request",
    "endpoint": "<URL to query>",
    "method": "<get | post | put | delete>", //Must be only 1 option
    "!body": {}, //Optional parameter
    "!headers": {} //Optional Parameter
}
```

---

> `Step` parameter is the order Tasker will pick up the tasks

> Parameters starting with "!" are optional parameters

## Usage

![Copy Action](https://raw.githubusercontent.com/carlossilva2/pyTasker/main/static/Copy%20PDFs.png)
![Complex Action](https://raw.githubusercontent.com/carlossilva2/pyTasker/main/static/Copy%20PDFs%20then%20zip.png)

## Roadmap

This is a project I'm working on my free time, however I have some new Actions in mind I want to implement.

### Actions in Pipeline

- ~~Input Action~~
- Command Action
- Encrypt Action
- Registry Action (for Windows)

### General Improvements

- Change reference system

## Support

[![Buy me a Coffee](https://cdn.buymeacoffee.com/buttons/default-orange.png)](https://www.buymeacoffee.com/cmsilva)