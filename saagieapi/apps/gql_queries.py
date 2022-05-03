# pylint: disable=duplicate-code
GQL_LIST_APPS_FOR_PROJECT = """
query labWebAppQuery($id: UUID!){
    labWebApps(projectId: $id){ 
      id
      name
      description
      countJobInstance
      versions {
        number
        creationDate
        releaseNote
        runtimeVersion
        commandLine
        isMajor
        isCurrent
        dockerInfo{
            image
            dockerCredentialsId
        }
        exposedPorts{
            name
            port
            isRewriteUrl
            basePathVariableName
            isAuthenticationRequired
        }
        storagePaths
      }
      category,
      technology {
        id
      }
      alerting {
        emails
        statusList
    }
      creationDate
      isDeletable
      graphPipelines {
        id
      }
      storageSizeInMB
      doesUseGPU
      resources{
        cpu{
          limit
          request
        }
        memory{
          limit
          request
        }
        gpu{
          limit
          request
        }
      }
    }
}
"""

GQL_GET_APP_INFO = """
query labWebAppQuery($id: UUID!){
    labWebApp(id: $id){ 
      id
      name
      description
      countJobInstance
      versions {
        number
        creationDate
        releaseNote
        runtimeVersion
        commandLine
        isMajor
        isCurrent
        dockerInfo{
            image
            dockerCredentialsId
        }
        exposedPorts{
            name
            port
            isRewriteUrl
            basePathVariableName
            isAuthenticationRequired
        }
        storagePaths
      }
      category,
      technology {
        id
      }
      alerting {
        emails
        statusList
    }
      creationDate
      isDeletable
      graphPipelines {
        id
      }
      storageSizeInMB
      doesUseGPU
      resources{
        cpu{
          limit
          request
        }
        memory{
          limit
          request
        }
        gpu{
          limit
          request
        }
      }
    }
  }
  """

GQL_CREATE_APP = """
mutation createJobMutation($projectId: UUID!, $name: String!, $description: String, $technologyId: UUID!, 
                           $storageSizeInMB: Int,
                           $image: String!, $dockerCredentialsId: UUID, $exposedPorts: [ExposedPortInput!],
                           $storagePaths: [String!],
                           $releaseNote: String, $alerting: JobPipelineAlertingInput) {
    createJob(job: {
            projectId: $projectId
            name: $name
            description: $description
            category: ""
            technology: {
                id: $technologyId
            }
            isStreaming: false
            isScheduled: false
            storageSizeInMB: $storageSizeInMB
            alerting: $alerting
        }
        jobVersion: {
            dockerInfo: {
                image: $image
                dockerCredentialsId: $dockerCredentialsId
            }
            exposedPorts: $exposedPorts
            storagePaths: $storagePaths 
            releaseNote: $releaseNote
        }){
        id
        versions {
            number
            __typename
        }
        __typename
    }}
"""

GQL_EDIT_APP = """
mutation editJobMutation($id: UUID!, $name: String, $description: String, $alerting: JobPipelineAlertingInput) {
    editJob(job: {
        id: $id
        name: $name
        description: $description
        alerting: $alerting
    }){
        id
        name
        description
        creationDate
        technology{
            id
        }
        alerting{
            emails
            statusList
        }
    }
}
"""
GQL_DELETE_APP = """
mutation deleteJobMutation($appId: UUID!){
    deleteJob(jobId: $appId)
}
"""

GQL_STOP_APP_INSTANCE = """
  mutation stopJobInstanceMutation($appInstanceId: UUID!){
    stopJobInstance(jobInstanceId: $appInstanceId){
      id
      number
      status
      startTime
      endTime
      jobId
    }
  }
  """


GQL_RUN_APP = """
  mutation runJobMutation($appId: UUID!){
    runJob(jobId: $appId){
      id
      status
    }
  }
  """
