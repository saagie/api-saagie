#   ___  _ __  __   __ __   __  __ _  _ __  ___
#  / _ \| '_ \ \ \ / / \ \ / / / _` || '__|/ __|
# |  __/| | | | \ V /   \ V / | (_| || |   \__ \
#  \___||_| |_|  \_/     \_/   \__,_||_|   |___/

gql_get_global_env_vars = """
  {
    globalEnvironmentVariables{
      id,
      name,
      scope,
      value,
      description,
      isPassword
    }
  }
  """

gql_create_global_env_var = """
  mutation {{
    saveEnvironmentVariable (
      environmentVariable: {{
        name: "{0}"
        value: "{1}"
        description: "{2}"
        isPassword: {3}
        scope: GLOBAL
      }}
    ) {{
      id
    }}
  }}
"""

gql_delete_env_var = """
  mutation {{
    deleteEnvironmentVariable (
      id: "{0}"
    )
  }}
"""

gql_get_project_env_vars = """
  {{
    projectEnvironmentVariables(projectId: "{0}"){{
      id,
      name,
      scope,
      value,
      description,
      isPassword
    }}
  }}
  """

gql_create_project_env_var = """
  mutation {{
    saveEnvironmentVariable (
      entityId: "{0}"
      environmentVariable: {{
        name: "{1}"
        value: "{2}"
        description: "{3}"
        isPassword: {4}
        scope: PROJECT
      }}
    ) {{
      id
    }}
  }}
"""


#   ____ _           _
#  / ___| |_   _ ___| |_ ___ _ __
# | |   | | | | / __| __/ _ \ '__|
# | |___| | |_| \__ \ ||  __/ |
#  \____|_|\__,_|___/\__\___|_|


gql_get_cluster_info = """
{
  getClusterCapacity {
    cpu
    gpu
    memory
  }
}
"""


#                                 _  _                 _
#  _ __   ___  _ __    ___   ___ (_)| |_   ___   _ __ (_)  ___  ___
# | '__| / _ \| '_ \  / _ \ / __|| || __| / _ \ | '__|| | / _ \/ __|
# | |   |  __/| |_) || (_) |\__ \| || |_ | (_) || |   | ||  __/\__ \
# |_|    \___|| .__/  \___/ |___/|_| \__| \___/ |_|   |_| \___||___/
#             |_|


gql_get_repositories_info = """
  {
    repositories {
      id
      name
      technologies {
        id
        label
        __typename
      }
    }
  }
"""

#                        _              _
#  _ __   _ __   ___    (_)  ___   ___ | |_  ___
# | '_ \ | '__| / _ \   | | / _ \ / __|| __|/ __|
# | |_) || |   | (_) |  | ||  __/| (__ | |_ \__ \
# | .__/ |_|    \___/  _/ | \___| \___| \__||___/
# |_|                 |__/


gql_get_projects_info = """
  {
       projects{
          id,
          name,
          creator,
          description,
          jobsCount,
          status
      }
  }
  """

gql_get_project_info = """
  {{
       project(id: "{0}"){{
          name,
          creator,
          description,
          jobsCount,
          status
      }}
  }}
  """

gql_get_project_technologies = """
{{
   technologiesByCategory(projectId: "{0}"){{
      jobCategory,
      technologies{{
        id
        }}
   }}
}} 
"""

gql_create_project = """
mutation {{
  createProject(project: {{
                    name: "{0}",
                    description: "{1}",
                    {2}
                    technologiesByCategory: [
                      {{
                        jobCategory: "Extraction",
                        technologies: [
                          {3}
                        ]
                      }},
                      {{
                        jobCategory: "Processing",
                        technologies: [
                          {3}
                        ]
                      }}
                    ]
                }}) {{
    id
    name
    creator
  }}
}}
"""

group_block_template = """
authorizedGroups: [
                      {{
                        name: "{0}",
                        role: {1}
                      }}
                    ]
"""

