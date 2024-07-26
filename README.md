# Setup guide

1. Install dependencies with `pip install -r requirements.txt`

2. By default, when 'PROD' is NOT set in environment variables the default django database will be used, which requires no set up and is connected automatically.

3. Once you have connected a database, migrations need to be applied.
   Migrations can be applied by running (from the project's root)
   `python manage.py makemigrations` to generate the migrations
   `python manage.py migrate` to apply them on the database

4. Make a superuser. Once a db has been made, a superuser with access to the admin panel      needs to be made. 
   `python manage.py createsuperuser`

5. Run the workers
   `python -m gunicorn agile.asgi:application -k uvicorn.workers.UvicornWorker` for production
   `python manage.py runserver` for development
   (Both should work in development, only use gunicorn in production)


# For Production
When in production, a database needs to be set up.
2. Database setup:
   This is currently configured to use a postgresql database. That means it needs the following variables, either in a .env file or as environment variables:
   PGHOST='YOUR-HOST-ADDRESS'
   PGDATABASE='YOUR-DATABASE-NAME'
   PGUSER='YOUR-DB-USER'
   PGPASSWORD='YOUR-DB-PASSWORD'

   Ensure the 'PROD' environment variable is set to 'TRUE'
