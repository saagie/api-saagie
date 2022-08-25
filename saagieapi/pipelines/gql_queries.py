# pylint: disable=duplicate-code
GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL = """
query projectPipelinesQuery($projectId: UUID!) {
    project(id: $projectId){
        pipelines{
            id
            name
        }
    }
}
  """

GQL_LIST_PIPELINES_FOR_PROJECT = """
query projectPipelinesQuery($projectId: UUID!, $instancesLimit: Int, $versionsLimit: Int, $versionsOnlyCurrent: Boolean) {
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
            versions(limit: $versionsLimit, onlyCurrent: $versionsOnlyCurrent) {
                number
                releaseNote
                graph{
                    jobNodes{
                        id
                        job{
                            id
                            name
                        }
                        position{
                            x
                            y
                        }
                        nextNodes
                    }
                    conditionNodes{
                        id
                        position{
                            x
                            y
                        }
                        nextNodesSuccess
                        nextNodesFailure
                    }
                }
                creationDate
                creator
                isCurrent
                isMajor
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

GQL_GET_PIPELINE = """
query graphPipelineQuery($id: UUID!, $instancesLimit: Int, $versionsLimit: Int, $versionsOnlyCurrent: Boolean) {
    graphPipeline(id: $id){
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
        versions(limit: $versionsLimit, onlyCurrent: $versionsOnlyCurrent) {
            number
            releaseNote
            graph{
                jobNodes{
                    id
                    job{
                        id
                        name
                    }
                    position{
                        x
                        y
                    }
                    nextNodes
                }
                conditionNodes{
                    id
                    position{
                        x
                        y
                    }
                    nextNodesSuccess
                    nextNodesFailure
                }
            }
            creationDate
            creator
            isCurrent
            isMajor
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
  """

GQL_STOP_PIPELINE_INSTANCE = """
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

GQL_EDIT_PIPELINE = """
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

GQL_RUN_PIPELINE = """
mutation runPipelineMutation($pipelineId: UUID!){
    runPipeline(pipelineId: $pipelineId){
      id
      status
    }
  }
"""

GQL_GET_PIPELINE_INSTANCE = """
query pipelineInstanceQuery($id: UUID!){
    pipelineInstance(id: $id){
          id
          status
          startTime
          endTime
    }
}
"""

GQL_CREATE_GRAPH_PIPELINE = """
mutation createGraphPipelineMutation($name: String!, $description: String, $projectId: UUID!,
                                     $releaseNote: String, $alerting: JobPipelineAlertingInput,
                                     $isScheduled: Boolean!, $cronScheduling: Cron, $scheduleTimezone:TimeZone,
                                     $jobNodes: [JobNodeInput!], $conditionNodes: [ConditionNodeInput!]) {
  createGraphPipeline(pipeline:  {
    name: $name
    description: $description
    projectId: $projectId
    releaseNote : $releaseNote
    alerting: $alerting
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

GQL_DELETE_PIPELINE = """
mutation deletePipelineMutation($id: UUID!){
  deletePipeline (
    id: $id
  )
}
"""

GQL_UPGRADE_PIPELINE = """
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
