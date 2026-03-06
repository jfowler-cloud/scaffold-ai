"""Lambda: poll Step Functions execution status — called by frontend."""
import json
import logging
import os
import sys

import boto3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from config import app_config

logger = logging.getLogger(__name__)
sfn = boto3.client("stepfunctions", region_name=app_config.aws_region)


def handler(event: dict, context=None) -> dict:
    """
    Input:  {executionArn} (from API Gateway path param or body)
    Output: {status, output} where output is the final Step Functions state when SUCCEEDED
    """
    execution_arn = (
        event.get("executionArn")
        or event.get("pathParameters", {}).get("executionArn")
    )
    if not execution_arn:
        return {"statusCode": 400, "body": json.dumps({"error": "executionArn required"})}

    try:
        resp = sfn.describe_execution(executionArn=execution_arn)
        status = resp["status"]  # RUNNING | SUCCEEDED | FAILED | TIMED_OUT | ABORTED

        body: dict = {"status": status}
        if status == "SUCCEEDED":
            output = json.loads(resp.get("output", "{}"))
            body["message"] = output.get("response", "")
            body["updated_graph"] = output.get("graph_json")
            body["generated_files"] = output.get("generated_files", [])
        elif status in ("FAILED", "TIMED_OUT", "ABORTED"):
            body["error"] = resp.get("cause", "Execution failed")

        return {"statusCode": 200, "body": json.dumps(body)}
    except Exception as e:
        logger.exception("get_execution failed: %s", e)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
