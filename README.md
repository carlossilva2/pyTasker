# Tasker

You know [Ansible](https://github.com/ansible/ansible) right? Well, this works kind of the same way, except you create tasks to automate your local computer.

How? You're in luck. Just create an InstructionSet (you can use the CLI command `tasker create` to get started) and let your life get easier!

## Installation

There are 2 ways of installation:

  1. Via source files available at Gitlab.
  2. Using Pip

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
    "target": "<File(s) or File Type>" //Can use location + file name/type
}
```

> Step parameter is the order Tasker will pick up the tasks

> Parameters starting with "!" are optional parameters

## Usage

![Copy Action](static/Copy%20PDFs.png "Copy Action")
Example of a Copy InstructionSet

## Roadmap

This is a project I'm working on my free time, however I have some new Actions in mind I want to implement.
