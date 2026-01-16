import sys
import os
import json
import pytest

# Add lambda directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../lambda/miniapp_api')))

from app import handle_create_task, handle_get_tasks

def test_create_task(tasks_table):
    user_id = 12345
    body = {"text": "Buy milk", "priority": "high"}
    
    response = handle_create_task(user_id, body)
    
    assert response["statusCode"] == 201
    body_json = json.loads(response["body"])
    assert "taskId" in body_json
    assert body_json["message"] == "Task created"
    
    # Verify in DB
    items = tasks_table.scan()["Items"]
    assert len(items) == 1
    assert items[0]["text"] == "Buy milk"
    assert items[0]["priority"] == "high"

def test_get_tasks(tasks_table):
    user_id = 12345
    # Create mock tasks
    tasks_table.put_item(Item={"userId": user_id, "taskId": "t1", "text": "Task 1", "priority": "medium"})
    tasks_table.put_item(Item={"userId": user_id, "taskId": "t2", "text": "Task 2", "priority": "low"})
    
    response = handle_get_tasks(user_id)
    
    assert response["statusCode"] == 200
    body_json = json.loads(response["body"])
    assert len(body_json["tasks"]) == 2
