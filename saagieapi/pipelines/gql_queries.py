# pylint: disable=duplicate-code
GQL_LIST_PIPELINES_FOR_PROJECT_MINIMAL = """
query projectPipelinesQuery($projectId: UUID!) {
    project(id: $projectId){
        pipelines{
            id
            name
            alias
        }
    }
}
"""

GQL_LIST_PIPELINES_FOR_PROJECT = """
query projectPipelinesQuery($projectId: UUID!, 
							$instancesLimit: Int, 
                            $versionsLimit: Int, 
                            $versionsOnlyCurrent: Boolean) {
    project(id: $projectId){
        pipelines{
            id
            name
            alias
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
                runWithExecutionVariables
                initialExecutionVariables{
                    key
                    value
                    isPassword
                }
                jobsInstance{
                    id
                    jobId
                    number
                    startTime
                    endTime
                }
                conditionsInstance{
                    id
                    conditionNodeId
                    isSuccess
                    startTime
                    endTime
                }
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
                sourceUrl
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
query graphPipelineQuery($id: UUID!, 
						 $instancesLimit: Int, 
                         $versionsLimit: Int, 
                         $versionsOnlyCurrent: Boolean) {
    graphPipeline(id: $id){
        id
        name
        alias
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
            runWithExecutionVariables
            initialExecutionVariables{
                key
                value
                isPassword
            }
            jobsInstance{
                id
                jobId
                number
                startTime
                endTime
            }
            conditionsInstance{
                id
                conditionNodeId
                isSuccess
                startTime
                endTime
            }
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
                    condition {
                        toString
                    }
                }
            }
            creationDate
            creator
            isCurrent
            isMajor
            sourceUrl
        }
        creationDate
        creator
        isScheduled
        cronScheduling
        scheduleStatus
        scheduleTimezone
        isLegacyPipeline
        hasExecutionVariablesEnabled
    }
}
"""

GQL_GET_PIPELINE_BY_NAME = """
query graphPipelineByNameQuery(
    $projectId: UUID!, 
    $pipelineName: String!,
    $instancesLimit: Int, 
    $versionsLimit: Int, 
    $versionsOnlyCurrent: Boolean
) {
    graphPipelineByName(projectId: $projectId, name: $pipelineName) {
        id
        name
        alias
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
            runWithExecutionVariables
            initialExecutionVariables{
                key
                value
                isPassword
            }
            jobsInstance{
                id
                jobId
                number
                startTime
                endTime
            }
            conditionsInstance{
                id
                conditionNodeId
                isSuccess
                startTime
                endTime
            }
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
                    condition {
                        toString
                    }
                }
            }
            creationDate
            creator
            isCurrent
            isMajor
            sourceUrl
        }
        creationDate
        creator
        isScheduled
        cronScheduling
        scheduleStatus
        scheduleTimezone
        isLegacyPipeline
        hasExecutionVariablesEnabled
    }
}
"""

GQL_GET_PIPELINE_BY_ALIAS = """
query graphPipelineByAliasQuery(
    $projectId: UUID!, 
    $pipelineAlias: String!,
    $instancesLimit: Int, 
    $versionsLimit: Int, 
    $versionsOnlyCurrent: Boolean
) {
    graphPipelineByAlias(projectId: $projectId, alias: $pipelineAlias) {
        id
        name
        alias
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
            runWithExecutionVariables
            initialExecutionVariables{
                key
                value
                isPassword
            }
            jobsInstance{
                id
                jobId
                number
                startTime
                endTime
            }
            conditionsInstance{
                id
                conditionNodeId
                isSuccess
                startTime
                endTime
            }
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
                    condition {
                        toString
                    }
                }
            }
            creationDate
            creator
            isCurrent
            isMajor
            sourceUrl
        }
        creationDate
        creator
        isScheduled
        cronScheduling
        scheduleStatus
        scheduleTimezone
        isLegacyPipeline
        hasExecutionVariablesEnabled
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
mutation($id: UUID!, 
		 $name: String, 
		 $description: String, 
		 $alerting: JobPipelineAlertingInput,
		 $isScheduled: Boolean, 
		 $cronScheduling: Cron, 
		 $scheduleTimezone:TimeZone, 
		 $hasExecutionVariablesEnabled: Boolean,
         $alias: String)    {
    editPipeline(pipeline: 
        {
            id: $id
            name: $name
            description: $description
            alerting:    $alerting
            isScheduled: $isScheduled
            cronScheduling: $cronScheduling
            scheduleTimezone: $scheduleTimezone
            hasExecutionVariablesEnabled: $hasExecutionVariablesEnabled
            alias: $alias
        }
    ){
        id
        name
        alias
        description
        alerting{
            emails
            statusList
        }
        isScheduled
        cronScheduling
        scheduleTimezone
        hasExecutionVariablesEnabled
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
        runWithExecutionVariables
        initialExecutionVariables{
            key
            value
            isPassword
        }
        jobsInstance{
            id
            jobId
            number
            startTime
            endTime
        }
        conditionsInstance{
            id
            conditionNodeId
            isSuccess
            startTime
            endTime
        }
    }
}
"""

