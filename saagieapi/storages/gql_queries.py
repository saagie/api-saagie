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
}

query projectQuery($id: UUID!, $minimal: Boolean!) {
  project(id: $id) {
    volumes {
      id
      name
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
    description
    size
    creator
    linkedApp {
      id
    }
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
