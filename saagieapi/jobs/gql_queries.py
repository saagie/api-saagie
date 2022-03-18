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
mutation editJobMutation($id: UUID!, $name: String, $description: String, 
                         $isScheduled: Boolean!, $cronScheduling: Cron, $scheduleTimezone: TimeZone,
                         $alerting: JobPipelineAlertingInput, $resources: JobResourceInput) {
    editJob(job: {
        id: $id
        name: $name
        description: $description
        isScheduled: $isScheduled
        cronScheduling: $cronScheduling
        scheduleTimezone: $scheduleTimezone
        alerting: $alerting
        resources: $resources
    }){
        id
        name
        description
        isScheduled
        cronScheduling
        scheduleTimezone
        resources{
            cpu {
                request
                limit}
            memory{
                request
                limit}
        }
        alerting{
            emails
            statusList
        }
    }
}
"""

gql_create_job = """
mutation createJobMutation($projectId: UUID!, $name: String!, $description: String, $category: String!,
                           $isScheduled: Boolean!, $cronScheduling: Cron, $scheduleTimezone: TimeZone
                           $technologyId: UUID!, 
                           $alerting: JobPipelineAlertingInput, $resources: JobResourceInput,
                           $releaseNote: String, $runtimeVersion: String, $commandLine: String,
                           $dockerInfo: JobDockerInput, $file: Upload) {{
    createJob(job: {{
            projectId: $projectId
            name: $name
            description: $description
            category: $category
            technology: {{
                id: $technologyId
            }}
            isStreaming: false
            isScheduled: $isScheduled
            cronScheduling: $cronScheduling
            scheduleTimezone: $scheduleTimezone
            alerting: $alerting
            resources: $resources
            doesUseGPU: false
        }} 
        jobVersion: {{
            releaseNote: $releaseNote
            runtimeVersion: $runtimeVersion
            commandLine: $commandLine
            {extra_technology}
            dockerInfo: $dockerInfo
        }}
        file: $file){{
        id
        versions {{
            number
            __typename
        }}
        __typename
    }}
}}
"""

gql_upgrade_job = """
mutation addJobVersionMutation($jobId: UUID!, $releaseNote: String, $runtimeVersion: String, $commandLine: String,
                               $usePreviousArtifact: Boolean, $dockerInfo: JobDockerInput, $file: Upload) {{
    addJobVersion(
        jobId: $jobId
        jobVersion: {{
            releaseNote: $releaseNote
            runtimeVersion: $runtimeVersion
            commandLine: $commandLine
            {extra_technology}
            dockerInfo: $dockerInfo
            usePreviousArtifact: $usePreviousArtifact
        }}
        file: $file){{
            number
            __typename
    }}
}}
"""

gql_get_info_job = """query {{
  job(id:"{0}"){{
    id,
    name,
    description,
    creationDate,
    isScheduled,
    cronScheduling,
    scheduleStatus,
    scheduleTimezone,
    isStreaming,
    isDeletable,
    graphPipelines(isCurrent: true){{
      id
    }},
    category,
    technology{{
      id
    }},
    alerting{{
      emails,
      statusList,
      loginEmails{{
        email
      }}
    }},
    resources{{
      cpu{{
        request,
        limit
      }}
      memory{{
        request,
        limit
      }}
    }}
  }}
}}
"""

gql_extra_technology = """
    extraTechnology: {{
        language: "{0}"
        version: "{1}"
    }}"""

gql_delete_job = """
  mutation {{
    archiveJob(
      jobId: "{0}"
    )
  }}
"""