GQL_CREATE_GRAPH_PIPELINE = """
mutation createGraphPipelineMutation($name: String!, 
									 $description: String, 
                                     $projectId: UUID!,
									 $releaseNote: String, 
                                     $alerting: JobPipelineAlertingInput,
                                     $isScheduled: Boolean!, 
                                     $cronScheduling: Cron, 
                                     $scheduleTimezone:TimeZone,
                                     $jobNodes: [JobNodeInput!], 
                                     $conditionNodes: [ConditionNodeInput!],
                                     $alias: String!,
                                     $sourceUrl: String) {
    createGraphPipeline(
        pipeline: {
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
            alias: $alias
            sourceUrl: $sourceUrl
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
mutation($id: UUID!, 
		 $jobNodes: [JobNodeInput!], 
         $conditionNodes: [ConditionNodeInput!], 
         $releaseNote: String,
         $sourceUrl: String){
    addGraphPipelineVersion(
        pipelineId: $id,
        graph: {
            jobNodes: $jobNodes,
            conditionNodes: $conditionNodes
        },
        releaseNote: $releaseNote,
        sourceUrl: $sourceUrl
    ){
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

GQL_ROLLBACK_PIPELINE_VERSION = """
mutation rollbackPipelineVersionMutation($pipelineId: UUID!, $versionNumber: Int!) {
    rollbackPipelineVersion(pipelineId: $pipelineId, versionNumber: $versionNumber) {
        id
        versions {
            number
            isCurrent
        }
    }
}
"""

GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_STATUS = """
query countDeletablePipelineInstancesByStatus($pipelineId: UUID!){
    countDeletablePipelineInstancesByStatus(pipelineId: $pipelineId){
        selector
        count
    }
}
"""

GQL_COUNT_DELETABLE_PIPELINE_INSTANCE_BY_DATE = """
query countDeletablePipelineInstancesByDate($pipelineId: UUID!, $beforeAt: DateTime!) {
  countDeletablePipelineInstancesByDate(
    pipelineId: $pipelineId
    beforeAt: $beforeAt
  )
}
"""

GQL_DELETE_PIPELINE_VERSION = """
mutation deletePipelineVersions($pipelineId: UUID!, $versions: [Int!]!){
    deletePipelineVersions(pipelineId: $pipelineId, pipelineVersionNumbers: $versions){
        number,
        success
    }
}
"""

GQL_DELETE_PIPELINE_INSTANCE = """
mutation deletePipelineInstances($pipelineId: UUID!, $pipelineInstancesId: [UUID!]){
    deletePipelineInstances(pipelineId: $pipelineId, pipelineInstanceIds: $pipelineInstancesId){
        id,
        success
    }
}
"""

GQL_DELETE_PIPELINE_INSTANCE_BY_SELECTOR = """
mutation deletePipelineInstancesByStatusSelector(
    $pipelineId: UUID!, 
    $selector: PipelineInstanceStatusSelector!, 
    $excludePipelineInstanceId: [UUID!], $includePipelineInstanceId: [UUID!]) 
{
    deletePipelineInstancesByStatusSelector(
        pipelineId: $pipelineId
        selector: $selector
        excludePipelineInstanceIds: $excludePipelineInstanceId
        includePipelineInstanceIds: $includePipelineInstanceId
    )
}
"""

GQL_DELETE_PIPELINE_INSTANCE_BY_DATE = """
mutation deletePipelineInstancesByDateSelector($pipelineId: UUID!, $beforeAt: DateTime!, $excludePipelineInstanceId: [UUID!], $includePipelineInstanceId: [UUID!]) {
    deletePipelineInstancesByDateSelector(
        pipelineId: $pipelineId
        beforeAt: $beforeAt
        excludePipelineInstanceIds: $excludePipelineInstanceId
        includePipelineInstanceIds: $includePipelineInstanceId
    )
}
"""

GQL_DUPLICATE_PIPELINE = """
mutation duplicatePipeline($pipelineId: UUID!, $duplicateJobs: Boolean) {
    duplicatePipeline(originalPipelineId: $pipelineId, duplicateJobs: $duplicateJobs) {
        id
        name
    }
}
"""
