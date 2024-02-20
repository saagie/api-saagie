# pylint: disable=duplicate-code
GQL_LIST_JOBS_FOR_PROJECT_MINIMAL = """
query jobsQuery($projectId: UUID!){
    jobs(projectId: $projectId){
        id
        name
        alias
    }
}
"""

GQL_LIST_JOBS_FOR_PROJECT = """
query jobsQuery($projectId: UUID!, $category: String, $technologyId: UUID, $instancesLimit: Int, $versionsLimit: Int, $versionsOnlyCurrent: Boolean){
    jobs(projectId: $projectId, category: $category, technologyId: $technologyId){
        id
        name
        alias
        description
        alerting{
            emails
            loginEmails{
                login
                email
            }
            statusList
        }
        countJobInstance
        instances(limit: $instancesLimit){
            id
            status
            history {
                currentStatus {
                    status
                    details
                    reason
                }
            }
            startTime
            endTime
        }
        versions(limit: $versionsLimit, onlyCurrent: $versionsOnlyCurrent) {
            number
            creationDate
            releaseNote
            runtimeVersion
            commandLine
            packageInfo{
                name
                downloadUrl
            }
            dockerInfo{
                image
                dockerCredentialsId
            }
            extraTechnology{
                language
                version
            }
            isCurrent
            isMajor
            deletableState {
                deletable
                reasons
            }
            sourceUrl
        }
        category
        technology {
            id
        }
        isScheduled
        cronScheduling
        scheduleTimezone
        scheduleStatus
        isStreaming
        creationDate
        migrationStatus
        migrationProjectId
        isDeletable
        pipelines {
            id
        }
        graphPipelines{
            id
        }
        doesUseGPU
        resources{
            cpu {
                request
                limit
            }
            memory{
                request
                limit
            }
        }
        originalJobId
    }
}
"""

GQL_GET_JOB_INSTANCE = """
query jobInstanceQuery($jobInstanceId: UUID!){
    jobInstance(id: $jobInstanceId){
        id
        number
        status
        history {
            currentStatus {
                status
                details
                reason
            }
        }
        startTime
        endTime
        jobId
        jobAlias
        version {
            number
            releaseNote
            runtimeVersion
            commandLine
            isMajor
            isCurrent
        }
        executionGlobalVariablesInput{
            key
            value
            isPassword
        }
        executionVariablesInput {
            parentJobInstanceId
            parentJobId
            parentJobAlias
            isDirectParent
            executionVariables {
                key
                value
                isPassword
            }
            isGlobalVariables
        }
        executionVariablesOutput {
            key
            value
            isPassword
        }
        executionVariablesByKey {
            keyVariable
            isPassword
            valueVariablesInputByJobInstance{
                jobInstanceId
                jobId
                jobAlias
                jobName
                isDirectParent
                value
                isPassword
            }
            valueGlobalVariableInput
            valueVariableOutput
        }
    }
}
"""

GQL_RUN_JOB = """
mutation runJobMutation($jobId: UUID!){
    runJob(jobId: $jobId){
        id
        status
    }
}
"""

GQL_STOP_JOB_INSTANCE = """
mutation stopJobInstanceMutation($jobInstanceId: UUID!){
    stopJobInstance(jobInstanceId: $jobInstanceId){
        id
        number
        status
        history {
            currentStatus {
                status
                details
                reason
            }
        }
        startTime
        endTime
        jobId
    }
}
"""

GQL_EDIT_JOB = """
mutation editJobMutation($jobId: UUID!, $name: String, $description: String, 
                         $isScheduled: Boolean!, $cronScheduling: Cron, $scheduleTimezone: TimeZone,
                         $alerting: JobPipelineAlertingInput, $resources: JobResourceInput) {
    editJob(job: {
        id: $jobId
        name: $name
        description: $description
        isScheduled: $isScheduled
        cronScheduling: $cronScheduling
        scheduleTimezone: $scheduleTimezone
        alerting: $alerting
        resources: $resources
    }){
        id
        name
        alias
        description
        isScheduled
        cronScheduling
        scheduleTimezone
        resources{
            cpu {
                request
                limit}
            memory{
                request
                limit}
        }
        alerting{
            emails
            statusList
        }
    }
}
"""

