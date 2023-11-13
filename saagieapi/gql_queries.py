# pylint: disable=duplicate-code
#   ____ _           _
#  / ___| |_   _ ___| |_ ___ _ __
# | |   | | | | / __| __/ _ \ '__|
# | |___| | |_| \__ \ ||  __/ |
#  \____|_|\__,_|___/\__\___|_|


GQL_GET_CLUSTER_INFO = """
{
    getClusterCapacity {
        cpu
        gpu
        memory
    }
}
"""

#        _       _    __
#  _ __ | | __ _| |_ / _| ___  _ __ _ __ ___
# | '_ \| |/ _` | __| |_ / _ \| '__| '_ ` _ \
# | |_) | | (_| | |_|  _| (_) | |  | | | | | |
# | .__/|_|\__,_|\__|_|  \___/|_|  |_| |_| |_|
# |_|

GQL_GET_PLATFORM_INFO = """
{
    platform{
        id
        name
        counts{
            projects
            jobs
            apps
            pipelines
        }
    }
}
"""


#                                 _  _                 _
#  _ __   ___  _ __    ___   ___ (_)| |_   ___   _ __ (_)  ___  ___
# | '__| / _ \| '_ \  / _ \ / __|| || __| / _ \ | '__|| | / _ \/ __|
# | |   |  __/| |_) || (_) |\__ \| || |_ | (_) || |   | ||  __/\__ \
# |_|    \___|| .__/  \___/ |___/|_| \__| \___/ |_|   |_| \___||___/
#             |_|


GQL_GET_REPOSITORIES_INFO = """
{
    repositories {
        id
        name
        technologies {
            id
            label
            available
            __typename
        }
    }
}
"""

GQL_GET_RUNTIMES = """
query technologyQuery($id: UUID!){
    technology(id: $id){ 
        __typename 
        ... on JobTechnology {
            contexts{
                id 
                label 
                available
            }
        }
        ... on SparkTechnology {
            contexts{
                id
                label
                available
            }
        }
        ... on AppTechnology{
            id
            label
            available
            appContexts{
                id
                available
                deprecationDate
                description
                dockerInfo {
                    image
                    version
                }
                facets
                label
                lastUpdate
                ports {
                    basePath
                    name
                    port
                    rewriteUrl
                    scope
                }
                missingFacets
                recommended
                trustLevel
                volumes{
                    path
                    size
                }
            }
        }
    }
}"""

#                      _ _ _   _
#   ___ ___  _ __   __| (_) |_(_) ___  _ __  ___
#  / __/ _ \| '_ \ / _` | | __| |/ _ \| '_ \/ __|
# | (_| (_) | | | | (_| | | |_| | (_) | | | \__ \
#  \___\___/|_| |_|\__,_|_|\__|_|\___/|_| |_|___/
#
GQL_CHECK_CUSTOM_EXPRESSION = """
query evaluateConditionExpression(  $projectId: UUID!, 
                                    $expression: String!, 
                                    $variables: [ConditionExpressionVariableInput!]) {
    evaluateConditionExpression (
        projectId: $projectId, 
        expression: $expression,
        variables: $variables
    )
}
"""

GQL_COUNT_CONDITION_LOGS = """
query conditionPipelineCountFilteredLogs($conditionInstanceId: UUID!,
                                        $projectID: UUID!,
                                        $streams: [LogStream]!) {
    conditionPipelineCountFilteredLogs (
        conditionInstanceID: $conditionInstanceId, 
        projectID: $projectID, 
        streams: $streams
    )
}
"""

GQL_GET_CONDITION_LOGS_BY_CONDITION = """
query conditionPipelineByNodeIdFilteredLogs($pipelineInstanceID: UUID!, 
                                            $conditionNodeID: UUID!, 
                                            $projectID: UUID!, 
                                            $streams: [LogStream]!) {
    conditionPipelineByNodeIdFilteredLogs(
        pipelineInstanceID: $pipelineInstanceID,
        conditionNodeID: $conditionNodeID,
        projectID: $projectID,
        streams: $streams
    ) {
        count
        content {
            index
            value
            stream
        }
    }
}
"""

GQL_GET_CONDITION_LOGS_BY_INSTANCE = """
query conditionPipelineFilteredLogs($conditionInstanceId: UUID!, 
                                    $projectId: UUID!, 
                                    $limit: Int, 
                                    $skip: Int, 
                                    $streams: [LogStream]!) {
    conditionPipelineFilteredLogs(
        conditionInstanceID: $conditionInstanceId, 
        projectID:$projectId, 
        limit: $limit, 
        skip: $skip, 
        streams: $streams
    ) {
        count
        content {
            index
            value
            stream
        }
    }
}
"""
