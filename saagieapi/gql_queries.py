# pylint: disable=duplicate-code
#   ____ _           _
#  / ___| |_   _ ___| |_ ___ _ __
# | |   | | | | / __| __/ _ \ '__|
# | |___| | |_| \__ \ ||  __/ |
#  \____|_|\__,_|___/\__\___|_|


GQL_GET_CLUSTER_INFO = """
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


GQL_GET_REPOSITORIES_INFO = """
  {
    repositories {
      id
      name
      technologies {
        id
        label
        available
        __typename
      }
    }
  }
"""

GQL_GET_RUNTIMES = """
query technologyQuery($id: UUID!){
    technology(id: $id){ 
        __typename 
        ... on JobTechnology {contexts{
        id 
        label 
        available}}
        ... on SparkTechnology {contexts{label}}
        ... on AppTechnology{
            id
            label
            available
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
