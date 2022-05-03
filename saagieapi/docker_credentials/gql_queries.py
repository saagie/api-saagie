# pylint: disable=duplicate-code
GQL_CREATE_DOCKER_CREDENTIALS = """
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

GQL_UPGRADE_DOCKER_CREDENTIALS = """
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

GQL_DELETE_DOCKER_CREDENTIALS = """
mutation deleteDockerCredentialsMutation($id: UUID!, $projectId: UUID!) {
    deleteDockerCredentials(
        id: $id
        projectId: $projectId)
}
"""

GQL_GET_ALL_DOCKER_CREDENTIALS = """
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

GQL_GET_DOCKER_CREDENTIALS = """
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
