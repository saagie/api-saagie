# pylint: disable=duplicate-code
GQL_LIST_STORAGE_FOR_PROJECT = """
query projectQuery($id: UUID!) {  
    project(id: $id) {    
        volumes {      
            id      
            name      
            size      
            description      
            creationDate      
            creator      
            linkedApp {        
                id        
                name        
                versions {          
                    number          
                    volumesWithPath {            
                        path            
                        volume {              
                            id        
                        }                      
                    }     
                }        
                currentVersion {          
                    number               
                }     
            }   
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
    __typename
  }
}
"""
