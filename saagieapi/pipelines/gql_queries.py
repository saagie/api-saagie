gql_list_pipelines_for_project_light = """
  query{{
    project(id: "{0}"){{
      pipelines{{
        id,
        name
  }}}}
  """


gql_list_pipelines_for_project = """
  query{{
    project(id: "{0}"){{
      pipelines{{
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
        scheduleStatus,
        scheduleTimezone,
        isLegacyPipeline
      }}
  }}}}
  """

gql_get_pipeline = """
  query{{
    graphPipeline(id: "{0}"){{
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
      scheduleStatus,
      scheduleTimezone,
      isLegacyPipeline
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

gql_create_graph_pipeline = """
  mutation($jobNodes: [JobNodeInput!], $conditionNodes: [ConditionNodeInput!]) {{
  createGraphPipeline(pipeline:  {{
    name: "{0}",
    description: "{1}",
    projectId: "{2}",
    releaseNote : "{3}",
    {4}
    graph: {{jobNodes: $jobNodes,
                conditionNodes: $conditionNodes}}
    }}
  ) {{
    id
  }}
}}
"""

gql_delete_pipeline = """
  mutation {{
  deletePipeline (
    id: "{0}"
  )
}}
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
