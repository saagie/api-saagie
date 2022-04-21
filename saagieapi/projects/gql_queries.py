gql_list_projects = """
  {
       projects{
          id,
          name,
          creator,
          description,
          jobsCount,
          status
      }
  }
  """

gql_get_project_info = """
query projectQuery($id: UUID!) {
    project(id: $id){
        name
        creator
        description
        jobsCount
        status
    }
}
  """

gql_get_project_technologies = """
query projectQuery($id: UUID!) {
    project(id: $id){
        technologiesByCategory{
            jobCategory
            technologies{
                id
            }
        }
    }
}
"""

gql_create_project = """
mutation createProjectMutation($name: String!, $description: String, $technologies: [TechnologyInput!],
                                $appTechnologies: [TechnologyInput!], $authorizedGroups: [SecurityGroupInput]) {
  createProject(project: {
                    name: $name
                    description: $description
                    authorizedGroups:  $authorizedGroups
                    technologiesByCategory: [
                      {
                        jobCategory: "Extraction",
                        technologies: $technologies
                      },
                      {
                        jobCategory: "Processing",
                        technologies: $technologies
                      }
                    ]
                    appTechnologies: $appTechnologies
                }) {
    id
    name
    creator
  }
}
"""

group_block_template = """
authorizedGroups: [
                      {{
                        name: "{0}",
                        role: {1}
                      }}
                    ]
"""

gql_delete_project = """
mutation deleteProjectMutation($projectId: UUID!){
    deleteProject(projectId: $projectId)
}
"""
