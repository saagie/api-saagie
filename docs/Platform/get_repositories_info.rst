.. _Getting repositories info


Getting repositories info
-------------------------

**saagieapi.get_repositories_info**

Example :

.. code:: python

   saagieapi.get_repositories_info()

Response payload example :

.. code:: python

   {
      "repositories":[
         {
            "id":"9fcbddfe-a7b7-4d25-807c-ad030782c923",
            "name":"Saagie",
            "technologies":[
               {
                  "id":"5cbb55aa-8ce9-449b-b0b9-64cc6781ea89",
                  "label":"R",
                  "available":True,
                  "__typename":"JobTechnology"
               },
               {
                  "id":"36912c68-d084-43b9-9fda-b5ded8eb7b13",
                  "label":"Docker image",
                  "available":True,
                  "__typename":"AppTechnology"
               },
               {
                  "id":"1d117fb6-0697-438a-b419-a69e0e7406e8",
                  "label":"Spark",
                  "available":True,
                  "__typename":"SparkTechnology"
               }
            ]
         },
         {
            "id":"fff42d30-2029-4f23-b326-d751f256f533",
            "name":"Saagie Community",
            "technologies":[
               {
                  "id":"034c28d7-c21f-4d7c-8dd9-7d09bc02f33f",
                  "label":"ShinyProxy",
                  "available":True,
                  "__typename":"AppTechnology"
               }
            ]
         }
      ]
   }