GQL_CREATE_JOB = """
mutation createJobMutation($projectId: UUID!, 
                            $name: String!, 
                            $description: String, 
                            $category: String!,
                            $isScheduled: Boolean!, 
                            $cronScheduling: Cron, 
                            $scheduleTimezone: TimeZone
                            $technologyId: UUID!, 
                            $extraTechnology: ExtraTechnologyInput,
                            $alerting: JobPipelineAlertingInput, 
                            $resources: JobResourceInput,
                            $releaseNote: String, 
                            $runtimeVersion: String, 
                            $commandLine: String,
                            $dockerInfo: JobDockerInput, 
                            $file: Upload, 
                            $sourceUrl: String) {
    createJob(
        job: {
            projectId: $projectId
            name: $name
            description: $description
            category: $category
            technology: {
                id: $technologyId
            }
            isStreaming: false
            isScheduled: $isScheduled
            cronScheduling: $cronScheduling
            scheduleTimezone: $scheduleTimezone
            alerting: $alerting
            resources: $resources
            doesUseGPU: false
        }
        jobVersion: {
            releaseNote: $releaseNote
            runtimeVersion: $runtimeVersion
            commandLine: $commandLine
            extraTechnology: $extraTechnology
            dockerInfo: $dockerInfo
            sourceUrl: $sourceUrl
        }
        file: $file
    ){
        id
        versions {
            number
            __typename
        }
        __typename
    }
}
"""

GQL_UPGRADE_JOB = """
mutation addJobVersionMutation($jobId: UUID!, 
                                $releaseNote: String, 
                                $runtimeVersion: String, 
                                $commandLine: String,
                                $extraTechnology: ExtraTechnologyInput,
                                $usePreviousArtifact: Boolean, 
                                $dockerInfo: JobDockerInput, 
                                $file: Upload,
                                $sourceUrl: String) {
    addJobVersion(
        jobId: $jobId
        jobVersion: {
            releaseNote: $releaseNote
            runtimeVersion: $runtimeVersion
            commandLine: $commandLine
            extraTechnology: $extraTechnology
            dockerInfo: $dockerInfo
            usePreviousArtifact: $usePreviousArtifact
            sourceUrl: $sourceUrl
        }
        file: $file
    ){
        number
        __typename
    }
}
"""

GQL_GET_JOB_INFO = """
query jobInfoQuery($jobId: UUID!, $instancesLimit: Int, $versionsLimit: Int, $versionsOnlyCurrent: Boolean){
    job(id: $jobId){
        id
        name
        alias
        description
        alerting{
            emails
            loginEmails{
                login
                email
            }
            statusList
        }
        instances(limit: $instancesLimit){
            id
            status
            history {
                currentStatus {
                    status
                    details
                    reason
                }
            }
            startTime
            endTime
            version {
                number
                releaseNote
                runtimeVersion
                commandLine
                isMajor
                doesUseGPU
            }
        }
        countJobInstance
        versions(limit: $versionsLimit, onlyCurrent: $versionsOnlyCurrent) {
            number
            creationDate
            releaseNote
            runtimeVersion
            commandLine
            packageInfo{
                name
                downloadUrl
            }
            dockerInfo{
                image
                dockerCredentialsId
            }
            extraTechnology{
                language
                version
            }
            isCurrent
            isMajor
            deletableState {
                deletable
                reasons
            }
            sourceUrl
        }
        category
        technology {
            id
        }
        isScheduled
        cronScheduling
        scheduleStatus
        scheduleTimezone
        isStreaming
        creationDate
        migrationStatus
        migrationProjectId
        isDeletable
        graphPipelines(isCurrent: true){
            id
        }
        doesUseGPU
        resources{
            cpu {
                request
                limit
            }
            memory{
                request
                limit
            }
        }
        originalJobId
    }
}
"""