gql_delete_project = """
mutation {{
  archiveProject(
    projectId: "{0}"
  )
}}
"""

#    _         _
#   (_)  ___  | |__   ___
#   | | / _ \ | '_ \ / __|
#   | || (_) || |_) |\__ \
#  _/ | \___/ |_.__/ |___/
# |__/


gql_get_project_jobs = """
  {{
    jobs(projectId: "{0}"){{
      id,
      name,
      description,
      alerting{{
        emails,
        loginEmails{{
          login,
          email
        }},
        statusList
      }},
      countJobInstance,
      instances{1}{{
        id,
        status,
        startTime,
        endTime
      }},
      versions {{
        releaseNote
        runtimeVersion
        commandLine
        isMajor
      }},
      category,
      technology {{
        id
      }},
      isScheduled,
      cronScheduling,
      scheduleStatus,
      isStreaming,
      creationDate,
      migrationStatus,
      migrationProjectId,
      isDeletable,
      pipelines {{
        id
      }}
    }}
  }}
  """

gql_get_project_job = """
  {{
    job(id: "{0}"){{
      id,
      name,
      description,
      alerting{{
        emails,
        loginEmails{{
          login,
          email
        }},
        statusList
      }},
      countJobInstance,
      instances{{
        id,
        status,
        startTime,
        endTime
      }},
      versions {{
        releaseNote
        runtimeVersion
        commandLine
        isMajor
      }},
      category,
      technology {{
        id
      }},
      isScheduled,
      cronScheduling,
      scheduleStatus,
      isStreaming,
      creationDate,
      migrationStatus,
      migrationProjectId,
      isDeletable,
      pipelines {{
        id
      }}
    }}
  }}
  """

gql_get_job_instance = """
  query{{
    jobInstance(id: "{0}"){{
      id,
      status,
      version {{
        releaseNote
        runtimeVersion
        commandLine
        isMajor
        doesUseGPU
      }}
    }}
  }}
  """

gql_run_job = """
  mutation{{
    runJob(jobId: "{0}"){{
      id,
      status
    }}
  }}
  """

gql_stop_job_instance = """
  mutation{{
    stopJobInstance(jobInstanceId: "{0}"){{
      id,
      number,
      status,
      startTime,
      endTime,
      jobId
    }}
  }}
  """

gql_edit_job = """
  mutation{{
    editJob(job: {{
      id: "{0}"
      {1}
    }}
    ) {{
        id,
        name,
        description,
        isScheduled,
        cronScheduling,
        scheduleTimezone
        resources{{
        cpu {{
            request,
            limit}},
        memory{{
            request,
            limit}}
        }}
      }}
  }}
"""

gql_create_job = """{{"operationName": "createJobMutation",\
                   "variables": {{\
                       "job": {{\
                           "projectId": "{1}",\
                           "name": "{0}",\
                           "description": "{2}",\
                           "category": "{3}",\
                           "technology": {{"id":"{4}"}},\
                           "isStreaming": false,\
                           {9}, \
                           "resources": {10}, \
                           "doesUseGPU": false\
                       }},\
                       "jobVersion": {{\
                           "runtimeVersion": "{5}",\
                           "commandLine": "{6}",\
                           {8}\
                           "dockerInfo": null,\
                           "releaseNote": "{7}"\
                       }},\
                       "file":null\
                   }},\
                   "query": "mutation createJobMutation($job: JobInput!, $jobVersion: JobVersionInput!, $file: Upload) \
                   {{\\n  createJob(job: $job, jobVersion: $jobVersion, file: $file) \
                   {{\\n    id\\n    versions {{\\n      number\\n      __typename\\n    }}\\n   \
                    __typename\\n  }}\\n}}\\n"}}"""

gql_extra_technology = '"extraTechnology": {{\
                           "language": "{0}",\
                           "version": "{1}"\
                       }},'

gql_delete_job = """
  mutation {{
    archiveJob(
      jobId: "{0}"
    )
  }}
"""

