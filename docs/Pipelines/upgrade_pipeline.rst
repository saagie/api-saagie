Upgrading a pipeline
--------------------

**saagieapi.pipelines.upgrade**

Example :

.. code:: python

   #Add new Job to pipeline
   job3_id = "e5e9fa38-1af8-42e7-95df-8d983eb78387"

   #Recreate a new GraphPipeline instance 
   job_node1 = JobNode(job1_id)
   job_node2 = JobNode(job2_id)
   job_node3 = JobNode(job3_id)
   condition_node_1 = ConditionNode()
   job_node1.add_next_node(condition_node_1)
   condition_node_1.add_success_node(job_node2)
   condition_node_1.add_failure_node(job_node3)
   graph_pipeline = GraphPipeline()
   graph_pipeline.add_root_node(job_node1)

   saagie.pipelines.upgrade(pipeline_id="ca79c5c8-2e57-4a35-bcfc-5065f0ee901c",
                            graph_pipeline=graph_pipeline)

Response payload example :

.. code:: python

   {
       "addGraphPipelineVersion":{
           "number":4,
           "releaseNote":"",
           "graph":{
               "jobNodes":[
                   {
                       "id":"82383907-bdd9-4d66-bc00-a84ff3a9caee",
                       "job":{
                           "id":"7a706539-69dd-4f5d-bba3-4eac6be74d8d"
                       }
                   },
                   {
                       "id":"5501eea2-e7af-4b44-a784-387f133b28c6",
                       "job":{
                           "id":"3dbbb785-a7f4-4840-9f98-814b105a1a31"
                       }
                   },
                   {
                       "id":"560d99bb-4e7b-4ab4-a5df-d879d31b4c0a",
                       "job":{
                           "id":"e5e9fa38-1af8-42e7-95df-8d983eb78387"
                       }
                   }
               ],
               "conditionNodes":[
                   {
                       "id":"9d0e886c-7771-4aa7-8321-cbccfaf4d3bb"
                   }
               ]
           },
           "creationDate":"2022-04-28T15:35:32.381215Z[UTC]",
           "creator":"john.doe",
           "isCurrent":True,
           "isMajor":False
       }
   }