"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import json
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

USERS_FILE = current_dir / "users.json"


def load_users():
    if not USERS_FILE.exists():
        USERS_FILE.write_text("[]", encoding="utf-8")
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def find_user_by_email(email: str) -> Optional[dict]:
    users = load_users()
    for user in users:
        if user["email"].lower() == email.lower():
            return user
    return None


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/auth/me")
def auth_me(request: Request):
    email = request.cookies.get("user_email")
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = find_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "email": user["email"],
        "name": user["name"],
        "branch": user["branch"],
    }


@app.post("/auth/login")
def auth_login(email: str = Form(...), password: str = Form(...), branch: str = Form(...)):
    user = find_user_by_email(email)
    if not user or user["password"] != password or user["branch"] != branch:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    response = JSONResponse({"message": "Login successful"})
    response.set_cookie("user_email", user["email"], httponly=True, samesite="lax")
    return response


@app.post("/auth/signup")
def auth_signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    branch: str = Form(...),
):
    if find_user_by_email(email):
        raise HTTPException(status_code=400, detail="A user with that email already exists")

    users = load_users()
    users.append({
        "name": name,
        "email": email,
        "password": password,
        "branch": branch,
    })
    save_users(users)
    return {"message": "Signup successful"}


@app.post("/auth/logout")
def auth_logout():
    response = JSONResponse({"message": "Logout successful"})
    response.delete_cookie("user_email")
    return response


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
