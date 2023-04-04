**saagie.pipelines.create_graph**

Creating a pipeline
-------------------

Example :

.. code:: python

   # Jobs to add in a pipeline
   job1_id = "7a706539-69dd-4f5d-bba3-4eac6be74d8d"
   job2_id = "3dbbb785-a7f4-4840-9f98-814b105a1a31"

   # Create a GraphPipeline instance
   job_node1 = JobNode(job1_id)
   job_node2 = JobNode(job2_id)
   condition_node_1 = ConditionNode()
   job_node1.add_next_node(condition_node_1)
   condition_node_1.add_success_node(job_node2)
   graph_pipeline = GraphPipeline()
   graph_pipeline.add_root_node(job_node1)

   saagie.pipelines.create_graph(project_id="860b8dc8-e634-4c98-b2e7-f9ec32ab4771",
                                 graph_pipeline=graph_pipeline,
                                 name="Amazing Pipeline",
                                 description="new pipeline",
                                 cron_scheduling="0 0 * * *",
                                 schedule_timezone="Pacific/Fakaofo",
                                 emails=["hello.world@gmail.com"],
                                 status_list=["FAILED"])

Response payload example :

.. code:: python

   {
       "createGraphPipeline": {
           "id": "ca79c5c8-2e57-4a35-bcfc-5065f0ee901c"
       }
   }
