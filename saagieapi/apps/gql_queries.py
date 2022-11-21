# pylint: disable=duplicate-code
GQL_LIST_APPS_FOR_PROJECT = """
fragment versionInfo on AppVersion {
  number
  creationDate
  releaseNote
  dockerInfo {
    image
    dockerCredentialsId
  }
  runtimeContextId
  creator
  ports {
    name
    number
    isRewriteUrl
    basePathVariableName
    scope
    internalUrl
  }
  isMajor
  volumesWithPath {
    path
    volume {
      id
      name
      creator
      description
      size
      projectId
      creationDate
      linkedApp {
        id
        name
      }
    }
  }
}

fragment appInformations on App {
  description
  creationDate
  creator
  versions @skip(if: $versionsOnlyCurrent) {
    ...versionInfo
  }
  currentVersion {
    ...versionInfo
  }
  technology {
    id
  }
  linkedVolumes {
    id
    name
    creator
    description
    size
    creationDate
  }
  isGenericApp
  history {
    id
    events {
      event {
        recordAt
        executionId
        __typename
        ... on RunAction {
          versionNumber
          author
        }
        ... on StopAction {
          author
        }
        ... on RollbackAction {
          versionNumber
          author
        }
        ... on UpgradeAction {
          versionNumber
          author
        }
        ... on RestartAction {
          versionNumber
          author
        }
        ... on StatusRetrieve {
          status
        }
      }
      transitionTime
    }
    runningVersionNumber
    currentDockerInfo {
      image
      dockerCredentialsId
    }
    currentStatus
    currentExecutionId
    startTime
    stopTime
  }
  alerting {
    emails
    statusList
    loginEmails {
      login
      email
    }
  }
  resources {
    cpu {
      request
      limit
    }
    memory {
      request
      limit
    }
  }
}

query projectQuery($id: UUID!, $minimal: Boolean!, $versionsOnlyCurrent: Boolean!) {
  project(id: $id) {
    apps {
      id
      name
      ...appInformations @skip(if: $minimal)
    }
  }
}
"""

GQL_GET_APP_INFO = """
fragment appVersionFieldFullInformation on AppVersion {
  number
  creator
  creationDate
  releaseNote
  dockerInfo {
    image
    dockerCredentialsId
  }
  runtimeContextId
  ports {
    name
    number
    isRewriteUrl
    basePathVariableName
    scope
    internalUrl
  }
  volumesWithPath {
    path
    volume {
      id
      name
      creator
      description
      size
      projectId
      creationDate
      linkedApp {
        id
        name
      }
    }
  }
  isMajor
}

query app($id: UUID!, $versionsOnlyCurrent: Boolean!) {
  app(id: $id) {
    id
    name
    creationDate
    technology {
      id
    }
    project {
      id
      name
    }
    description
    creationDate
    versions @skip(if: $versionsOnlyCurrent) {
      ...appVersionFieldFullInformation
    }
    currentVersion {
      ...appVersionFieldFullInformation
    }
    history {
      id
      currentStatus
      currentExecutionId
      currentDockerInfo {
        image
        dockerCredentialsId
      }
      startTime
      stopTime
      events {
        event {
          recordAt
          executionId
          __typename
          ... on RunAction {
            versionNumber
            author
          }
          ... on StopAction {
            author
          }
          ... on RollbackAction {
            versionNumber
            author
          }
          ... on UpgradeAction {
            versionNumber
            author
          }
          ... on RestartAction {
            versionNumber
            author
          }
          ... on StatusRetrieve {
            status
          }
        }
        transitionTime
      }
    }
    isGenericApp
    alerting {
      emails
      statusList
      loginEmails {
        login
        email
      }
    }
    resources {
      cpu {
        request
        limit
      }
      memory {
        request
        limit
      }
    }
    linkedVolumes {
      id
      name
      creator
      description
      size
      creationDate
    }
  }
}
"""

GQL_CREATE_APP_CATALOG = """
mutation installAppMutation($projectId: UUID!, $technologyId: UUID!, $contextId: String!) {
  installApp(projectId: $projectId, technologyId: $technologyId, contextId: $contextId) {
    id
    name
  }
}
"""

GQL_CREATE_APP_SCRATCH = """
mutation createAppMutation($app: AppInput!) {
  createApp(app: $app) {
    id
  }
}
"""

GQL_EDIT_APP = """
mutation editAppMutation($app: AppEditionInput!) {
  editApp(appEdition: $app) {
    id
  }
}
"""

GQL_DELETE_APP = """
mutation deleteAppMutation($appId: UUID!) {
  deleteApp(appId: $appId) {
    id
  }
}
"""

GQL_STOP_APP = """
mutation stopAppMutation($id: UUID!) {
  stopApp(id: $id) {
    id
    history {
      id
      runningVersionNumber
      currentStatus
    }
  }
}
"""

GQL_RUN_APP = """
mutation runAppMutation($id: UUID!) {
  runApp(id: $id) {
    id
    versions {
      number
    }
    history {
      id
      currentDockerInfo {
        image
        dockerCredentialsId
      }
      runningVersionNumber
      currentStatus
    }
  }
}
"""

GQL_UPDATE_APP = """
mutation addAppVersion($appId: UUID!, $appVersion: AppVersionInput!) {
  addAppVersion(appId: $appId, version: $appVersion) {
    number
    releaseNote
    dockerInfo {
      image
      dockerCredentialsId
    }
    ports {
      number
      name
      basePathVariableName
      isRewriteUrl
      scope
    }
    volumesWithPath {
      path
      volume {
        id
        name
        size
        creator
      }
    }
  }
}
"""
