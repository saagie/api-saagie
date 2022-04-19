#   ____ _           _
#  / ___| |_   _ ___| |_ ___ _ __
# | |   | | | | / __| __/ _ \ '__|
# | |___| | |_| \__ \ ||  __/ |
#  \____|_|\__,_|___/\__\___|_|


gql_get_cluster_info = """
{
  getClusterCapacity {
    cpu
    gpu
    memory
  }
}
"""

#                                 _  _                 _
#  _ __   ___  _ __    ___   ___ (_)| |_   ___   _ __ (_)  ___  ___
# | '__| / _ \| '_ \  / _ \ / __|| || __| / _ \ | '__|| | / _ \/ __|
# | |   |  __/| |_) || (_) |\__ \| || |_ | (_) || |   | ||  __/\__ \
# |_|    \___|| .__/  \___/ |___/|_| \__| \___/ |_|   |_| \___||___/
#             |_|


gql_get_repositories_info = """
  {
    repositories {
      id
      name
      technologies {
        id
        label
        __typename
      }
    }
  }
"""

gql_get_runtimes = """
query technologyQuery($id: UUID!){
    technology(id: $id){ 
        __typename 
        ... on JobTechnology {contexts{label}}
        ... on SparkTechnology {contexts{label}}
        ... on AppTechnology{
            id
            label
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
