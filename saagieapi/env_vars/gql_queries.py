# pylint: disable=duplicate-code
GQL_LIST_GLOBAL_ENV_VARS = """
{
    globalEnvironmentVariables{
        id,
        name,
        scope,
        value,
        description,
        isPassword
    }
}
"""

GQL_CREATE_ENV_VAR = """
mutation saveEnvironmentVariableMutation($id: UUID, 
                                         $projectId: UUID, 
                                         $name: String!, 
                                         $scope: EnvVarScope!, 
                                         $value: String, 
                                         $description: String, 
                                         $isPassword: Boolean!)  {
    saveEnvironmentVariable(
        entityId: $projectId
        environmentVariable: {
            id: $id
            name: $name
            scope: $scope
            value: $value
            description: $description
            isPassword:$isPassword
        }
    ){
        id
    }
}
"""

GQL_UPDATE_ENV_VAR = """
mutation($id: UUID, 
         $projectId: UUID, 
         $name: String!, 
         $scope: EnvVarScope!, 
         $value: String, 
         $description: String, 
         $isPassword: Boolean!)  {
    saveEnvironmentVariable(
        entityId: $projectId
        environmentVariable: {
            id: $id
            name: $name
            scope: $scope
            value: $value
            description: $description
            isPassword:$isPassword
        }
    ){
        id
    }
}
"""

GQL_DELETE_ENV_VAR = """
mutation deleteEnvironmentVariableMutation($id: UUID!) {
    deleteEnvironmentVariable (id: $id)
}
"""

GQL_LIST_PROJECT_ENV_VARS = """
query technologyQuery($projectId: UUID!){
    projectEnvironmentVariables(projectId: $projectId){
        id
        name
        scope
        value
        description
        isPassword
    }
}
"""

GQL_LIST_PIPELINE_ENV_VARS = """
query pipelineEnvironmentVariablesQuery($pipelineId: UUID!, 
                                        $scopeFilter: EnvVarScope) {  
    pipelineEnvironmentVariables(pipelineId: $pipelineId, 
                                 scope: $scopeFilter
    ) {    
        id
        scope
        name
        value
        description
        isPassword
        overriddenValues {
            id
            scope
            value
            description
            isPassword
        }
    }
}
"""

GQL_CREATE_PIPELINE_ENV_VAR = """
mutation replaceEnvironmentVariablesByRawForScope($entityId: UUID, 
                                                  $scope: EnvVarScope!, 
                                                  $rawEnvironmentVariables: String!) {  
    replaceEnvironmentVariablesByRawForScope(
        entityId: $entityId, 
        scope: $scope, 
        rawEnvironmentVariables: 
        $rawEnvironmentVariables
    ) {    
        id
        scope
        name
        value
    }
}
"""
