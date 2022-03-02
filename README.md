<p align="center"><img width=100% src="https://github.com/saagie/api-saagie/blob/master/.github/banner.png"></p>

[![PyPI version](https://img.shields.io/pypi/v/saagieapi?style=for-the-badge)](https://pypi.org/project/saagieapi/)
![PyPI version](https://img.shields.io/pypi/pyversions/saagieapi?style=for-the-badge)

[![GitHub release date](https://img.shields.io/github/release-date/saagie/api-saagie?style=for-the-badge&color=blue)][releases]

[![Contributors](https://img.shields.io/github/contributors/saagie/api-saagie?style=for-the-badge&color=black)][contributors]
![License](https://img.shields.io/pypi/l/saagieapi?style=for-the-badge&color=black)

[releases]: https://github.com/saagie/api-saagie/releases

[contributors]: https://github.com/saagie/api-saagie/graphs/contributors

- [Presentation](#presentation)
- [Installation](#installation)
- [Usage](#usage)
    * [Projects](#projects)
- [Contributing](#contributing)

## Presentation

The `saagieapi` python package implements python API wrappers to easily interact with the Saagie platform in python.

There are two subpackages that each give access to a main class whose methods allows to interact with the API :

* The `manager` subpackage implements the `SaagieApiManager` class whose methods can interact with the `manager`
  interface in Saagie (Saagie legacy)
* The `projects` subpackage implements the `SaagieApi` class whose methods can interact with the `Projects` interface in
  Saagie (current main interface)

## Installing

```bash
pip install saagieapi==<version>
```

### Compatibility with your Saagie platform

| **Saagie platform version** | **saagie-api release** |
|-----------------------------|------------------------|
| < 2.2.0                     | < 0.6.0                |
| >= 2.2.0                    | >= 0.6.0               |

## Usage

### Projects

```python
from saagieapi.projects import SaagieApi

saagie = SaagieApi(url_saagie="<url>",
                   id_platform="1",
                   user="<saagie-user-name>",
                   password="<saagie-user-password>",
                   realm="saagie")

# Create a project named 'Project_test' on the saagie platform
project_dict = saagie.create_project(name="Project_test",
                                     group="<saagie-group-with-proper-permissions>",
                                     role='Manager',
                                     description='A test project')

# Save the project id
project_id = project_dict['createProject']['id']

# Create a python job named 'Python test job' inside this project
job_dict = saagie.create_job(job_name="Python test job",
                             project_id=project_id,
                             file='<path-to-local-file>',
                             description='Amazing python job',
                             category='Processing',
                             technology_catalog='Saagie',
                             technology='python',
                             runtime_version='3.6',
                             command_line='python {file} arg1 arg2',
                             release_note='',
                             extra_technology=''
                             )

# Save the job id
job_id = job_dict['data']['createJob']['id']

# Run the python job and wait for its completion
saagie.run_job_callback(job_id=job_id, freq=10, timeout=-1)

```

### Connecting to your platform

There are 2 options to connect to your platform :  

1. using the default constructor : 
```python
saagie = SaagieApi(url_saagie="<url>",
                   id_platform="1",
                   user="<saagie-user-name>",
                   password="<saagie-user-password>",
                   realm="saagie")
 ```


2. Using the `easy_connect` alternative constructor which uses the complete URL (eg: 
        https://mysaagie-workspace.prod.saagie.com/projects/platform/6/) and will 
        parse it in order to retrieve the platform URL, platform id and the 
        realm.
```python
saagie = SaagieApi.easy_connect(url_saagie_platform="<url>",
                   user="<saagie-user-name>",
                   password="<saagie-user-password>")
```

#### Finding your platform, project, job and instances ids

Your Saagie projects homepage has the following structure `https://<REALM>-workspace.me.saagie.com/projects/platform/<PLATFORM_ID>/`

> `https://mysaagie-workspace.me.saagie.com/projects/platform/1/`
>would give  : 
> - `platform_id` = 1
> - `realm` = mysaagie 

**Project id** can be found in the project URL after the `/project` 

> `https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/jobs`
> would give  : 
> - `project_id` = 8321e13c-892a-4481-8552-5be4b6cc5df4


**Job id** can be found in the project URL after the `/job` 

> `https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b`
> would give  : 
> - `job_id` = a85ac3db-bca1-4f15-b8f7-44731fba874b

**App id** can be found in the project URL after the `/app` 

> `https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/app/02c01d47-8a29-47d0-a53c-235add43c885`
> would give  : 
> - `app_id` = 02c01d47-8a29-47d0-a53c-235add43c885

**Pipeline id** can be found in the project URL after the `/pipeline` 

> `https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/pipeline/4da29f25-e7c9-4410-869e-40b9ba0074d1`
> would give  : 
> - `pipeline_id` = 4da29f25-e7c9-4410-869e-40b9ba0074d1

**Job instance id** can be found in the project URL after the `/instances` 

> `https://mysaagie-workspace.me.saagie.com/projects/platform/1/project/8321e13c-892a-4481-8552-5be4b6cc5df4/job/a85ac3db-bca1-4f15-b8f7-44731fba874b/instances/6ff448ae-3770-4639-b0f8-079e5c614ab6`
> would give  : 
> - `job_instance_id` = 6ff448ae-3770-4639-b0f8-079e5c614ab6

## Contributing

All contributions are made with the pull-request system. Please follow the following steps:

- Create an issue with the correct label (i.e. Documentation/Bug/Feature)
- Create a new branch starting with the issue type : `feat/...`, `fix/...` or `doc/...`. GitHub Action (CI) will be
  triggered on each push on your branch. Warning, after the first push on your branch, an automatic commit/push will be
  made by the CI in order to increment the version. Thus, remember to update your repository after your first commit.
- Implement your change
- Open a Pull Request (don't forget to link the PR to the issue)
- PR will be reviewed by the Professional Service Team and merged if all the checks are successful

### Commits Guidelines

We're using the [Python Semantic Release library](https://python-semantic-release.readthedocs.io/en/latest/) to manage
our versioning.

In order to work properly, you need to follow
the  [Emoji Parser commit style](https://python-semantic-release.readthedocs.io/en/latest/configuration.html#major-emoji)
when squashing the commits during the merge of the PR to master.

- Messages with :ambulance:, :lock:, :bug:, :zap:, :goal_net:, :alien:, :wheelchair:, :speech_balloon:, :mag:, :apple:
  , :penguin:, :checkered_flag:, :robot:, :green_apple: emojis in the commit will make the release process to bump the
  patch version
- Messages with :sparkles:, :children_crossing:, :lipstick:, :iphone:, :egg:, :chart_with_upwards_trend: emojis in the
  commit will make the release process to bump the minor version
- Messages with a :boom: emoji in the commit will make the release process to bump the major version
