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
        isValid
        invalidReasons{
            type
            concernedProperty
            message
        }
    }
}
"""

GQL_CREATE_ENV_VAR = """
mutation saveEnvironmentVariableMutation($entityId: UUID, 
                                         $envVar: EnvironmentVariableInput!) {
    saveEnvironmentVariable(
        entityId: $entityId
        environmentVariable: $envVar
    ){
        id
    }
}
"""

GQL_UPDATE_ENV_VAR = """
mutation updateEnvironmentVariableMutation($entityId: UUID, 
                                           $envVar: EnvironmentVariableInput!) {
    saveEnvironmentVariable(
        entityId: $entityId
        environmentVariable: $envVar
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
        isValid
        overriddenValues {
            id
            scope
            value
            description
            isPassword
        }
        invalidReasons{
            type
            concernedProperty
            message
        }
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
        isValid
        overriddenValues {
            id
            scope
            value
            description
            isPassword
        }
        invalidReasons{
            type
            concernedProperty
            message
        }
    }
}
"""

GQL_LIST_APP_ENV_VARS = """
query appEnvironmentVariablesQuery($appId: UUID!, 
                                   $scopeFilter: EnvVarScope) {  
    appEnvironmentVariables(appId: $appId, 
                            scope: $scopeFilter
    ) {    
        id
        scope
        name
        value
        description
        isPassword
        isValid
        overriddenValues {
            id
            scope
            value
            description
            isPassword
        }
        invalidReasons{
            type
            concernedProperty
            message
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
