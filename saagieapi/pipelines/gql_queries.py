gql_list_pipelines_for_project_minimal = """
query projectPipelinesQuery($projectId: UUID!) {
    project(id: $projectId){
        pipelines{
            id
            name
        }
    }
}
  """


gql_list_pipelines_for_project = """
query projectPipelinesQuery($projectId: UUID!, $instancesLimit: Int) {
    project(id: $projectId){
        pipelines{
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
            pipelineInstanceCount
            instances(limit: $instancesLimit){
              id
              status
              startTime
              endTime
            }
            creationDate
            creator
            isScheduled
            cronScheduling
            scheduleStatus
            scheduleTimezone
            isLegacyPipeline
          }
    }
}
  """

gql_get_pipeline = """
query graphPipelineQuery($id: UUID!) {
    graphPipeline(id: $id){
        id
        name
        description,
        alerting{
            emails
            loginEmails{
                login
                email
            }
            statusList
        }
        pipelineInstanceCount
        creationDate
        creator
        isScheduled
        cronScheduling
        scheduleStatus
        scheduleTimezone
        isLegacyPipeline
    }
}
  """

gql_stop_pipeline_instance = """
mutation stopPipelineInstanceMutation($pipelineInstanceId: UUID!){
    stopPipelineInstance(pipelineInstanceId: $pipelineInstanceId){
      id
      number
      status
      startTime
      endTime
      pipelineId
    }
}
  """

gql_edit_pipeline = """
  mutation($id: UUID!, $name: String, $description: String, $alerting: JobPipelineAlertingInput,
          $isScheduled: Boolean, $cronScheduling: Cron, $scheduleTimezone:TimeZone)  {
    editPipeline(pipeline: {
        id: $id
        name: $name
        description: $description
        alerting:  $alerting
        isScheduled: $isScheduled
        cronScheduling: $cronScheduling
        scheduleTimezone: $scheduleTimezone
      })
    {
      id
      name
      description
      alerting{
        emails
        statusList
      }
      isScheduled
      cronScheduling
      scheduleTimezone
    }
  }
"""

gql_run_pipeline = """
mutation runPipelineMutation($pipelineId: UUID!){
    runPipeline(pipelineId: $pipelineId){
      id
      status
    }
  }
"""

gql_create_pipeline = """
mutation createPipelineMutation($name: String!, $description: String, $projectId: UUID!, $jobsId: [UUID!]!){
    createPipeline(pipeline: {
                                name: $name
                                description: $description
                                projectId: $projectId
                                jobsId: $jobsId
                                isScheduled: false
        }){
        id
    }
}
"""

gql_get_pipeline_instance = """
query pipelineInstanceQuery($id: UUID!){
    pipelineInstance(id: $id){
          id
          status
          startTime
          endTime
    }
}
"""

gql_create_graph_pipeline = """
mutation createGraphPipelineMutation($name: String!, $description: String, $projectId: UUID!, 
                                     $releaseNote: String, 
                                     $isScheduled: Boolean!, $cronScheduling: Cron, $scheduleTimezone:TimeZone,
                                     $jobNodes: [JobNodeInput!], $conditionNodes: [ConditionNodeInput!]) {
  createGraphPipeline(pipeline:  {
    name: $name
    description: $description
    projectId: $projectId
    releaseNote : $releaseNote
    isScheduled: $isScheduled
    cronScheduling: $cronScheduling
    scheduleTimezone: $scheduleTimezone
    graph: {
        jobNodes: $jobNodes
        conditionNodes: $conditionNodes
    }
  }
  ) {
    id
  }
}
"""

gql_delete_pipeline = """
mutation deletePipelineMutation($id: UUID!){
  deletePipeline (
    id: $id
  )
}
"""

gql_upgrade_pipeline = """
  mutation($id: UUID!, $jobNodes: [JobNodeInput!], $conditionNodes: [ConditionNodeInput!], $releaseNote: String){
  addGraphPipelineVersion(
    pipelineId: $id,
    graph: {jobNodes: $jobNodes,
                conditionNodes: $conditionNodes},
    releaseNote: $releaseNote
    )
    {
      number,
      releaseNote,
      graph{
        jobNodes {
          id,
          job {
            id
          }
        },
        conditionNodes{
          id
        }
      },
      creationDate,
      creator,
      isCurrent,
      isMajor
    }
  }
"""
