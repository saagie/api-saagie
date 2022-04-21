gql_list_global_env_vars = """
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

gql_create_env_var = """
mutation saveEnvironmentVariableMutation($id: UUID, $projectId: UUID, $name: String!, $scope: EnvVarScope!, 
                                         $value: String, $description: String, $isPassword: Boolean!)  {
            saveEnvironmentVariable(
                entityId: $projectId
                environmentVariable: {
                    id: $id
                    name: $name
                    scope: $scope
                    value: $value
                    description: $description
                    isPassword:$isPassword

    }){
        id
    }
}
"""

gql_update_env_var = """
mutation($id: UUID, $projectId: UUID, $name: String!, $scope: EnvVarScope!, $value: String, $description: String, 
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

    }){
        id
    }}
"""

gql_delete_env_var = """
mutation deleteEnvironmentVariableMutation($id: UUID!) {
    deleteEnvironmentVariable (id: $id)
}
"""

gql_list_project_env_vars = """
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