from gql import gql

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

gql_get_project_jobs = """
        {{
          jobs(projectId: "{0}"){{
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
              id,
              label
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
                      id,
                      label
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

gql_get_project_web_apps = """
        {{
          labWebApps(projectId: "{0}"){{
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
              id,
              label
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
                      id,
                      label
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

gql_get_project_apps = """
        {{
          apps(projectId: "{0}"){{
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
              }},
              isCurrent
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
                      }},
                      isCurrent
                    }}
                  }}
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

gql_run_job = """
        mutation{{
          runJob(jobId: "{0}"){{
            id,
            status
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

gql_get_pipelines = """
query{{
  pipelines(projectId: "{0}"){{
    id,
    name,
    creator,
    description,
    alerting{{
      emails
    }},
    creationDate,
    pipelineInstanceCount
  }}
}}
"""

gql_get_pipeline = """
query{{
  pipeline(id: "{0}"){{
    id,
    name,
    creator,
    description,
    alerting{{
      emails
    }},
    creationDate,
    pipelineInstanceCount
  }}
}}
"""