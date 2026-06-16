from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


class TestApp:
    def setup_method(self):
        reset_activities()

    def test_root_redirects_to_index(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities_returns_all_activities(self):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert data["Chess Club"]["max_participants"] == 12
        assert data["Gym Class"]["participants"] == ["john@mergington.edu", "olivia@mergington.edu"]

    def test_signup_for_activity_success(self):
        response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})
        assert response.status_code == 200
        assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_for_activity_not_found(self):
        response = client.post("/activities/Bad Club/signup", params={"email": "student@mergington.edu"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_for_activity_already_registered(self):
        response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_unregister_from_activity_success(self):
        response = client.delete("/activities/Chess Club/unregister", params={"email": "michael@mergington.edu"})
        assert response.status_code == 200
        assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_from_activity_not_found(self):
        response = client.delete("/activities/Bad Club/unregister", params={"email": "student@mergington.edu"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_from_activity_not_registered(self):
        response = client.delete("/activities/Chess Club/unregister", params={"email": "unknown@mergington.edu"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"
