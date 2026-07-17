"""CodeCraftHub: a beginner-friendly Flask REST API using JSON storage."""

import json
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request


app = Flask(__name__)

# Store courses.json beside app.py, even if the app is started from another folder.
DATA_FILE = Path(__file__).resolve().parent / "courses.json"
REQUIRED_FIELDS = ("name", "description", "target_date", "status")
VALID_STATUSES = {"Not Started", "In Progress", "Completed"}


# ---------- JSON file helpers ----------

def initialize_data_file():
    """Create courses.json containing an empty JSON list when it is missing."""
    if not DATA_FILE.exists():
        try:
            DATA_FILE.write_text("[]\n", encoding="utf-8")
        except OSError as error:
            raise OSError(f"Could not create the data file: {error}") from error


def load_courses():
    """Load and return the list of courses stored in courses.json."""
    initialize_data_file()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            courses = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise OSError(f"Could not read the data file: {error}") from error

    # The top-level JSON value must be a list because all routes expect a list.
    if not isinstance(courses, list):
        raise OSError("Could not read the data file: expected a JSON list")
    return courses


def save_courses(courses):
    """Replace the JSON file contents with the supplied course list."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(courses, file, indent=2)
            file.write("\n")
    except (OSError, TypeError) as error:
        raise OSError(f"Could not write to the data file: {error}") from error


def find_course(courses, course_id):
    """Return the course with course_id, or None when it does not exist."""
    return next((course for course in courses if course.get("id") == course_id), None)


def get_next_id(courses):
    """Generate 1 for the first course, then one more than the largest ID."""
    existing_ids = [course.get("id", 0) for course in courses]
    return max(existing_ids, default=0) + 1


# ---------- Request validation ----------

def validate_course_data(data):
    """Return an error message for invalid input, or None for valid input."""
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"

    # Required text fields should not accept empty strings or whitespace only.
    for field in ("name", "description", "target_date", "status"):
        if not isinstance(data[field], str) or not data[field].strip():
            return f"'{field}' must be a non-empty string"

    if data["status"] not in VALID_STATUSES:
        allowed = ", ".join(sorted(VALID_STATUSES))
        return f"Invalid status. Allowed values: {allowed}"

    try:
        # strptime rejects impossible dates as well as incorrectly formatted ones.
        datetime.strptime(data["target_date"], "%Y-%m-%d")
    except ValueError:
        return "Invalid target_date. Use YYYY-MM-DD format"

    return None


def get_json_body():
    """Read a JSON request body without letting Flask return an HTML error page."""
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Request body must contain valid JSON"}), 400)
    return data, None


def storage_error_response(error):
    """Use one consistent response when courses.json cannot be read or written."""
    return jsonify({"error": "File storage error", "details": str(error)}), 500


# ---------- REST API routes ----------

@app.post("/api/courses")
def create_course():
    """Add a course and return it with HTTP status 201 Created."""
    data, error_response = get_json_body()
    if error_response:
        return error_response

    validation_error = validate_course_data(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        courses = load_courses()
        course = {
            "id": get_next_id(courses),
            "name": data["name"].strip(),
            "description": data["description"].strip(),
            "target_date": data["target_date"],
            "status": data["status"],
            # UTC makes the timestamp unambiguous for API clients.
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        courses.append(course)
        save_courses(courses)
    except OSError as error:
        return storage_error_response(error)

    return jsonify(course), 201


@app.get("/api/courses")
def get_courses():
    """Return every saved course."""
    try:
        return jsonify(load_courses()), 200
    except OSError as error:
        return storage_error_response(error)


@app.get("/api/courses/stats")
def get_course_stats():
    """Return the total courses and a count for each supported status."""
    try:
        courses = load_courses()
    except OSError as error:
        return storage_error_response(error)

    # Begin every valid status at zero so the response is predictable even
    # when no courses exist for one or more statuses.
    courses_by_status = {
        "Not Started": 0,
        "In Progress": 0,
        "Completed": 0,
    }

    for course in courses:
        status = course.get("status")
        if status in courses_by_status:
            courses_by_status[status] += 1

    return jsonify({
        "total_courses": len(courses),
        "courses_by_status": courses_by_status,
    }), 200


@app.get("/api/courses/<int:course_id>")
def get_course(course_id):
    """Return one course selected by its numeric ID."""
    try:
        course = find_course(load_courses(), course_id)
    except OSError as error:
        return storage_error_response(error)

    if course is None:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(course), 200


@app.put("/api/courses/<int:course_id>")
def update_course(course_id):
    """Update all editable fields while keeping ID and created_at unchanged."""
    data, error_response = get_json_body()
    if error_response:
        return error_response

    validation_error = validate_course_data(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        courses = load_courses()
        course = find_course(courses, course_id)
        if course is None:
            return jsonify({"error": "Course not found"}), 404

        course.update({
            "name": data["name"].strip(),
            "description": data["description"].strip(),
            "target_date": data["target_date"],
            "status": data["status"],
        })
        save_courses(courses)
    except OSError as error:
        return storage_error_response(error)

    return jsonify(course), 200


@app.delete("/api/courses/<int:course_id>")
def delete_course(course_id):
    """Delete one course selected by its numeric ID."""
    try:
        courses = load_courses()
        course = find_course(courses, course_id)
        if course is None:
            return jsonify({"error": "Course not found"}), 404

        courses.remove(course)
        save_courses(courses)
    except OSError as error:
        return storage_error_response(error)

    return jsonify({"message": "Course deleted successfully"}), 200


# Create courses.json during startup rather than waiting for the first request.
# A startup failure is printed; API routes will still return a clear 500 response.
try:
    initialize_data_file()
except OSError as startup_error:
    print(f"Warning: {startup_error}")


if __name__ == "__main__":
    # Debug mode is convenient while learning. Do not use it in production.
    app.run(debug=True)
