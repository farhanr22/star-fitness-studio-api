# Fitness Studio Booking API

A robust API for a fitness studio, built with Python, FastAPI, and SQLAlchemy - providing a complete backend solution for user authentication, class management, and a concurrency-safe booking system.


### Table of Contents
- [1. Project Overview](#1-project-overview)
- [2. Technical Decisions & Assumptions](#2-technical-decisions--assumptions)
- [3. Installation & Setup](#3-installation--setup)
- [4. API Usage Guide](#4-api-usage-guide)

---

## 1. Project Overview

This API serves as the backend for a fictional fitness studio, enabling users to sign up, log in, create/view upcoming classes, and create/view bookings. 

The project is built with a focus on robustness, including a modular architecture, request validation (with Pydantic), consistent error handling and comprehensive logging.

### Features

- ✅ **User Authentication (JWT + dual-tokens):** Sign up and log in via a JWT-based system, with separate acces and refresh tokens that are rotated regularly.
- ✅ **Class Management and Listing:** Authenticated users can create class and view a list of upcoming fitness classes.
- ✅ **Booking System:** Users can book slots in classes and view their bookings. Atomic database transactions are used to prevent overbooking.
- ✅ **Structured Error Handling:** A consistent error response schema provides a predictable experience for API clients 
- ✅ **Comprehensive Integration Tests:** A full test suite using Pytest, verifying major operations of each module.
- ✅ **Containerized Deployment:** Dockerized for easy setup and deployment.
- ✅ **Comprehensive Logging:** All major operations and any errors are logged to `stdout` with appropriate log levels.
- ✅ **Database Seeding:** A `seed.py` script is included to populate the database with sample users, classes, and bookings, allowing for quick exploration of the API.

### Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** SQLite, using SQLAlchemy
- **Testing:** pytest
- **Containerization:** Docker & Docker Compose

### API Overview

| Method | Route        | Description                                | Auth? |
| :----- | :----------- | :----------------------------------------- | :---- |
| `POST` | `/signup`    | Registers a new user.                      |    No |
| `POST` | `/login`     | Authenticates a user and returns JWTs.     |    No |
| `POST` | `/refresh`   | Return new access/refresh tokens.          |    No |
| `POST` | `/classes`   | Creates a new fitness class.               |   Yes |
| `GET`  | `/classes`   | Fetches all upcoming fitness classes.      |   Yes |
| `POST` | `/book`      | Books a slot in a specific class.          |   Yes |
| `GET`  | `/bookings`  | Fetches all bookings for the current user. |   Yes |

---

## 2. Technical Decisions & Assumptions

- **Architecture: _Vertical Slice_**  
    The application is organized into modules (`auth`, `classes`, and `bookings`) which are self-contained (with their own API routes, DB models, request/response schemas, etc) and expose only necessary functions or objects.

- **Atomic Updates using Database Lock**  
    To prevent overbooking, the booking process uses a lock (`SELECT ... FOR UPDATE` or `.with_for_update()` in SQLAlchemy) within a database transaction to ensure that the slot availability check and the decrement operation are atomic. This maintains data integrity during concurrent access.

- **Auth with email/password login and rotating tokens**  
    Users log in with email and password to receive both an access token (short-lived) and a refresh token (longer-lived). The access token is sent in the `Authorization` header for protected requests. When it expires, a new access token can be obtained by sending the refresh token to the `/refresh` endpoint, allowing continued access without re-entering credentials.

- **Timezone Management - IST Storage and UTC API**  
    As per the requirements, all class datetimes are stored as timezone-aware timestamps in IST. The API, however, accepts and returns all datetimes in the standard UTC ISO 8601 format with a "Z" suffix.

- **Errors with Consistent Response Schema**  
    All API error responses, whether from input validation/authentication/business logicor/unhandled server errors, return a consistent JSON structure: `{"errors": [...]}`. This is achieved using custom exception handlers and middleware, providing a predictable experience for client applications.

- **Assumptions Made**  
    - The API requires a user to sign up and then perform a separate login request to receive their tokens.  
    - While the booking endpoint accepts a `client_name` and `client_email`, the booking is always tied to the authenticated user's ID to a single user from booking the same class multiple times.  
    - The combination of Instructor name and class time must be unique for each class.  
    - No class creation or booking is allowed in the past.

## 3. Installation & Setup

*The below instructions assume a Linux system.*

<details>
<summary><strong>Option 1: Using Docker (Recommended)</strong></summary>

**Prerequisites:** Docker and Docker Compose installed.

**1. Clone the repository:**
```bash
git clone https://github.com/farhanr22/star-fitness-studio-api.git
cd star-fitness-studio-api
```

**2. Create the environment file:**
Copy the example environment file. The default values are sufficient.
```bash
cp .env.example .env
```

**3. Build and Run the Container:**
```bash
docker compose up --build
```
The API will be available at `http://localhost:8000`.

**4. Seed the Database (Optional):**
To populate the database with sample data and receive login credentials, run the following command in a new terminal:
```bash
docker compose exec api python seed.py
```

**5. Run Tests (Optional):**
```bash
docker compose exec api pytest
```
</details>

<details>
<summary><strong>Option 2: Using a Local Virtual Environment</strong></summary>

**Prerequisites:** Python 3.11+ and `venv` installed.

**1. Clone the repository and navigate into it:**
```bash
git clone https://github.com/farhanr22/star-fitness-studio-api.git
cd star-fitness-studio-api
```

**2. Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Create the environment file:**
```bash
cp .env.example .env
```

**5. Run the Server:**
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

**6. Seed the Database (Optional):**
In a new terminal (with the venv activated), run:
```bash
python seed.py
```

**7. Run Tests (Optional):**
```bash
pytest
```
</details>

---

## 4. API Usage Guide

<details>
<summary><strong>Interactive API Docs (Swagger UI)</strong></summary>

Once the server is running, you can access the interactive Swagger UI documentation at **[http://localhost:8000/docs](http://localhost:8000/docs)**. 

You can  explore and test each API route by expanding it in the Swagger UI, clicking the "Try it out" button, customizing the request body as needed, and then clicking "Execute" to see the response below.

To use the protected endpoints:
1. Execute a request to `POST /login` with valid credentials (e.g., from the seed script, or after making a successful `POST` request to `/signup`).
2. Copy the `access_token` from the response body.
3. Click the "Authorize" button at the top right of the page.
4. In the popup, paste the token into the value field and click the "Authorize" button.
5. You can now execute any of the locked endpoints.

</details>

<details>
<summary><strong>cURL Workflow</strong></summary>

**1. Sign Up as a New User:**
```bash
curl -X POST "http://localhost:8000/signup" \
-H "Content-Type: application/json" \
-d '{
  "name": "CURL User",
  "email": "curl.user@example.com",
  "password": "password123"
}'
```
*You may skip this step by using the credentials from running `seed.py`.*

**2. Log In & Capture Tokens:**
```bash
curl -X POST "http://localhost:8000/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "curl.user@example.com",
  "password": "password123"
}'
```

From the response body, copy the `access_token`. Then, set them as variables in your terminal:

```bash
export ACCESS_TOKEN="paste_access_token_here"
```

**3. Create a New Class:**
```bash
curl -X POST "http://localhost:8000/classes" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $ACCESS_TOKEN" \
-d '{
  "name": "Evening Stretch",
  "instructor": "CURL Teacher",
  "dateTime": "2030-12-25T19:00:00Z",
  "availableSlots": 25
}'
```

**4. Book the Class:**
*Note the `id` from the previous response and use it as the `class_id`.*
```bash
curl -X POST "http://localhost:8000/book" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $ACCESS_TOKEN" \
-d '{
  "class_id": 5,
  "client_name": "CURL Booker",
  "client_email": "curl.user@example.com"
}'
```

**5. View Your Bookings:**
```bash
curl -X GET "http://localhost:8000/bookings" \
-H "Authorization: Bearer $ACCESS_TOKEN"
```

</details>


## License

This project is licensed under the [MIT License](LICENSE).