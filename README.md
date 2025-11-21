# LitRevu - Book Review Platform

## 📖 About the Project

LitRevu is a Django-based web application for requesting and publishing book reviews. 
This project was developed as an exercise of a training program focused on mastering Django framework and server-side 
rendering techniques.

### Context

This project dives into the world of Django, a powerful framework for creating web applications in Python. It uses server-side rendering to create dynamic and accessible user interfaces.
The mission consisted of creating all the application pages by integrating essential features for users: registration, login, activity feed, reviews, and subscriptions.
The application is developed following Django best practices for server-side rendering, database interaction, and user authentication.

### Key Features

- **User Authentication**: Sign up, login, and logout functionality
- **Activity Feed**: View tickets and reviews from followed users
- **Ticket Creation**: Request reviews for books or articles
- **Review System**: Publish reviews in response to tickets or create standalone reviews
- **Subscription Management**: Follow other users to see their activity
- **User Posts**: View and manage your own tickets and reviews

---

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd litrevu
   ```

2. **Build and start the container**
   ```bash
   docker compose -f docker/compose.yml up --build
   ```

3. **Access the application**
   
   Open your browser and navigate to: [http://localhost:8000](http://localhost:8000)

4. **Test Users**
   
   Two test users are automatically created:
   - Username: `Bob` | Password: `litrevuTest`
   - Username: `Tom` | Password: `litrevuTest`

5. **Stop the application**
   ```bash
   docker compose -f docker/compose.yml down
   ```

### Data Persistence

The SQLite database is persisted in the `data/` directory. To reset the database, simply delete this directory and restart the container.

---

## 💻 Local Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd litrevu
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Activate the virtual environment**
   
   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create test users (optional)**
   ```bash
   python manage.py create_test_users
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   
   Open your browser and navigate to: [http://localhost:8000](http://localhost:8000)

---

## 📦 Project Structure


---

## 🛠️ Technologies Used

- **Framework**: Django 5.2.5
- **Template Engine**: Jinja2
- **Database**: SQLite3
- **Package Manager**: uv
- **Containerization**: Docker & Docker Compose
- **Image Processing**: Pillow

---

## ⚠️ Important Notes

### Development Server

This application uses Django's built-in development server (`runserver`) for ease of evaluation and testing. **This setup is not suitable for production environments.**

### Security

The `SECRET_KEY` in `settings.py` is exposed for development purposes only. In a production environment, this should be stored securely as an environment variable.

---

## 🐛 Troubleshooting

### Docker Issues

**Permission denied errors**: Make sure Docker has proper permissions to access the project directory.

**Port 8000 already in use**: Stop any other services running on port 8000 or modify the port mapping in `docker/compose.yml`.

### Local Development Issues

**Module not found**: Ensure you've activated the virtual environment and run `uv sync`.

**Database errors**: Try deleting `data/db.sqlite3` and running `python manage.py migrate` again.

---

## 👤 Author
Arnaud Goguelin
