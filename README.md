# The Cakery

The Cakery is a Django-based web application for managing a bakery business. It includes a cake catalog, an ordering system, and user authentication features.

## Features

- User authentication and authorization
- Cake catalog with images and details
- RESTful API endpoints for cake data
- Database storage for cakes and user information
- Admin interface for managing content

## Requirements

- Python 3.8 or higher
- Django 3.2 or higher
- Django REST Framework
- SQLite (default) or PostgreSQL
- Other dependencies listed in `requirements.txt`

## Installation

### Setup the Project and Virtual Environment Side by Side

Ensure your project directory and virtual environment are in the same folder level, not nested.

### Clone the Repository
```bash
git clone https://github.com/hrsh-hp/THE_CAKERY_DJANGO.git
```

### Create a Virtual Environment (Outside the Project Folder)
```bash
python -m venv cakery-venv  # Create virtual environment
```

### Activate the Virtual Environment
#### Windows:
```bash
cakery-venv\Scripts\activate
```

#### macOS/Linux:
```bash
source cakery-venv/bin/activate
```

### Install Dependencies
```bash
pip install -r THE_CAKERY/requirements.txt
```

### Setup Environment Variables
```bash
cd THE_CAKERY_DJANGO
cp .env.example .env  # For Linux/macOS
copy .env.example .env  # For Windows
```

### Run Migrations
```bash
python manage.py migrate
```

### Create a Superuser
```bash
python manage.py createsuperuser
```

### Start the Development Server
```bash
python manage.py runserver
```

## Project Structure

```
project_root/
├── cakery-venv/           # Virtual environment (outside the project directory)
├── THE_CAKERY/            # Django project directory
│   ├── Auth/              # Authentication app
│   ├── cakery/            # Main project module
│   ├── cakes/             # Cakes app
│   ├── media/             # User-uploaded files
│   ├── static/            # Static files
│   ├── .env               # Environment variables
│   ├── db.sqlite3         # SQLite database
│   ├── manage.py          # Django management script
│   ├── requirements.txt   # Python dependencies
│   ├── README.md          # This file
```

## Usage

1. Access the admin interface at `http://localhost:8000/admin/` using your superuser credentials.
2. Browse the API endpoints at `http://localhost:8000/api/`.
3. View the cake catalog at `http://localhost:8000/cakes/`.

## API Endpoints

- `/api/auth/` - Authentication endpoints
- `/api/cakes/` - Cake catalog endpoints

## Database Population

To populate the database with initial data:
```bash
python manage.py shell < populate_data.py
```

Alternatively, use Jupyter Notebook:
```bash
jupyter notebook
# Open populate.ipynb and run the cells
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