GQL_GET_JOB_INFO_BY_ALIAS = """
query jobInfoByAlias($projectId: UUID!, $alias: String!, $instancesLimit: Int, $versionsLimit: Int, $versionsOnlyCurrent: Boolean){
    jobByAlias(projectId: $projectId, alias: $alias){
        id
        name
        alias
        description
        alerting{
            emails
            loginEmails{
                login
                email
            }
            statusList
        }
        instances(limit: $instancesLimit){
            id
            history {
                currentStatus {
                    status
                    details
                    reason
                }
            }
            startTime
            endTime
            version {
                number
                releaseNote
                runtimeVersion
                commandLine
                isMajor
            }
        }
        countJobInstance
        versions(limit: $versionsLimit, onlyCurrent: $versionsOnlyCurrent) {
            number
            creationDate
            releaseNote
            runtimeVersion
            commandLine
            packageInfo{
                name
                downloadUrl
            }
            dockerInfo{
                image
                dockerCredentialsId
            }
            extraTechnology{
                language
                version
            }
            isCurrent
            isMajor
            deletableState {
                deletable
                reasons
            }
            sourceUrl
        }
        category
        technology {
            id
        }
        isScheduled
        cronScheduling
        scheduleStatus
        scheduleTimezone
        isStreaming
        creationDate
        migrationStatus
        migrationProjectId
        isDeletable
        graphPipelines(isCurrent: true){
            id
        }
        doesUseGPU
        resources{
            cpu {
                request
                limit
            }
            memory{
                request
                limit
            }
        }
        originalJobId
    }
}
"""

GQL_DELETE_JOB = """
mutation deleteJobMutation($jobId: UUID!){
    deleteJob(jobId: $jobId)
}
"""

GQL_ROLLBACK_JOB_VERSION = """
mutation rollbackJobVersionMutation($jobId: UUID!, $versionNumber: Int!) {  
    rollbackJobVersion(jobId: $jobId, versionNumber: $versionNumber) {    
        id    
        versions {      
            number      
            isCurrent      
        }    
    }
}
"""

GQL_DELETE_JOB_INSTANCE = """
mutation deleteJobInstances($jobId: UUID!, $jobInstancesId: [UUID!]) {
    deleteJobInstances(jobId: $jobId, jobInstanceIds: $jobInstancesId){
        id
        success
    }
}
"""

GQL_DELETE_JOB_INSTANCES_BY_SELECTOR = """
mutation deleteJobInstancesBySelector($jobId: UUID!, 
                                    $selector: JobInstanceSelector!, 
                                    $excludeJobInstanceId: [UUID!], 
                                    $includeJobInstanceId: [UUID!]) {
    deleteJobInstancesBySelector(
        jobId: $jobId, 
        selector: $selector,
        excludeJobInstanceIds: $excludeJobInstanceId,
        includeJobInstanceIds: $includeJobInstanceId
    )
}
"""

GQL_DELETE_JOB_INSTANCES_BY_DATE = """
mutation deleteJobInstancesByDate($jobId: UUID!, 
                                    $beforeAt: DateTime!, 
                                    $excludeJobInstanceId: [UUID!], 
                                    $includeJobInstanceId: [UUID!]) {
    deleteJobInstancesByDate(
        jobId: $jobId, 
        beforeAt: $beforeAt,
        excludeJobInstanceIds: $excludeJobInstanceId,
        includeJobInstanceIds: $includeJobInstanceId
    )
}
"""

GQL_DELETE_JOB_VERSION = """
mutation deleteJobVersion($jobId: UUID!, $jobVersionsNumber: [Int!]!) {
    deleteJobVersions(jobId: $jobId, jobVersionNumbers: $jobVersionsNumber) {
        number
        success
    }
}
"""

GQL_DUPLICATE_JOB = """
mutation duplicateJob($jobId: UUID!) {
    duplicateJob(originalJobId: $jobId) {
        id
        name
    }
}
"""

GQL_COUNT_INSTANCES_BY_SELECTOR = """
query countJobInstancesBySelector($jobId: UUID!) {
    countJobInstancesBySelector(jobId: $jobId) {
        selector
        count
    }
}
"""

GQL_COUNT_INSTANCES_BY_DATE = """
query countJobInstancesByDate($jobId: UUID!, $beforeAt: DateTime!) {
    countJobInstancesByDate(
        jobId: $jobId, 
        beforeAt: $beforeAt
    )
}
"""

GQL_MOVE_JOB = """
mutation migrateJobsMutation($jobId: UUID!, $targetPlatformId: Int!, $targetProjectId: UUID!) {  
    moveJob(jobId: $jobId, targetPlatformId: $targetPlatformId, targetProjectId: $targetProjectId)
}
"""

GQL_GENERATE_JOB_DESCRIPTION = """
mutation editJobWithAiGeneratedDescriptionMutation($jobId: UUID!) {
    editJobWithAiGeneratedDescription(jobId: $jobId) {
        id
        description
        aiDescriptionVersionNumber
    }
}
"""
