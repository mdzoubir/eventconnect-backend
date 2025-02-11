# EventConnect

EventConnect is a Django-based web application designed to facilitate the creation, management, and participation in events. It provides a platform for organizers to host events and for users to discover and join them.

## Project Structure

The project's directory structure is organized as follows:

```
├── eventconnect
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── eventconnect-env
├── events
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── manage.py
├── README.md
├── requirements.txt
├── runtime.txt
├── vercel_app.py
├── vercel_build_script.sh
└── vercel.json
```

### Directories and Files

- `eventconnect/`: Contains the main project settings and configurations.
  - `asgi.py`: ASGI configuration for asynchronous support.
  - `settings.py`: Settings and configurations for the Django project.
  - `urls.py`: URL declarations for routing.
  - `wsgi.py`: WSGI configuration for deployment.
- `eventconnect-env/`: Directory for the virtual environment (not typically included in version control).
- `events/`: Contains the event management application.
  - `admin.py`: Configuration for the Django admin interface.
  - `apps.py`: Application configuration.
  - `models.py`: Data models representing the database schema.
  - `serializers.py`: Serializers for converting data between complex types and JSON.
  - `tests.py`: Test cases for the application.
  - `urls.py`: URL routing specific to the events app.
  - `utils.py`: Utility functions.
  - `views.py`: Handles the logic for processing requests and returning responses.
- `manage.py`: Command-line utility for administrative tasks.
- `README.md`: This file, providing an overview of the project.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `runtime.txt`: Specifies the Python runtime version.
- `vercel_app.py`: Entry point for Vercel deployment.
- `vercel_build_script.sh`: Build script for Vercel deployment.
- `vercel.json`: Configuration file for Vercel deployment.

## Setup Instructions

To set up the project locally:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/mdzoubir/eventconnect-backend.git
   cd eventconnect-backend
   ```

2. **Create and Activate Virtual Environment**:

   ```bash
   python3 -m venv eventconnect-env
   source eventconnect-env/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

Access the application at `http://127.0.0.1:8000/`.

## API Endpoints

The application provides the following API endpoints:

### Events

- `GET /api/events/` - Retrieve a list of all events.
- `POST /api/events/` - Create a new event.
- `GET /api/events/<id>/` - Retrieve details of a specific event.
- `PUT /api/events/<id>/` - Update an existing event.
- `DELETE /api/events/<id>/` - Delete an event.

### RSVPs

- `GET /api/rsvps/` - Retrieve a list of RSVPs.
- `POST /api/rsvps/` - Create a new RSVP.
- `GET /api/rsvps/<id>/` - Retrieve details of a specific RSVP.
- `PUT /api/rsvps/<id>/` - Update an RSVP.
- `DELETE /api/rsvps/<id>/` - Delete an RSVP.

### User Authentication

- `POST /api/register/` - Register a new user.
- `POST /api/token/` - Obtain an access and refresh token.
- `POST /api/token/refresh/` - Refresh an access token.

### Matched Events

- `GET /api/matched-events/` - Retrieve events matched based on user preferences.

## Database Setup

The project uses PostgreSQL as the database. To set up the database:

1. **Install PostgreSQL** (if not already installed).
2. **Create a new database**:
   ```sql
   CREATE DATABASE eventconnect;
   ```
3. **Configure `settings.py`**:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'eventconnect',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
4. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

## Deployment

The project is configured for deployment on Vercel. Ensure that the `vercel.json`, `vercel_app.py`, and `vercel_build_script.sh` files are correctly set up. For detailed deployment instructions, refer to Vercel's official documentation.

### Live URL:

[EventConnect Deployment](https://eventconnect-backend.vercel.app/)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes.
