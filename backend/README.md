# Web Builder Backend

A Python FastAPI backend for creating and managing HTML, CSS, and JavaScript projects - similar to Bolt.new.

## Features

- 🔐 JWT-based user authentication (register/login)
- 📁 Project management (create, read, update, delete)
- 💾 File management (save/update HTML, CSS, JS files)
- 👁️ Live preview of projects
- 🗄️ SQLite database (can switch to PostgreSQL)

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (can be switched to PostgreSQL)
- **Authentication**: JWT (JSON Web Tokens)
- **Python**: 3.11+

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY`: A random secret key for JWT signing
- `DATABASE_URL`: Database connection string (default: SQLite)
- `PROJECTS_DIR`: Directory to store project files (default: `./projects`)

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login (form data)
- `POST /auth/login-json` - Login (JSON body)

### Projects

- `POST /projects` - Create a new project
- `GET /projects` - List all user's projects
- `GET /projects/{id}` - Get project details
- `PATCH /projects/{id}` - Update project metadata
- `DELETE /projects/{id}` - Delete a project

### Files

- `GET /projects/{id}/files` - Get all project files (HTML, CSS, JS)
- `GET /projects/{id}/files/{filename}` - Get a specific file
- `PUT /projects/{id}/files/{filename}` - Update a file (HTML, CSS, or JS)

### Preview

- `GET /projects/{id}/preview` - Live preview of the project

## Example Usage

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create a Project

```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Portfolio",
    "description": "A personal portfolio website"
  }'
```

### 4. Update HTML File

```bash
curl -X PUT "http://localhost:8000/projects/{project_id}/files/index.html" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "<h1>Hello World</h1>"
  }'
```

### 5. Update CSS File

```bash
curl -X PUT "http://localhost:8000/projects/{project_id}/files/style.css" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "body { background: #f0f0f0; }"
  }'
```

### 6. Update JS File

```bash
curl -X PUT "http://localhost:8000/projects/{project_id}/files/script.js" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "console.log(\"Hello World\");"
  }'
```

### 7. View Project Preview

Open in browser:
```
http://localhost:8000/projects/{project_id}/preview
```

### 8. Get All Files

```bash
curl -X GET "http://localhost:8000/projects/{project_id}/files" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── file_handler.py      # File management
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Auth endpoints
│       └── projects.py      # Project endpoints
├── projects/                # Generated project files (created at runtime)
├── .env.example
├── requirements.txt
└── README.md
```

## File Structure

Each project has its own folder with three files:

```
projects/
└── {project_id}/
    ├── index.html
    ├── style.css
    └── script.js
```

## Database

The application uses SQLite by default. To switch to PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

2. Install PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```

## Notes

- Project files are stored in the `projects/` directory
- Each project has its own folder: `projects/{project_id}/`
- Files are: `index.html`, `style.css`, `script.js`
- The preview endpoint combines all files into a single HTML document
- All file operations require authentication

## Production Considerations

- Change `SECRET_KEY` to a strong random value
- Set `allow_origins` in CORS middleware to specific domains
- Use environment variables for all sensitive data
- Consider using PostgreSQL for production
- Add rate limiting for API endpoints
- Implement proper error logging
- Add database migrations (Alembic)
- Set up file backup strategy

