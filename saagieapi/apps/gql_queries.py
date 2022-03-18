gql_get_project_apps = """
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

gql_get_project_app = """
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

gql_create_app = """
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

gql_edit_app = """
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
