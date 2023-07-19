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
        events(limit: $limit, skip: $skip) {
                appHistoryId
                action {
                    # appHistoryId # TODO Question : Pourquoi ça fonctionne pas ? 
                    event {
                        recordAt
                        executionId
                        ... on RunAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on StopAction {
                            author
                            __typename
                        }
                        ... on RollbackAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on UpgradeAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on RestartAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on StatusRetrieve {
                            status
                            reason
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                statuses {
                    event {
                        recordAt
                        executionId
                        ... on StatusRetrieve {
                            status
                            reason
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
        runningVersionNumber
        currentDockerInfo {
            image
            dockerCredentialsId
        }
        currentStatus
        currentStatusReason
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
            currentStatusReason
            currentExecutionId
            currentDockerInfo {
                image
                dockerCredentialsId
            }
            startTime
            stopTime
            author
            countEvents
            events(limit: $limit, skip: $skip) {
                appHistoryId
                action {
                    # appHistoryId # TODO Question : Pourquoi ça fonctionne pas ? 
                    event {
                        recordAt
                        executionId
                        ... on RunAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on StopAction {
                            author
                            __typename
                        }
                        ... on RollbackAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on UpgradeAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on RestartAction {
                            versionNumber
                            author
                            __typename
                        }
                        ... on StatusRetrieve {
                            status
                            reason
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                statuses {
                    event {
                        recordAt
                        executionId
                        ... on StatusRetrieve {
                            status
                            reason
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
            }
            __typename
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

GQL_ROLLBACK_APP_VERSION = """
mutation rollbackAppVersionMutation($appId: UUID!, $versionNumber: Int!) {
    rollbackAppVersion(appId: $appId, versionNumber: $versionNumber) {
        id
        versions {
            number
        }
        currentVersion {
            number
        }
    }
}
"""
