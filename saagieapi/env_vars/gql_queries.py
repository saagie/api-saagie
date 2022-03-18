gql_get_global_env_vars = """
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

gql_create_global_env_var = """
  mutation {{
    saveEnvironmentVariable (
      environmentVariable: {{
        name: "{0}"
        value: "{1}"
        description: "{2}"
        isPassword: {3}
        scope: GLOBAL
      }}
    ) {{
      id
    }}
  }}
"""

gql_delete_env_var = """
  mutation {{
    deleteEnvironmentVariable (
      id: "{0}"
    )
  }}
"""

gql_get_project_env_vars = """
  {{
    projectEnvironmentVariables(projectId: "{0}"){{
      id,
      name,
      scope,
      value,
      description,
      isPassword
    }}
  }}
  """

gql_create_project_env_var = """
  mutation {{
    saveEnvironmentVariable (
      entityId: "{0}"
      environmentVariable: {{
        name: "{1}"
        value: "{2}"
        description: "{3}"
        isPassword: {4}
        scope: PROJECT
      }}
    ) {{
      id
    }}
  }}
"""
