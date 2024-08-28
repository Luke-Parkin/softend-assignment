# Setup guide

## Development

1. Install dependencies with `pip install -r requirements.txt`

2. By default, when 'PROD' is NOT set in environment variables the default django database will be used, which requires no set up and is connected automatically. (use instructions in the next section for setting up another db)

3. Generate the static assets (css, js)
   `python manage.py collectstatic --clear --no-input`

4. Once you have connected a database (again, done by default if 'PROD' is not set), migrations need to be applied.
   Migrations can be applied by running (from the project's root)
   `python manage.py makemigrations` to generate the migrations
   `python manage.py migrate` to apply them on the database

5. Make a superuser. Once a db has been made, a superuser with access to the admin panel needs to be made. 
   `python manage.py createsuperuser`

6. Run the workers
   `python -m gunicorn agile.asgi:application -k uvicorn.workers.UvicornWorker` for production
   - OR -
   `python manage.py runserver` for development
   (Both should work in development, only use gunicorn in production)

## For Production

1. When in production, a database needs to be linked
   This is currently configured to use a postgresql database. That means it needs the following variables, either in a .env file or as environment variables:
   PGHOST='YOUR-HOST-ADDRESS'
   PGDATABASE='YOUR-DATABASE-NAME'
   PGUSER='YOUR-DB-USER'
   PGPASSWORD='YOUR-DB-PASSWORD'

   Ensure the 'PROD' environment variable is set to 'TRUE'
2. The service can be run by your runner of choice. Gunicorn is recommended:
      `python -m gunicorn agile.asgi:application -k uvicorn.workers.UvicornWorker`

## Specific deployment implementations for this production

For this the official production, two hosts are used

The database is hosted on <neon.tech>. This is quite slow but good enough for the demonstration, and was chosen for the
ease of connection, and the fact they don't delete your data every 30 days like other free providers

<https://vercel.com> is used as the server host, vercel.json stores the infrastructure-as-code, including the rewrite paths for urls.
build.sh is defined in the vercel.json, and the script builds the static resources and migrates the db for production.

Vercel automatically runs the build/deployment on merge to main in github.

## Notes on users
