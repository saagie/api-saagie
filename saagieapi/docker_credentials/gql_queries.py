gql_create_docker_credentials = """
mutation createDockerCredentialsMutation($registry: String, $username: String!, $password: String!, $projectId: UUID!) {
    createDockerCredentials(
        dockerCredentials: {
            registry: $registry
            username: $username
            password: $password 
            projectId: $projectId}){
        id
        registry
        username
        lastUpdate
    }
}
"""

gql_upgrade_docker_credentials = """
mutation updateDockerCredentialsMutation($id: UUID!, $registry: String, 
                    $username: String, $password: String!, $projectId: UUID!) {
    updateDockerCredentials(
        dockerCredentialsUpdate: {
            id: $id
            registry: $registry
            username: $username
            password: $password 
            projectId: $projectId}){
        id
        registry
        username
        lastUpdate
    }
}
"""

gql_delete_docker_credentials = """
mutation deleteDockerCredentialsMutation($id: UUID!, $projectId: UUID!) {
    deleteDockerCredentials(
        id: $id
        projectId: $projectId)
}
"""

gql_get_all_docker_credentials = """
query allDockerCredentialsQuery($projectId: UUID!) {
    allDockerCredentials(projectId: $projectId){
        id
        registry
        username
        lastUpdate
        jobs{
            id
        }
    }
}
"""

gql_get_docker_credentials = """
query dockerCredentialsQuery($id: UUID!, $projectId: UUID!) {
    dockerCredentials(id: $id, projectId: $projectId){
        id
        registry
        username
        lastUpdate
        jobs{
            id
        }
    }
}
"""
