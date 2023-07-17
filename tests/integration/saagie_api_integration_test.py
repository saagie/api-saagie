class TestIntegrationSaagieAPI:
    @staticmethod
    def test_check_condition_expression(create_global_project):
        conf = create_global_project
        result = conf.saagie_api.check_condition_expression(expression="1 + 1 == 2", project_id=conf.project_id)

        assert result["evaluateConditionExpression"] is True

    @staticmethod
    def test_count_condition_logs(create_global_project, create_graph_pipeline):
        conf = create_global_project

        pipeline_id, job_id = create_graph_pipeline
        conf.saagie_api.pipelines.run_with_callback(pipeline_id=pipeline_id)

        pipeline_info = conf.saagie_api.pipelines.get_info(pipeline_id=pipeline_id)

        if pipeline_info["graphPipeline"]["instances"]:
            for cond_inst in pipeline_info["graphPipeline"]["instances"][0]["conditionsInstance"]:
                if cond_inst["id"]:
                    cond_inst_id = cond_inst["id"]
                    break

        nb_logs = conf.saagie_api.count_condition_logs(
            condition_instance_id=cond_inst_id, project_id=conf.project_id, streams=["STDOUT", "STDERR"]
        )

        conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

        # nb logs lines can be different for 2 instances, test only that result is int
        assert isinstance(nb_logs["conditionPipelineCountFilteredLogs"], int)

    @staticmethod
    def test_get_condition_instance_logs_by_condition(create_global_project, create_graph_pipeline):
        conf = create_global_project

        pipeline_id, job_id = create_graph_pipeline
        conf.saagie_api.pipelines.run_with_callback(pipeline_id=pipeline_id)

        pipeline_info = conf.saagie_api.pipelines.get_info(pipeline_id=pipeline_id)

        if pipeline_info["graphPipeline"]["instances"]:
            pipeline_instance_id = pipeline_info["graphPipeline"]["instances"][0]["id"]
            for cond_inst in pipeline_info["graphPipeline"]["instances"][0]["conditionsInstance"]:
                if cond_inst["id"]:
                    cond_id = cond_inst["conditionNodeId"]
                    break

        logs = conf.saagie_api.get_condition_instance_logs_by_condition(
            condition_id=cond_id,
            project_id=conf.project_id,
            pipeline_instance_id=pipeline_instance_id,
            streams=["STDOUT", "STDERR"],
        )

        conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

        assert "content" in logs["conditionPipelineByNodeIdFilteredLogs"]

    @staticmethod
    def test_get_condition_instance_logs_by_instance(create_global_project, create_graph_pipeline):
        conf = create_global_project

        pipeline_id, job_id = create_graph_pipeline
        conf.saagie_api.pipelines.run_with_callback(pipeline_id=pipeline_id)

        pipeline_info = conf.saagie_api.pipelines.get_info(pipeline_id=pipeline_id)

        if pipeline_info["graphPipeline"]["instances"]:
            for cond_inst in pipeline_info["graphPipeline"]["instances"][0]["conditionsInstance"]:
                if cond_inst["id"]:
                    cond_inst_id = cond_inst["id"]
                    break

        logs = conf.saagie_api.get_condition_instance_logs_by_instance(
            condition_instance_id=cond_inst_id,
            project_id=conf.project_id,
            streams=["STDOUT", "STDERR"],
        )

        conf.saagie_api.pipelines.delete(pipeline_id)
        conf.saagie_api.jobs.delete(job_id)

        assert "content" in logs["conditionPipelineFilteredLogs"]
