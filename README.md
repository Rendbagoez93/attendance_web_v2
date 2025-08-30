#Attendance Management System

A web-based employee attendance and management system built with Django.

## Features
- Secure employee login/logout
- Role-based dashboards (HR, Manager, Employee)
- Employee CRUD (Create, Read, Update, Delete)
- Attendance tracking and management
- Employee profile management
- Notification and confirmation system for user actions
- Responsive UI with Bootstrap 5

## Project Structure
```
attendance.v2/
├── attendance/           # Django project settings
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── emp_attd/             # Attendance app (views, models, templates)
├── employee/             # Employee management app
│   ├── management/       # Custom management commands
│   ├── migrations/       # Database migrations
│   └── templates/        # Employee templates
├── static/               # Static files (CSS, JS, images)
├── templates/            # Shared templates
├── db.sqlite3            # SQLite database (development)
├── manage.py             # Django management script
├── pyproject.toml        # Project dependencies
├── uv.lock               # Lock file for dependencies
└── .gitignore            # Git ignore rules
```

## Setup Instructions
1. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd attendance.v2
   ```
2. **Install dependencies**
   ```sh
   uv pip install -r requirements.txt
   ```
3. **Apply migrations**
   ```sh
   uv run manage.py migrate
   ```
4. **Create a superuser**
   ```sh
   uv run manage.py createsuperuser
   ```
5. **Run the development server**
   ```sh
   uv run manage.py runserver
   ```
6. **Access the app**
   Open your browser and go to `http://127.0.0.1:8000/`

## Default Accounts
- Admin and sample employee accounts can be created using the provided management command:
  ```sh
  uv run manage.py create_sample_employees
  ```

## Customization
- Update company branding in `static/images/` and `templates/base.html`.
- Adjust roles and permissions in the `Employee` model.