#   __ _  _ __   _ __   ___
#  / _` || '_ \ | '_ \ / __|
# | (_| || |_) || |_) |\__ \
#  \__,_|| .__/ | .__/ |___/
#        |_|    |_|


gql_get_project_web_apps = """
  {{
    labWebApps(projectId: "{0}"){{
      id,
      name,
      description,
      countJobInstance,
      instances{1}{{
        id,
        status,
        startTime,
        endTime
      }},
      versions {{
        releaseNote
        runtimeVersion
        commandLine
        isMajor
      }},
      category,
      technology {{
        id
      }},
      isScheduled,
      cronScheduling,
      scheduleStatus,
      isStreaming,
      creationDate,
      migrationStatus,
      migrationProjectId,
      isDeletable,
      pipelines {{
        id
      }}
    }}
  }}
  """

get_project_web_app = """
  {{
    labWebApp(id: "{0}"){{
      id,
      name,
      description,
      countJobInstance,
      instances{{
        id,
        status,
        startTime,
        endTime
      }},
      versions {{
        releaseNote
        runtimeVersion
        commandLine
        isMajor
      }},
      category,
      technology {{
        id
      }},
      isScheduled,
      cronScheduling,
      scheduleStatus,
      isStreaming,
      creationDate,
      migrationStatus,
      migrationProjectId,
      isDeletable,
      pipelines {{
        id
      }}
    }}
  }}
  """

gql_get_project_app = """
  {{
    app(id: "{0}"){{
      id,
      name,
      description,
      creationDate,
      creator,
      versions{{
        number,
        creationDate,
        dockerInfo{{
          image,
          dockerCredentialsId
        }}
      }}
    }}
  }}
  """

#         _               _  _
#  _ __  (_) _ __    ___ | |(_) _ __    ___  ___
# | '_ \ | || '_ \  / _ \| || || '_ \  / _ \/ __|
# | |_) || || |_) ||  __/| || || | | ||  __/\__ \
# | .__/ |_|| .__/  \___||_||_||_| |_| \___||___/
# |_|       |_|

gql_get_pipelines = """
  query{{
    pipelines(projectId: "{0}"){{
      id,
      name,
      description,
      alerting{{
        emails,
        loginEmails{{
          login,
          email
        }},
        statusList
      }},
      pipelineInstanceCount,
      instances{1}{{
        id,
        status,
        startTime,
        endTime
      }},
      creationDate,
      creator,
      isScheduled,
      cronScheduling,
      scheduleStatus
    }}
  }}
  """

gql_get_pipeline = """
  query{{
    pipeline(id: "{0}"){{
      id,
      name,
      description,
      alerting{{
        emails,
        loginEmails{{
          login,
          email
        }},
        statusList
      }},
      pipelineInstanceCount,
      creationDate,
      creator,
      isScheduled,
      cronScheduling,
      scheduleStatus
    }}
  }}
  """

gql_stop_pipeline_instance = """
  mutation{{
    stopPipelineInstance(pipelineInstanceId: "{0}"){{
      id,
      number,
      status,
      startTime,
      endTime,
      pipelineId
    }}
  }}
  """

gql_edit_pipeline = """
  mutation{{
    editPipeline(pipeline: {0}) {{
        id,
        name,
        description,
        isScheduled,
        cronScheduling
      }}
  }}
"""

gql_run_pipeline = """
  mutation{{
    runPipeline(pipelineId: "{0}"){{
      id,
      status
    }}
  }}
"""

gql_create_pipeline = """
  mutation {{
      createPipeline(pipeline: {{
          name: "{0}",
          description: "{1}",
          projectId: "{2}",
          jobsId: {3},
          isScheduled: false
      }}){{id}}
  }}
"""

gql_get_pipeline_instance = """
  query {{
      pipelineInstance(id: "{0}"){{
          id,
          status,
          startTime,
          endTime
      }}
  }}
"""
