"""DynamoDB helpers — mirrors PSP shared/db.py pattern."""
import boto3
from typing import Optional
from config import app_config

dynamodb = boto3.resource("dynamodb", region_name=app_config.aws_region)


def get_table(name: str):
    return dynamodb.Table(name)


def get_execution(execution_id: str) -> Optional[dict]:
    table = get_table(app_config.scaffold_executions_table)
    return table.get_item(Key={"executionId": execution_id}).get("Item")


def put_item(table_name: str, item: dict) -> None:
    get_table(table_name).put_item(Item=item)


def update_item(table_name: str, key: dict, updates: dict) -> dict:
    expr_parts, attr_names, attr_values = [], {}, {}
    for i, (k, v) in enumerate(updates.items()):
        ph, vk = f"#a{i}", f":v{i}"
        expr_parts.append(f"{ph} = {vk}")
        attr_names[ph] = k
        attr_values[vk] = v
    table = get_table(table_name)
    resp = table.update_item(
        Key=key,
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp.get("Attributes", {})
