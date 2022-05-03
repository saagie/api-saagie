# pylint: disable=duplicate-code
GQL_LIST_PROJECTS = """
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

GQL_GET_PROJECT_INFO = """
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

GQL_GET_PROJECT_JOBS_TECHNOLOGIES = """
query projectQuery($id: UUID!) {
    project(id: $id){
        technologiesByCategory{
            jobCategory
            technologies{
                id
                __typename
            }
        }
    }
}
"""

GQL_GET_PROJECT_APPS_TECHNOLOGIES = """
query appTechnologiesQuery($id: UUID!) {
    project(id: $id){
        appTechnologies{
                id
        }
    }
}
"""

GQL_CREATE_PROJECT = """
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


GQL_DELETE_PROJECT = """
mutation deleteProjectMutation($projectId: UUID!){
    deleteProject(projectId: $projectId)
}
"""
