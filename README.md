# Shopify Parser Dashboard

## Project Overview

This project is an administrative dashboard for creating shopify carts with a total of at least 200$, built with Django and deployed via Docker Compose. It provides a Django Admin interface to add, edit, and delete store records.

## Environment Variables

Create a `.env` file in the project root and add the following variables:

```dotenv
SECRET_KEY=<your_django_secret_key>

DB_USER=<your_db_username>
DB_PASSWORD=<your_db_password>
DB_NAME=<your_db_name>
DB_HOST=db
DB_PORT=5432

CELERY_BROKER_URL = 'redis://redis:6379'

DJANGO_SUPERUSER_USERNAME=<admin_username>
DJANGO_SUPERUSER_PASSWORD=<admin_password>
```

## Getting Started

1. **Clone the repository** and navigate into the project directory:

   ```bash
   git clone https://github.com/MykhailoKononov/ShopifyCarts.git
   cd shopify_parser
   ```

2. **Create and configure** the `.env` file with your values as shown above.

3. **Build and start** the Docker containers:

   ```bash
   docker-compose up --build -d
   ```

4. **Wait** for the services to start and become healthy.

## Accessing Django Admin

1. Open your browser and go to: `http://localhost:8000/admin`
2. Log in using the superuser credentials set in the `.env` file:

   * **Username:** the value of `DJANGO_SUPERUSER_USERNAME`
   * **Password:** the value of `DJANGO_SUPERUSER_PASSWORD`


## Useful Commands

* **View logs** of all containers:

  ```bash
  docker-compose logs -f
  ```

* **Stop and remove** containers:

  ```bash
  docker-compose down
  ```

* **Rebuild and restart** the services:

  ```bash
  docker-compose up --build -d
  ```

---

Now you can quickly deploy the project and start managing stores via the Django Admin interface.
