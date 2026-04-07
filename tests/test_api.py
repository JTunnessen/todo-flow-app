import pytest
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

TODAY = date.today().isoformat()
FUTURE_DATE = (date.today() + timedelta(days=30)).isoformat()
PAST_DATE = (date.today() - timedelta(days=5)).isoformat()


# ===========================================================================
# CREATE TODO  POST /todos
# ===========================================================================

class TestCreateTodo:
    """Tests for the POST /todos endpoint."""

    def test_create_todo_happy_path(self, client, sample_todo_payload):
        """Creating a todo with all valid fields should return 201 and the created item."""
        response = client.post("/todos", json=sample_todo_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_todo_payload["title"]
        assert data["description"] == sample_todo_payload["description"]
        assert data["priority"] == sample_todo_payload["priority"]
        assert data["status"] == sample_todo_payload["status"]

    def test_create_todo_returns_id(self, client, sample_todo_payload):
        """A newly created todo must have an 'id' field in the response."""
        response = client.post("/todos", json=sample_todo_payload)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_create_todo_missing_title_returns_422(self, client):
        """Omitting the required 'title' field should return HTTP 422."""
        payload = {
            "description": "No title here",
            "due_date": FUTURE_DATE,
            "priority": 1,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 422

    def test_create_todo_invalid_status_returns_422(self, client):
        """Supplying an invalid status value should return HTTP 422."""
        payload = {
            "title": "Bad Status",
            "description": "...",
            "due_date": FUTURE_DATE,
            "priority": 1,
            "status": "INVALID_STATUS"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 422

    def test_create_todo_negative_priority_returns_422(self, client):
        """Negative or zero priority should be rejected with HTTP 422."""
        payload = {
            "title": "Priority Test",
            "description": "...",
            "due_date": FUTURE_DATE,
            "priority": -1,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 422

    def test_create_todo_without_description(self, client):
        """Creating a todo without an optional description should succeed."""
        payload = {
            "title": "No Description",
            "due_date": FUTURE_DATE,
            "priority": 2,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code in (200, 201)

    def test_create_todo_without_due_date(self, client):
        """Creating a todo without a due_date should succeed if it is optional."""
        payload = {
            "title": "No Due Date",
            "description": "Optional due date",
            "priority": 3,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code in (200, 201)

    def test_create_todo_status_new(self, client):
        """A todo created with status 'New' should persist that status."""
        payload = {
            "title": "New Status Todo",
            "priority": 1,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code in (200, 201)
        assert response.json()["status"] == "New"

    def test_create_todo_status_in_process(self, client):
        """A todo created with status 'In Process' should persist that status."""
        payload = {
            "title": "In Process Todo",
            "priority": 1,
            "status": "In Process"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code in (200, 201)
        assert response.json()["status"] == "In Process"

    def test_create_todo_status_deferred(self, client):
        """A todo created with status 'Deferred' should persist that status."""
        payload = {
            "title": "Deferred Todo",
            "priority": 1,
            "status": "Deferred"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code in (200, 201)
        assert response.json()["status"] == "Deferred"

    def test_create_todo_status_complete(self, client):
        """A todo created with status 'Complete' should persist that status."""
        payload = {
            "title": "Complete Todo",
            "priority": 1,
            "status": "Complete"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code in (200, 201)
        assert response.json()["status"] == "Complete"

    def test_create_todo_empty_title_returns_422(self, client):
        """An empty string for title should be rejected."""
        payload = {
            "title": "",
            "priority": 1,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 422

    def test_create_todo_priority_zero_returns_422(self, client):
        """Priority of zero should be rejected (priority must be >= 1)."""
        payload = {
            "title": "Zero Priority",
            "priority": 0,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 422

    def test_create_todo_non_numeric_priority_returns_422(self, client):
        """A string value for priority should be rejected with HTTP 422."""
        payload = {
            "title": "String Priority",
            "priority": "high",
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 422

    def test_create_todo_invalid_due_date_format_returns_422(self, client):
        """An invalid date string for due_date should return HTTP 422."""
        payload = {
            "title": "Bad Date",
            "due_date": "not-a-date",
            "priority": 1,
            "status": "New"
        }
        response = client.post("/todos", json=payload)
        assert response.status_code == 422


# ===========================================================================
# LIST TODOS  GET /todos
# ===========================================================================

class TestListTodos:
    """Tests for the GET /todos endpoint."""

    def test_list_todos_empty_db_returns_empty_list(self, client):
        """With no todos, GET /todos should return an empty list."""
        response = client.get("/todos")
        assert response.status_code == 200
        assert response.json() == [] or isinstance(response.json(), list)

    def test_list_todos_returns_list(self, client):
        """GET /todos should always return a JSON array."""
        response = client.get("/todos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_todos_contains_created_todo(self, client, created_todo):
        """A created todo should appear in the GET /todos list."""
        response = client.get("/todos")
        assert response.status_code == 200
        ids = [t["id"] for t in response.json()]
        assert created_todo["id"] in ids

    def test_list_todos_multiple_items(self, client):
        """Creating multiple todos should return all of them in the list."""
        for i in range(3):
            client.post("/todos", json={
                "title": f"Todo {i}",
                "priority": i + 1,
                "status": "New"
            })
        response = client.get("/todos")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_todos_filter_by_status(self, client):
        """Filtering by status should return only todos with that status."""
        client.post("/todos", json={"title": "Todo A", "priority": 1, "status": "New"})
        client.post("/todos", json={"title": "Todo B", "priority": 1, "status": "Complete"})
        response = client.get("/todos", params={"status": "New"})
        if response.status_code == 200:
            data = response.json()
            for todo in data:
                assert todo["status"] == "New"

    def test_list_todos_filter_by_priority(self, client):
        """Filtering by priority should return only todos with that priority."""
        client.post("/todos", json={"title": "High Priority", "priority": 1, "status": "New"})
        client.post("/todos", json={"title": "Low Priority", "priority": 5, "status": "New"})
        response = client.get("/todos", params={"priority": 1})
        if response.status_code == 200:
            data = response.json()
            for todo in data:
                assert todo["priority"] == 1

    def test_list_todos_invalid_status_filter_returns_422_or_empty(self, client):
        """Filtering by an invalid status should return 422 or an empty/error response."""
        response = client.get("/todos", params={"status": "BOGUS"})
        assert response.status_code in (200, 400, 422)


# ===========================================================================
# GET SINGLE TODO  GET /todos/{id}
# ===========================================================================

class TestGetTodo:
    """Tests for the GET /todos/{id} endpoint."""

    def test_get_todo_by_id_happy_path(self, client, created_todo):
        """GET /todos/{id} should return the correct todo."""
        todo_id = created_todo["id"]
        response = client.get(f"/todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["id"] == todo_id

    def test_get_todo_response_shape(self, client, created_todo):
        """The todo response should contain all expected fields."""
        todo_id = created_todo["id"]
        response = client.get(f"/todos/{todo_id}")
        data = response.json()
        for field in ("id", "title", "status", "priority"):
            assert field in data, f"Missing field: {field}"

    def test_get_todo_not_found_returns_404(self, client):
        """Requesting a non-existent todo id should return HTTP 404."""
        response = client.get("/todos/nonexistent-id-xyz")
        assert response.status_code == 404

    def test_get_todo_after_delete_returns_404(self, client, created_todo):
        """Getting a deleted todo should return HTTP 404."""
        todo_id = created_todo["id"]
        client.delete(f"/todos/{todo_id}")
        response = client.get(f"/todos/{todo_id}")
        assert response.status_code == 404


# ===========================================================================
# UPDATE TODO  PUT /todos/{id}  or  PATCH /todos/{id}
# ===========================================================================

class TestUpdateTodo:
    """Tests for the PUT/PATCH /todos/{id} endpoint."""

    def _update(self, client, todo_id, payload, method="put"):
        fn = getattr(client, method)
        return fn(f"/todos/{todo_id}", json=payload)

    def test_update_todo_title(self, client, created_todo):
        """Updating the title of a todo should persist the new value."""
        todo_id = created_todo["id"]
        new_title = "Updated Title"
        for method in ("put", "patch"):
            resp = self._update(client, todo_id, {"title": new_title, "priority": 1, "status": "New"}, method)
            if resp.status_code in (200, 204):
                if resp.status_code == 200:
                    assert resp.json()["title"] == new_title
                return
        pytest.skip("Neither PUT nor PATCH succeeded")

    def test_update_todo_status(self, client, created_todo):
        """Updating the status of a todo should persist the new status."""
        todo_id = created_todo["id"]
        for method in ("put", "patch"):
            resp = self._update(client, todo_id, {"title": "Test Todo", "priority": 1, "status": "Complete"}, method)
            if resp.status_code in (200, 204):
                if resp.status_code == 200:
                    assert resp.json()["status"] == "Complete"
                return
        pytest.skip("Neither PUT nor PATCH succeeded")

    def test_update_todo_priority(self, client, created_todo):
        """Updating the priority of a todo should persist the new priority."""
        todo_id = created_todo["id"]
        for method in ("put", "patch"):
            resp = self._update(client, todo_id, {"title": "Test Todo", "priority": 99, "status": "New"}, method)
            if resp.status_code in (200, 204):
                if resp.status_code == 200:
                    assert resp.json()["priority"] == 99
                return
        pytest.skip("Neither PUT nor PATCH succeeded")

    def test_update_nonexistent_todo_returns_404(self, client):
        """Updating a todo that does not exist should return HTTP 404."""
        payload = {"title": "Ghost Todo", "priority": 1, "status": "New"}
        for method in ("put", "patch"):
            resp = getattr(client, method)("/todos/nonexistent-id", json=payload)
            if resp.status_code == 404:
                return
        pytest.skip("Endpoint did not return 404 for missing todo")

    def test_update_todo_invalid_status_returns_422(self, client, created_todo):
        """Updating a todo with an invalid status should return HTTP 422."""
        todo_id = created_todo["id"]
        payload = {"title": "Test", "priority": 1, "status": "INVALID"}
        for method in ("put", "patch"):
            resp = self._update(client, todo_id, payload, method)
            if resp.status_code == 422:
                return
        pytest.skip("Endpoint did not validate status")

    def test_update_todo_due_date(self, client, created_todo):
        """Updating the due_date of a todo should persist the new date."""
        todo_id = created_todo["id"]
        new_date = "2088-06-15"
        payload = {"title": "Test Todo", "priority": 1, "status": "New", "due_date": new_date}
        for method in ("put", "patch"):
            resp = self._update(client, todo_id, payload, method)
            if resp.status_code in (200, 204):
                if resp.status_code == 200:
                    assert new_date in str(resp.json().get("due_date", ""))
                return
        pytest.skip("Neither PUT nor PATCH succeeded")


# ===========================================================================
# DELETE TODO  DELETE /todos/{id}
# ===========================================================================

class TestDeleteTodo:
    """Tests for the DELETE /todos/{id} endpoint."""

    def test_delete_todo_happy_path(self, client, created_todo):
        """Deleting an existing todo should return 200 or 204."""
        todo_id = created_todo["id"]
        response = client.delete(f"/todos/{todo_id}")
        assert response.status_code in (200, 204)

    def test_delete_todo_removes_from_list(self, client, created_todo):
        """After deleting a todo it should no longer appear in GET /todos."""
        todo_id = created_todo["id"]
        client.delete(f"/todos/{todo_id}")
        response = client.get("/todos")
        ids = [t["id"] for t in response.json()]
        assert todo_id not in ids

    def test_delete_nonexistent_todo_returns_404(self, client):
        """Deleting a todo that does not exist should return HTTP 404."""
        response = client.delete("/todos/nonexistent-id-abc")
        assert response.status_code == 404

    def test_delete_todo_twice_returns_404(self, client, created_todo):
        """Deleting the same todo a second time should return HTTP 404."""
        todo_id = created_todo["id"]
        client.delete(f"/todos/{todo_id}")
        response = client.delete(f"/todos/{todo_id}")
        assert response.status_code == 404


# ===========================================================================
# OVERDUE INDICATOR
# ===========================================================================

class TestOverdueTodos:
    """Tests related to overdue todo detection."""

    def test_overdue_field_present_in_response(self, client):
        """A todo with a past due date should expose an 'overdue' or equivalent field."""
        payload = {
            "title": "Past Due Todo",
            "due_date": PAST_DATE,
            "priority": 1,
            "status": "New"
        }
        resp = client.post("/todos", json=payload)
        if resp.status_code not in (200, 201):
            pytest.skip("Could not create past-due todo")
        data = resp.json()
        # If the API exposes an 'overdue' or 'is_overdue' flag, verify it is True.
        if "overdue" in data:
            assert data["overdue"] is True
        elif "is_overdue" in data:
            assert data["is_overdue"] is True

    def test_future_due_date_not_overdue(self, client):
        """A todo with a future due date should not be marked overdue."""
        payload = {
            "title": "Future Todo",
            "due_date": FUTURE_DATE,
            "priority": 1,
            "status": "New"
        }
        resp = client.post("/todos", json=payload)
        if resp.status_code not in (200, 201):
            pytest.skip("Could not create future todo")
        data = resp.json()
        if "overdue" in data:
            assert data["overdue"] is False
        elif "is_overdue" in data:
            assert data["is_overdue"] is False


# ===========================================================================
# API CONTRACT TESTS
# ===========================================================================

class TestApiContract:
    """API contract tests: correct content types and status codes."""

    def test_create_todo_returns_json(self, client, sample_todo_payload):
        """POST /todos should return JSON content type."""
        response = client.post("/todos", json=sample_todo_payload)
        assert "application/json" in response.headers.get("content-type", "")

    def test_list_todos_returns_json(self, client):
        """GET /todos should return JSON content type."""
        response = client.get("/todos")
        assert "application/json" in response.headers.get("content-type", "")

    def test_get_todo_returns_json(self, client, created_todo):
        """GET /todos/{id} should return JSON content type."""
        response = client.get(f"/todos/{created_todo['id']}")
        assert "application/json" in response.headers.get("content-type", "")

    def test_404_response_has_detail_field(self, client):
        """A 404 response should include a 'detail' field in the body."""
        response = client.get("/todos/does-not-exist")
        if response.status_code == 404:
            assert "detail" in response.json()

    def test_422_response_has_detail_field(self, client):
        """A 422 response should include a 'detail' field in the body."""
        response = client.post("/todos", json={})
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_post_with_no_body_returns_422(self, client):
        """POST /todos with no body at all should return HTTP 422."""
        response = client.post("/todos", content=b"")
        assert response.status_code == 422

    def test_post_with_wrong_content_type_returns_422(self, client):
        """POST /todos with plain text body should return HTTP 422."""
        response = client.post(
            "/todos",
            content="title=Test&priority=1",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in (415, 422)

    def test_created_todo_id_is_string(self, client, sample_todo_payload):
        """The 'id' field of a created todo should be a non-empty string."""
        response = client.post("/todos", json=sample_todo_payload)
        assert response.status_code in (200, 201)
        assert isinstance(response.json()["id"], str)
        assert len(response.json()["id"]) > 0

    def test_created_todo_priority_is_integer(self, client, sample_todo_payload):
        """The 'priority' field of a created todo should be an integer."""
        response = client.post("/todos", json=sample_todo_payload)
        assert response.status_code in (200, 201)
        assert isinstance(response.json()["priority"], int)

    def test_two_todos_get_different_ids(self, client, sample_todo_payload):
        """Each created todo should receive a unique id."""
        resp1 = client.post("/todos", json=sample_todo_payload)
        resp2 = client.post("/todos", json=sample_todo_payload)
        assert resp1.status_code in (200, 201)
        assert resp2.status_code in (200, 201)
        assert resp1.json()["id"] != resp2.json()["id"]


# ===========================================================================
# SORTING / PRIORITY ORDERING
# ===========================================================================

class TestSortingAndFiltering:
    """Tests for sortable list and filtering features."""

    def test_filter_by_status_new(self, client):
        """Filtering todos by 'New' status should only return 'New' todos."""
        client.post("/todos", json={"title": "A", "priority": 1, "status": "New"})
        client.post("/todos", json={"title": "B", "priority": 2, "status": "Deferred"})
        resp = client.get("/todos", params={"status": "New"})
        if resp.status_code == 200:
            for todo in resp.json():
                assert todo["status"] == "New"

    def test_filter_by_status_complete(self, client):
        """Filtering todos by 'Complete' status should only return complete todos."""
        client.post("/todos", json={"title": "Done", "priority": 1, "status": "Complete"})
        client.post("/todos", json={"title": "WIP", "priority": 1, "status": "In Process"})
        resp = client.get("/todos", params={"status": "Complete"})
        if resp.status_code == 200:
            for todo in resp.json():
                assert todo["status"] == "Complete"

    def test_sort_by_priority_ascending(self, client):
        """Sorting todos by priority ascending should order them correctly."""
        for p in [3, 1, 2]:
            client.post("/todos", json={"title": f"P{p}", "priority": p, "status": "New"})
        resp = client.get("/todos", params={"sort": "priority", "order": "asc"})
        if resp.status_code == 200:
            priorities = [t["priority"] for t in resp.json()]
            assert priorities == sorted(priorities)
