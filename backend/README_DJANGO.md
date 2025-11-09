# Django Backend Setup

This is the Django version of the Web Builder backend API.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `backend` directory with:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///./app.db
   PROJECTS_DIR=./projects
   GROQ_API_KEY=your-groq-api-key
   OPENAI_API_KEY=your-openai-api-key
   OLLAMA_BASE_URL=http://localhost:11434
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

All endpoints match the FastAPI version:

- `GET /health/` - Health check
- `POST /projects` - Create project
- `GET /projects/` - List projects
- `GET /projects/<project_id>/` - Get project
- `PATCH /projects/<project_id>/update/` - Update project
- `DELETE /projects/<project_id>/delete/` - Delete project
- `GET /projects/<project_id>/files/` - Get project files
- `GET /projects/<project_id>/files/<filename>/` - Get file content
- `PUT /projects/<project_id>/files/<filename>/update/` - Update file
- `GET /projects/<project_id>/preview/` - Preview project
- `POST /ai/create-project-stream/` - Create project with AI (streaming)
- `GET /ai/tokens/` - Get token info

## Project Structure

```
backend/
├── webbuilder/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/                 # Django app
│   ├── models.py      # Database models (converted from SQLAlchemy)
│   ├── views.py        # API views (converted from FastAPI routers)
│   ├── serializers.py  # Request/response serializers (converted from Pydantic)
│   ├── urls.py         # URL routing
│   └── utils.py        # Utility functions (file handling)
├── app/                 # Original AI service files (unchanged)
│   ├── ai_providers.py
│   ├── ai_service_v2.py
│   └── ...
└── manage.py           # Django management script
```

## Differences from FastAPI

1. **URLs**: Django uses trailing slashes by default
2. **Async**: Django views are synchronous by default, async streaming is handled differently
3. **Serializers**: Uses DRF serializers instead of Pydantic models
4. **Database**: Uses Django ORM instead of SQLAlchemy
5. **CORS**: Uses `django-cors-headers` instead of FastAPI middleware

## Notes

- The AI service files in `app/` directory remain unchanged and are imported by the Django views
- All file handling logic is preserved in `api/utils.py`
- The database schema is the same, just using Django models instead of SQLAlchemy

