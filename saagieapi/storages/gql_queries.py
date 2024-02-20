# pylint: disable=duplicate-code
GQL_LIST_STORAGE_FOR_PROJECT = """
fragment appVersionFieldInformation on AppVersion {
    number
    volumesWithPath {
        path
        volume {
            id
        }
    }
}

fragment volumeInformation on Volume {
    size
    description
    creationDate
    creator
    linkedApp {
        id
        name
        versions {
            ...appVersionFieldInformation
        }
        currentVersion {
            ...appVersionFieldInformation
        }
    }
    originalVolumeId
    duplicationStatus
    isLocked
}

query projectQuery($id: UUID!, $minimal: Boolean!) {
    project(id: $id) {
        volumes {
            id
            name
            projectId
            ...volumeInformation @skip(if: $minimal)
        }
    }
}
"""

GQL_CREATE_STORAGE = """
mutation createVolumeMutation($volume: VolumeInput!) {
    createVolume(volume: $volume) {
        id
        name
        projectId
        description
        size
        creator
        linkedApp {
            id
        }
        originalVolumeId
        duplicationStatus
        isLocked
    }
}
"""

GQL_EDIT_STORAGE = """
mutation editVolumeMutation($volume: VolumeEditionInput!) {
    editVolume(volumeEdition: $volume) {
        id
        name
    }
}
"""

GQL_DELETE_STORAGE = """
mutation deleteVolumeMutation($id: UUID!) {
    deleteVolume(id: $id) {
        id
        name
    }
}
"""

GQL_UNLINK_STORAGE = """
mutation unlinkVolumeMutation($id: UUID!) {
    unlinkVolume(id: $id) {
        id
        name
    }
}
"""

GQL_MOVE_STORAGE = """
mutation moveVolumeMutation($volumeId: UUID!, $targetPlatformId: Int!, $targetProjectId: UUID!) {  
    moveVolume(volumeId: $volumeId, targetPlatformId: $targetPlatformId, targetProjectId: $targetProjectId)
}
"""

GQL_GET_STORAGE_INFO = """
fragment appVersionFieldInformation on AppVersion {
    number
    volumesWithPath {
        path
        volume {
            id
        }
    }
}

query volumeInfoQuery($volumeId: UUID!) {
    volume(id: $volumeId) {
        id
        name
        projectId
        size
        description
        creationDate
        creator
        linkedApp {
            id
            name
            versions {
                ...appVersionFieldInformation
            }
            currentVersion {
                ...appVersionFieldInformation
            }
        }
        originalVolumeId
        duplicationStatus
        isLocked
    }
}
"""

GQL_DUPLICATE_STORAGE = """
mutation duplicateVolume($volumeId: UUID!) {
    duplicateVolume(originalVolumeId: $volumeId) {
        id
        name
        originalVolumeId
        duplicationStatus
        isLocked
    }
}
"""
