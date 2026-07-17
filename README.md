# CodeCraftHub

CodeCraftHub is a small learning project for developers who want to track the
courses they plan to study. It provides a REST API built with Python and Flask.
Course data is saved in a plain JSON file, so no database, login, or user account
setup is required.

The project is intentionally simple. Its purpose is to demonstrate how an HTTP
request reaches a Flask route, how an API validates JSON data, and how it returns
JSON responses with meaningful HTTP status codes.

## Features

- Create, read, update, and delete courses (CRUD)
- Automatically generate numeric course IDs starting at `1`
- Automatically record a UTC creation timestamp
- Validate required fields and target dates
- Restrict course status to three supported values
- Return helpful JSON error messages
- Store all data in `courses.json`
- Automatically create `courses.json` when it does not exist
- Use no database, authentication, or user management

## What a course looks like

Each course contains:

| Field | Description | Example |
|---|---|---|
| `id` | Automatically generated numeric identifier | `1` |
| `name` | Required course name | `Flask Fundamentals` |
| `description` | Required explanation of the course | `Learn REST APIs with Flask.` |
| `target_date` | Required date in `YYYY-MM-DD` format | `2026-08-31` |
| `status` | Required learning status | `Not Started` |
| `created_at` | Automatically generated UTC timestamp | `2026-07-17T20:00:00+00:00` |

The only valid status values are:

- `Not Started`
- `In Progress`
- `Completed`

Status values are case-sensitive.

## Project structure

```text
codecrafthub/
├── app.py            # Flask application, API routes, validation, and file helpers
├── courses.json      # Course data; created automatically when the app starts
├── requirements.txt  # Python packages needed by the project
├── README.md         # Project documentation
├── data/             # Currently unused; kept for possible future organization
└── storage.py        # Currently unused; file helpers could be moved here later
```

For a first REST API, keeping the working code in `app.py` makes the complete
request flow easy to follow. As the project grows, file-storage functions could
be moved into `storage.py` and tests could be placed in a separate `tests/`
folder.

## Installation

### Prerequisites

Install the following before continuing:

- Python 3.9 or newer
- A terminal such as PowerShell
- A text editor such as Visual Studio Code

Check that Python is available:

```powershell
python --version
```

### Windows PowerShell setup

1. Open PowerShell and enter the project directory:

   ```powershell
   cd C:\Users\welld\Downloads\codecrafthub
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv venv
   ```

3. Activate the virtual environment:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   The terminal prompt should now begin with `(venv)`.

4. Install the required packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Confirm that Flask is installed:

   ```powershell
   python -m flask --version
   ```

