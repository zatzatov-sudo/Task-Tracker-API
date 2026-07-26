# Manual Testing Notes


# Prerequisites
- The API server is running locally: `uvicorn app.main:app --reload --port 8000`
- Swagger UI is available at `http://127.0.0.1:8000/docs`

# Using Swagger UI (Interactive Documentation)

**Test 1**

- Step 1: Create a Task
  Click `POST /tasks`, then **Try it out**.
  Under "Edit Value", paste the following:
     {
       "title": "Testing_Task",
       "description": "Brief_description",
       "status": "ToDo",
       "priority": "High",
       "assignee": "Hassan"
     }
- Step2: Under "Responses", I got the following: (successful)
      {
        "id": "7b8429cd-9c7f-4f2c-8a08-c4a220638592",
        "title": "Testing_Task",
        "description": "Brief_description",
        "status": "ToDo",
        "priority": "High",
        "assignee": "Hassan",
        "tags": [],
        "created_at": "2026-07-26T17:22:23.249287Z",
        "updated_at": "2026-07-26T17:22:23.249287Z"
}
- Step 3: Now let's test changing the status of the created task to "Done" (bypassing InProgress):
      task_id: 7b8429cd-9c7f-4f2c-8a08-c4a220638592
      {
        "status": "Done"
      }
- Step 4: Output
      {
        "detail": "Invalid status transition from ToDo to Done. Allowed transitions: ['Done->InProgress', 'InProgress->Done', 'ToDo->InProgress']"
      }

**Test 2**

- Step 1: Let's use a non-exsisting task id "00000000-0000-0000-0000-000000000000"

- Step 2: Paste this non-exsisting id under PATCH /tasks/{task_id}.

- Step 3: Click "Execute"

- Step 4: Output
      {
       "detail": "Task with id 00000000-0000-0000-0000-000000000000 not found"
      }

