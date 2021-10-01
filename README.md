# Saagie API wrapper in Python

[![GitHub release](https://img.shields.io/github/release/saagie/api-saagie?style=for-the-badge)][releases] 
[![GitHub release date](https://img.shields.io/github/release-date/saagie/api-saagie?style=for-the-badge&color=blue)][releases]  
![License](https://img.shields.io/pypi/l/saagieapi?style=for-the-badge&color=black)
[![Contributors](https://img.shields.io/github/contributors/saagie/api-saagie?style=for-the-badge&color=black)][contributors]

[releases]: https://github.com/saagie/api-saagie/releases
[contributors]: https://github.com/saagie/api-saagie/graphs/contributors

- [Presentation](#presentation)
- [Installation](#installation)
- [Examples](#examples)
  * [Projects](#projects)
- [Notes](#notes)

## Presentation
The `saagieapi` python package implements python API wrappers to easily interract with the Saagie platform in python.

There are two subpackages that each give access to a main class whose methods allows to interract with the API :
* The `manager` subpackage implements the `SaagieApiManager` class whose methods can interract with the `manager` interface in Saagie (Saagie leagacy)
* The `projects` subpackage implements the `SaagieApi` class whose methods can interract with the `Projects` interface in Saagie (current main interface)

## Installation
Via pip :

```bash
pip install git+http://git@github.com/saagie/api-saagie.git
```


## Examples

### Projects

```python
from saagieapi.projects import SaagieApi

saagie = SaagieApi(url_saagie="https://saagie-workspace.prod.saagie.io",
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
                             technology='python',
                             runtime_version='3.6',
                             command_line='python {file} arg1 arg2',
                             release_note='',
                             extra_technology='',
                             extra_technology_vers='')

# Save the job id
job_id = job_dict['data']['createJob']['id']

# Run the python job and wait for its completion
saagie.run_job_callback(job_id=job_id, freq=10, timeout=-1)

```

## CONTRIBUTING

All contributions are made with the pull-request system.
Please follow the following steps:

- Create an issue with the correct label (i.e. Documentation/Bug/Feature)
- Create a new branch starting with the issue type : `feature/...`, `bug/...` or `documentation/...`. GitHub Action (CI) will be triggered on each push on your branch. Warning, after the first push on your branch, an automatic commit/push will be made by the CI in order to increment the version. Thus, remember to update your repository after your first commit.
- Implement your change
- Open a Pull Request that uses our template (don't forget to link the PR to the issue)
- PR will be reviewed by the Professional Service Team and merged if all the checks are successful

### Commits Guidelines

We're using the [Python Semantic Release library](https://python-semantic-release.readthedocs.io/en/latest/) to manage our versioning. 
In order to work properly, you need to follow the [Angular commit style](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits) when squashing the commits during the merge of the PR to master.  