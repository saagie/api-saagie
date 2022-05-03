# pylint: disable=duplicate-code
GQL_LIST_JOBS_FOR_PROJECT_MINIMAL = """
query jobsQuery($projectId: UUID!){
    jobs(projectId: $projectId){
        id
        name
    }
}
"""

GQL_LIST_JOBS_FOR_PROJECT = """
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

GQL_GET_JOB_INSTANCE = """
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

GQL_RUN_JOB = """
  mutation runJobMutation($jobId: UUID!){
    runJob(jobId: $jobId){
      id
      status
    }
  }
  """

GQL_STOP_JOB_INSTANCE = """
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

GQL_EDIT_JOB = """
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

GQL_CREATE_JOB = """
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

GQL_UPGRADE_JOB = """
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

GQL_GET_JOB_INFO = """
query jobInfoQuery($jobId: UUID!, $instancesLimit: Int){
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
        instances(limit: $instancesLimit){
            id
            status
            startTime
            endTime
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

GQL_DELETE_JOB = """
mutation deleteJobMutation($jobId: UUID!){
    deleteJob(jobId: $jobId)
}
"""
