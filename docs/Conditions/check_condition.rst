Check a condition expression
---------------
The expression can only use a Common Expression Language(CEL) expression without variables

**saagieapi.check_condition_expression**

Example :

.. code:: python

    saagieapi.check_condition_expression(expression="double(rmse) > 500.0",
                                         project_id="your_project_id",
                                         variables={"key": "rmse", "value": 300}
                                         )

Response payload example :

.. code:: python

    {
      "data": {
        "evaluateConditionExpression": False
      }
    }






