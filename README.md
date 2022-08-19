![Saagie api logo](https://github.com/saagie/api-saagie/blob/master/.github/banner.png?raw=true)

[![PyPI version](https://img.shields.io/pypi/v/saagieapi?style=for-the-badge)](https://pypi.org/project/saagieapi/)
![PyPI version](https://img.shields.io/pypi/pyversions/saagieapi?style=for-the-badge)

[![GitHub release date](https://img.shields.io/github/release-date/saagie/api-saagie?style=for-the-badge&color=blue)][releases]

[![Contributors](https://img.shields.io/github/contributors/saagie/api-saagie?style=for-the-badge&color=black)][contributors]
![License](https://img.shields.io/pypi/l/saagieapi?style=for-the-badge&color=black)

[releases]: https://github.com/saagie/api-saagie/releases

[contributors]: https://github.com/saagie/api-saagie/graphs/contributors

- [Presentation](#presentation)
- [Installation](#installing)
- [Usage](#usage)
- [Contributing](#contributing)

## Presentation

The `saagieapi` python package implements python API wrappers to easily interact with the Saagie platform in python.

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

All the implemented features are documented in the [Wiki](https://github.com/saagie/api-saagie/wiki)

Here's a full example of how to use the API:

```python
from saagieapi import SaagieApi

saagie = SaagieApi(url_saagie="<url>",
                   id_platform="1",
                   user="<saagie-user-name>",
                   password="<saagie-user-password>",
                   realm="saagie")

# Create a project named 'Project_test' on the saagie platform
project_dict = saagie.projects.create(name="Project_test",
                                     group="<saagie-group-with-proper-permissions>",
                                     role='Manager',
                                     description='A test project')

# Save the project id
project_id = project_dict['createProject']['id']

# Create a python job named 'Python test job' inside this project
job_dict = saagie.jobs.create(job_name="Python test job",
                              project_id=project_id,
                              file='<path-to-local-file>',
                              description='Amazing python job',
                              category='Processing',
                              technology_catalog='Saagie',
                              technology='python',
                              runtime_version='3.8',
                              command_line='python {file} arg1 arg2',
                              release_note='',
                              extra_technology='')

# Save the job id
job_id = job_dict['data']['createJob']['id']

# Run the python job and wait for its completion
saagie.jobs.run_with_callback(job_id=job_id, freq=10, timeout=-1)

```

### Connecting to your platform

There are 2 options to connect to your platform :

1. using the default constructor:

    ```python
    from saagieapi import *
    saagie = SaagieApi(url_saagie="<url>",
                       id_platform="1",
                       user="<saagie-user-name>",
                       password="<saagie-user-password>",
                       realm="saagie")
    ```

2. Using the `easy_connect` alternative constructor which uses the complete URL (eg:
    <https://mysaagie-workspace.prod.saagie.com/projects/platform/6/>) and will
    parse it in order to retrieve the platform URL, platform id and the realm.

    ```python
    from saagieapi import *
    saagie = SaagieApi.easy_connect(url_saagie_platform="<url>",
                    user="<saagie-user-name>",
                    password="<saagie-user-password>")
    ```

If you want to know how to find the correct values for the URL, platform id and the realm,
please refer to the [Wiki](https://github.com/saagie/api-saagie/wiki#connecting-to-your-platform).

## Contributing

The complete guide to contribute is available here:
[Contributing](https://github.com/saagie/api-saagie/blob/master/CONTRIBUTING.md)


## :warning: Warning :warning:
This library is provided on an experimental basis and is not covered by Saagie support for the moment.
