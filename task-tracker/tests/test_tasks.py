def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post("/tasks", json={"title": "Buy groceries"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy groceries"
    assert body["description"] == ""
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"
    assert body["assignee"] is None
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post(
        "/tasks", json={"title": "Buy groceries", "priority": "Urgent"}
    )
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post(
        "/tasks", json={"title": "Buy groceries", "nonexistent_field": "value"}
    )
    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(
    client, created_task
):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low priority task", "priority": "Low"})
    client.post("/tasks", json={"title": "High priority task", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "High priority task"
    assert body[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created_task["id"]


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Task with id 00000000-0000-0000-0000-000000000000 not found"
    )


def test_patch_partial_update_keeps_other_fields(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}", json={"priority": "High"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["priority"] == "High"
    assert body["title"] == created_task["title"]
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["assignee"] == created_task["assignee"]


def test_patch_not_found_returns_404(client):
    response = client.patch(
        "/tasks/00000000-0000-0000-0000-000000000000", json={"title": "Ghost"}
    )
    assert response.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}", json={"status": "InProgress"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# --- Tags ---

def test_create_task_with_tags_returns_normalized_tags(client):
    response = client.post("/tasks", json={"title": "Tagged task", "tags": ["Bug", " Frontend ", "bug"]})
    assert response.status_code == 201
    body = response.json()
    # "Bug" and "bug" deduplicate to one; " Frontend " strips to "frontend"
    assert body["tags"] == ["bug", "frontend"]


def test_create_task_without_tags_returns_empty_list(client):
    response = client.post("/tasks", json={"title": "No tags"})
    assert response.status_code == 201
    assert response.json()["tags"] == []


def test_create_task_blank_tag_is_dropped(client):
    response = client.post("/tasks", json={"title": "Blank tag", "tags": ["bug", "  ", "frontend"]})
    assert response.status_code == 201
    assert response.json()["tags"] == ["bug", "frontend"]


def test_create_task_tag_too_long_returns_422(client):
    long_tag = "a" * 33
    response = client.post("/tasks", json={"title": "Long tag", "tags": [long_tag]})
    assert response.status_code == 422


def test_create_task_too_many_tags_returns_422(client):
    tags = [f"tag{i}" for i in range(11)]
    response = client.post("/tasks", json={"title": "Too many tags", "tags": tags})
    assert response.status_code == 422


def test_patch_replaces_tags(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"tags": ["backend", "urgent"]}
    )
    assert response.status_code == 200
    assert response.json()["tags"] == ["backend", "urgent"]


def test_patch_clears_tags_with_empty_list(client):
    create = client.post("/tasks", json={"title": "Has tags", "tags": ["bug"]})
    task_id = create.json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"tags": []})
    assert response.status_code == 200
    assert response.json()["tags"] == []


def test_patch_omitting_tags_preserves_existing_tags(client):
    create = client.post("/tasks", json={"title": "Keep tags", "tags": ["bug"]})
    task_id = create.json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "Updated title"})
    assert response.status_code == 200
    assert response.json()["tags"] == ["bug"]


def test_list_tasks_filter_by_tag_returns_only_matches(client):
    client.post("/tasks", json={"title": "Task A", "tags": ["bug"]})
    client.post("/tasks", json={"title": "Task B", "tags": ["frontend"]})
    response = client.get("/tasks", params={"tag": "bug"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Task A"


def test_list_tasks_filter_by_tag_case_insensitive(client):
    client.post("/tasks", json={"title": "Task A", "tags": ["bug"]})
    response = client.get("/tasks", params={"tag": "BUG"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_tasks_filter_by_tag_no_match_returns_empty(client):
    client.post("/tasks", json={"title": "Task A", "tags": ["bug"]})
    response = client.get("/tasks", params={"tag": "nonexistent"})
    assert response.status_code == 200
    assert response.json() == []