If PowerShell blocks activation, see [Troubleshooting](#troubleshooting).

### macOS or Linux setup

```bash
cd path/to/codecrafthub
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Running the application

With the virtual environment active, run:

```powershell
python app.py
```

Flask should display an address similar to:

```text
Running on http://127.0.0.1:5000
```

Leave this terminal running. Open a second PowerShell terminal for API requests.
The development server reloads when `app.py` changes because debug mode is
enabled.

To stop the server, return to its terminal and press `Ctrl+C`.

## REST API concepts

An endpoint combines an HTTP method and URL. The HTTP method communicates the
operation:

- `POST` creates data.
- `GET` reads data.
- `PUT` replaces the editable data for an existing item.
- `DELETE` removes data.

The base address used in the examples is:

```text
http://127.0.0.1:5000
```

### Endpoint summary

| Method | Endpoint | Purpose | Success status |
|---|---|---|---|
| `POST` | `/api/courses` | Create a course | `201 Created` |
| `GET` | `/api/courses` | Get every course | `200 OK` |
| `GET` | `/api/courses/stats` | Get course totals by status | `200 OK` |
| `GET` | `/api/courses/<course_id>` | Get one course | `200 OK` |
| `PUT` | `/api/courses/<course_id>` | Update one course | `200 OK` |
| `DELETE` | `/api/courses/<course_id>` | Delete one course | `200 OK` |

In a URL such as `/api/courses/1`, the number `1` is the course ID.

## API examples

These examples use `curl.exe`, which avoids PowerShell's older `curl` alias.
PowerShell single-quoted JSON does **not** need backslashes before double quotes.

### Create a course

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/courses `
  -H "Content-Type: application/json" `
  -d '{"name":"Flask Fundamentals","description":"Learn how to create REST APIs with Flask.","target_date":"2026-08-31","status":"Not Started"}'
```

Example `201 Created` response:

```json
{
  "created_at": "2026-07-17T20:00:00.000000+00:00",
  "description": "Learn how to create REST APIs with Flask.",
  "id": 1,
  "name": "Flask Fundamentals",
  "status": "Not Started",
  "target_date": "2026-08-31"
}
```

The exact `created_at` value will be different because the server generates it
at request time.

### Get all courses

```powershell
curl.exe -i http://127.0.0.1:5000/api/courses
```

Example `200 OK` response:

```json
[
  {
    "created_at": "2026-07-17T20:00:00.000000+00:00",
    "description": "Learn how to create REST APIs with Flask.",
    "id": 1,
    "name": "Flask Fundamentals",
    "status": "Not Started",
    "target_date": "2026-08-31"
  }
]
```

An empty course list is returned as `[]`.

### Get course statistics

```powershell
curl.exe -i http://127.0.0.1:5000/api/courses/stats
```

Example `200 OK` response:

```json
{
  "courses_by_status": {
    "Completed": 1,
    "In Progress": 2,
    "Not Started": 3
  },
  "total_courses": 6
}
```

Each supported status appears in the response even when its count is zero.

### Get a specific course

```powershell
curl.exe -i http://127.0.0.1:5000/api/courses/1
```

The API returns the course with ID `1`, or `404 Not Found` if it does not exist.

### Update a course

`PUT` requires all four editable fields, even if only one value is changing.
The original `id` and `created_at` remain unchanged.

```powershell
curl.exe -i -X PUT http://127.0.0.1:5000/api/courses/1 `
  -H "Content-Type: application/json" `
  -d '{"name":"Flask Fundamentals","description":"Learn how to create and test REST APIs with Flask.","target_date":"2026-09-15","status":"In Progress"}'
```

Example `200 OK` response:

```json
{
  "created_at": "2026-07-17T20:00:00.000000+00:00",
  "description": "Learn how to create and test REST APIs with Flask.",
  "id": 1,
  "name": "Flask Fundamentals",
  "status": "In Progress",
  "target_date": "2026-09-15"
}
```

### Delete a course

```powershell
curl.exe -i -X DELETE http://127.0.0.1:5000/api/courses/1
```

Example `200 OK` response:

```json
{
  "message": "Course deleted successfully"
}
```

## Testing the API manually

For a predictable test, first make sure `courses.json` contains:

```json
[]
```

Do not edit that file while the API is processing a request. Then run these
tests in order:

1. Start the Flask server with `python app.py`.
2. Send the `POST` example and expect `201 Created` with ID `1`.
3. Send `GET /api/courses` and expect a list containing the course.
4. Send `GET /api/courses/1` and expect that course.
5. Send the `PUT` example and expect the new status and target date.
6. Send the `DELETE` example and expect a success message.
7. Send `GET /api/courses/1` again and expect `404 Not Found`.

The `-i` curl option includes HTTP response headers, making status codes visible.

### Missing-field test

This request deliberately omits `description`:

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/courses `
  -H "Content-Type: application/json" `
  -d '{"name":"Python Basics","target_date":"2026-10-01","status":"Not Started"}'
```

Expected `400 Bad Request` response:

```json
{
  "error": "Missing required fields: description"
}
```

### Invalid-status test

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/courses `
  -H "Content-Type: application/json" `
  -d '{"name":"Python Basics","description":"Learn Python syntax.","target_date":"2026-10-01","status":"Almost Finished"}'
```

Expected `400 Bad Request` response:

```json
{
  "error": "Invalid status. Allowed values: Completed, In Progress, Not Started"
}
```

### Invalid-date test

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/courses `
  -H "Content-Type: application/json" `
  -d '{"name":"Python Basics","description":"Learn Python syntax.","target_date":"10/01/2026","status":"Not Started"}'
```

Expected `400 Bad Request` response:

```json
{
  "error": "Invalid target_date. Use YYYY-MM-DD format"
}
```

### Course-not-found test

```powershell
curl.exe -i http://127.0.0.1:5000/api/courses/999
```

Expected `404 Not Found` response:

```json
{
  "error": "Course not found"
}
```

## HTTP status codes used

| Status | Meaning in this API |
|---|---|
| `200 OK` | A read, update, or delete operation succeeded |
| `201 Created` | A new course was successfully created |
| `400 Bad Request` | The submitted JSON or course data was invalid |
| `404 Not Found` | No course exists with the requested ID |
| `500 Internal Server Error` | The JSON data file could not be read or written |

## How JSON file storage works

When a request arrives, the application follows this basic flow:

```text
Client request
    -> Flask route
    -> Validate request data
    -> Read courses.json
    -> Create, find, update, or delete a course
    -> Write courses.json when data changed
    -> Return a JSON response
```

JSON storage is useful for learning and small single-user projects. It is not a
replacement for a database in a production application because simultaneous
writes can conflict and searching large files becomes inefficient.

## Troubleshooting

### `python` is not recognized

Python is either not installed or not on the system `PATH`. Install Python and
enable the installer option named **Add Python to PATH**. On Windows, the `py`
command may also work:

```powershell
py --version
py -m venv venv
```

### PowerShell blocks virtual-environment activation

If activation reports that scripts are disabled, allow local scripts for your
Windows account:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Alternatively, skip activation and call the environment's Python directly:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe app.py
```

### `ModuleNotFoundError: No module named 'flask'`

Activate the virtual environment and install the dependencies:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### `Request body must contain valid JSON`

Make sure the request includes the JSON content-type header and valid JSON:

```powershell
-H "Content-Type: application/json"
```

In PowerShell, this is correct:

```powershell
-d '{"name":"Example"}'
```

Do not add backslashes before the JSON quotation marks. For example,
`'{\"name\":\"Example\"}'` sends unwanted backslashes and is invalid JSON.

For large payloads, save the JSON in `new-course.json` and send the file:

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/api/courses `
  -H "Content-Type: application/json" `
  --data-binary "@new-course.json"
```

### The API returns `404 Not Found`

Check that:

- The URL begins with `/api/courses`.
- A numeric ID is used, such as `/api/courses/1`.
- The requested course has already been created and not deleted.

Use this request to see all existing IDs:

```powershell
curl.exe http://127.0.0.1:5000/api/courses
```

### Port 5000 is already in use

Stop the other server using port `5000`, or temporarily change the last line in
`app.py` to:

```python
app.run(debug=True, port=5001)
```

Then use `http://127.0.0.1:5001` in API requests.

### The API reports a file-storage error

Confirm that the project directory is writable and `courses.json` contains a
valid JSON list. An empty valid file should contain:

```json
[]
```

An empty file is not valid JSON. If the file contains important course data,
make a backup before editing it.

### Changes seem to disappear

Course data is stored in `courses.json`, not in Python memory. Confirm that you
are running the `app.py` from this project directory and inspecting the
`courses.json` beside it. Deleting or replacing that file removes the stored
courses.

## Learning ideas

After understanding this version, useful next steps include:

- Add automated tests with `pytest` and Flask's test client.
- Add a `PATCH` endpoint for partial updates.
- Filter courses by status.
- Move JSON helpers into `storage.py`.
- Add request logging.
- Replace the JSON file with SQLite to learn database basics.

The current JSON approach is intentionally limited so the REST concepts remain
visible and approachable.
