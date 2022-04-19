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
  {{
       project(id: "{0}"){{
          name,
          creator,
          description,
          jobsCount,
          status
      }}
  }}
  """

gql_get_project_technologies = """
{{
   project(id: "{0}"){{
   technologiesByCategory {{
      jobCategory,
      technologies{{
        id
        }}
      }}
   }}
}} 
"""

gql_create_project = """
mutation {{
  createProject(project: {{
                    name: "{0}",
                    description: "{1}",
                    {2}
                    technologiesByCategory: [
                      {{
                        jobCategory: "Extraction",
                        technologies: [
                          {3}
                        ]
                      }},
                      {{
                        jobCategory: "Processing",
                        technologies: [
                          {3}
                        ]
                      }}
                    ]
                }}) {{
    id
    name
    creator
  }}
}}
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
mutation {{
  archiveProject(
    projectId: "{0}"
  )
}}
"""
