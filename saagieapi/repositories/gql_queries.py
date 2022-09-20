GQL_LIST_REPOSITORIES = """
query repsositoriesQuery($minimal: Boolean!, $lastSynchronization: Boolean) {
  repositories {
    id
    name
    synchronizationReports(lastSynchronization: $lastSynchronization) {
      lastReversibleId
      ...reportInformations @skip(if: $minimal)
    }
    ...repositoryInformations @skip(if: $minimal)
  }
}

fragment repositoryInformations on Repository {
    technologies {
      available
      id
      label
    }
    source {
      ... on UrlSource {
        url
      }
      ... on FileSource {
        name
      }
    }
}

fragment reportInformations on SynchronizationReports {
    count
      list {
        endedAt
        ... on SuccessfulSynchronization {
          endedAt
          issues {
            message
            path
          }
          revert {
            date
            author
          }
        }
        ... on FailedSynchronization {
          failure
        }
      }
}
"""


GQL_CREATE_REPOSITORY = """
mutation addRepositoryMutation(
  $repositoryInput: RepositoryInput!
  $upload: Upload
) {
  addRepository(repositoryInput: $repositoryInput, upload: $upload) {
    count
    objects {
      id
      name
    }
  }
}
"""

GQL_DELETE_REPOSITORY = """
mutation RemoveRepository($removeRepositoryId: UUID!) {
  removeRepository(id: $removeRepositoryId) {
    id
    name
  }
}
"""

GQL_EDIT_REPOSITORY = """
mutation editRepositoryMutation($repositoryInput: RepositoryEditionInput!) {
  editRepository(repositoryInput: $repositoryInput) {
    count
    objects {
      name
      source {
        ... on UrlSource {
          url
        }
        ... on FileSource {
          name
        }
      }
      id
    }
  }
}
"""

GQL_SYNCHRONIZE_REPOSITORY = """
mutation synchronizeRepository($id: UUID!, $upload: Upload) {
  synchronizeRepository(id: $id, upload: $upload) {
    count
    report {
      id
      endedAt
      startedAt
      trigger {
        author
        type
      }
      ... on SuccessfulSynchronization {
        technologyReports {
          status
          technologyId
        }
        issues {
          message
          path
        }
      }
      ... on FailedSynchronization {
        failure
      }
    }
    repositoryId
    repositoryName
  }
}
"""

GQL_REVERT_LAST_SYNCHRONISATION = """
mutation revertLastSynchronization($repositoryId: UUID!, $synchronizationReportId: UUID!) {
  revertLastSynchronization(repositoryId: $repositoryId, synchronizationReportId: $synchronizationReportId) {
    report {
      id
      trigger {
        author
        type
      }
      endedAt
      startedAt
    }
    repositoryName
    repositoryId
  }
}
"""

GQL_GET_REPOSITORY_INFO = """
query RepositoryQuery($id: UUID!, $withReverted: Boolean, $lastSynchronization: Boolean, $limit: Int) {
  repository(id: $id) {
    creationDate
    creator
    editor
    id
    modificationDate
    name
    readOnly
    source {
      ... on UrlSource {
        url
      }
      ... on FileSource {
        name
      }
    }
    synchronizationReports(limit: $limit, withReverted: $withReverted, lastSynchronization: $lastSynchronization) {
      count
      list {
        source {
          ... on UrlSource {
            url
          }
          ... on FileSource {
            name
          }
        }
        ... on SuccessfulSynchronization {
          endedAt
          startedAt
          trigger {
            author
            type
          }
          technologyReports {
            status
            technologyId
            message
          }
          issues {
            message
            path
          }
          revert {
            author
            date
          }
        }
        ... on FailedSynchronization {
          endedAt
          startedAt
          trigger {
            author
            type
          }
          failure
        }
      }
      lastReversibleId
    }
    connectionTypes {
      id
      label
      actions {
        checkConnection {
          scriptId
        }
      }
    }
    technologies {
      id
      technologyId
      label
      icon
      repositoryId
      available
      missingFacets
      description
      ... on AppTechnology {
        appContexts {
          id
          label
          available
          missingFacets
          recommended
          description
          dockerInfo {
            image
            version
          }
          trustLevel
          deprecationDate
          lastUpdate
        }
      }
      ... on JobTechnology {
        contexts {
          id
          label
          available
          missingFacets
          description
          recommended
          dockerInfo {
            image
            version
          }
          trustLevel
          deprecationDate
          lastUpdate
        }
      }
      ... on ExtJobTechnology {
        iconUrl
        contexts {
          id
          label
          available
          missingFacets
          description
          recommended
          trustLevel
          deprecationDate
          lastUpdate
          connectionTypeUUID
          actions {
            getStatus {
              scriptId
            }
            start {
              scriptId
            }
            stop {
              scriptId
            }
            getLogs {
              scriptId
            }
          }
        }
      }
      ... on SparkTechnology {
        contexts {
          id
          label
          available
          missingFacets
          description
          recommended
          trustLevel
          deprecationDate
          dockerInfo {
            image
            version
          }
          technologyContexts {
            available
            missingFacets
            description
            id
            label
            recommended
            trustLevel
            deprecationDate
            jobContexts {
              available
              description
              dockerInfo {
                image
                version
              }
              id
              label
              recommended
              trustLevel
              deprecationDate
              lastUpdate
            }
          }
        }
      }
    }
  }
}
"""
