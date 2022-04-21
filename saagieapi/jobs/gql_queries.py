gql_list_jobs_for_project_minimal = """
query jobsQuery($projectId: UUID!){
    jobs(projectId: $projectId){
        id
        name
    }
}
"""

gql_list_jobs_for_project = """
query jobsQuery($projectId: UUID!, $category: String, $technologyId: UUID, $instancesLimit: Int){
    jobs(projectId: $projectId, category: $category, technologyId: $technologyId){
        id
        name
        description
        alerting{
        emails
        loginEmails{
          login
          email
        }
        statusList
        }
        countJobInstance
        instances(limit: $instancesLimit){
            id
            status
            startTime
            endTime
        }
        versions {
            releaseNote
            runtimeVersion
            commandLine
            isMajor
        }
        category
        technology {
            id
        }
        isScheduled
        cronScheduling
        scheduleTimezone
        scheduleStatus
        isStreaming
        creationDate
        migrationStatus
        migrationProjectId
        isDeletable
        pipelines {
            id
        }
        graphPipelines{
            id
        }
        resources{
            cpu {
                request
                limit
            }
            memory{
                request
                limit
            }
        }
    }
}
  """

gql_get_job_instance = """
query jobInstanceQuery($jobInstanceId: UUID!){
    jobInstance(id: $jobInstanceId){
      id
      status
      version {
        releaseNote
        runtimeVersion
        commandLine
        isMajor
        doesUseGPU
      }
    }
  }
  """

gql_run_job = """
  mutation runJobMutation($jobId: UUID!){
    runJob(jobId: $jobId){
      id
      status
    }
  }
  """

gql_stop_job_instance = """
  mutation stopJobInstanceMutation($jobInstanceId: UUID!){
    stopJobInstance(jobInstanceId: $jobInstanceId){
      id
      number
      status
      startTime
      endTime
      jobId
    }
  }
  """

gql_edit_job = """
mutation editJobMutation($jobId: UUID!, $name: String, $description: String, 
                         $isScheduled: Boolean!, $cronScheduling: Cron, $scheduleTimezone: TimeZone,
                         $alerting: JobPipelineAlertingInput, $resources: JobResourceInput) {
    editJob(job: {
        id: $jobId
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
                           $technologyId: UUID!, $extraTechnology: ExtraTechnologyInput,
                           $alerting: JobPipelineAlertingInput, $resources: JobResourceInput,
                           $releaseNote: String, $runtimeVersion: String, $commandLine: String,
                           $dockerInfo: JobDockerInput, $file: Upload) {
    createJob(job: {
            projectId: $projectId
            name: $name
            description: $description
            category: $category
            technology: {
                id: $technologyId
            }
            isStreaming: false
            isScheduled: $isScheduled
            cronScheduling: $cronScheduling
            scheduleTimezone: $scheduleTimezone
            alerting: $alerting
            resources: $resources
            doesUseGPU: false
        }
        jobVersion: {
            releaseNote: $releaseNote
            runtimeVersion: $runtimeVersion
            commandLine: $commandLine
            extraTechnology: $extraTechnology
            dockerInfo: $dockerInfo
        }
        file: $file){
        id
        versions {
            number
            __typename
        }
        __typename
    }
}
"""

gql_upgrade_job = """
mutation addJobVersionMutation($jobId: UUID!, $releaseNote: String, $runtimeVersion: String, $commandLine: String,
                               $extraTechnology: ExtraTechnologyInput,
                               $usePreviousArtifact: Boolean, $dockerInfo: JobDockerInput, $file: Upload) {
    addJobVersion(
        jobId: $jobId
        jobVersion: {
            releaseNote: $releaseNote
            runtimeVersion: $runtimeVersion
            commandLine: $commandLine
            extraTechnology: $extraTechnology
            dockerInfo: $dockerInfo
            usePreviousArtifact: $usePreviousArtifact
        }
        file: $file){
            number
            __typename
    }
}
"""

gql_get_job_info = """
query jobInfoQuery($jobId: UUID!){
    job(id: $jobId){
        id
        name
        description
        alerting{
            emails
            loginEmails{
              login
              email
            }
            statusList
        }
        countJobInstance
        versions {
            releaseNote
            runtimeVersion
            commandLine
            isMajor
        }
        category
        technology {
            id
        }
        isScheduled
        cronScheduling
        scheduleStatus
        scheduleTimezone
        isStreaming
        creationDate
        migrationStatus
        migrationProjectId
        isDeletable
        graphPipelines(isCurrent: true){
            id
        }
        resources{
            cpu {
                request
                limit
            }
            memory{
                request
                limit
            }
        }
        
    }
}
"""

gql_delete_job = """
mutation deleteJobMutation($jobId: UUID!){
    deleteJob(jobId: $jobId)
}
"""
