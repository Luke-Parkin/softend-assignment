# Setup guide

## Development

1. Install dependencies with `pip install -r requirements.txt`

2. By default, when 'PROD' is NOT set in environment variables the default django database will be used, which requires no set up and is connected automatically. (use instructions in prod for setting up another db)

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

## For Production

1. When in production, a database needs to be linked
   This is currently configured to use a postgresql database. That means it needs the following variables, either in a .env file or as environment variables:
   PGHOST='YOUR-HOST-ADDRESS'
   PGDATABASE='YOUR-DATABASE-NAME'
   PGUSER='YOUR-DB-USER'
   PGPASSWORD='YOUR-DB-PASSWORD'

   Ensure the 'PROD' environment variable is set to 'TRUE'
2. The service can be run by your runner of choice. Gunicorn is reccomended:
      `python -m gunicorn agile.asgi:application -k uvicorn.workers.UvicornWorker`

## Specific deployment implementations for this production

For this the official production, <https://render.com/> is used.
The environment variables are stored as secrets within render.
The render.yaml defines the infrastructure and concurrency.
The build.sh script handles the building.

The database is hosted on <neon.tech>. This is quite slow but good enough for the demonstration.

Using the free version of render.com does have drawbacks, primarily its speed and it's spin-down feature. Render spins down services after 15 minutes of no use. Since the service takes 2 minutes to start back up, this makes usage a bad experience.

As such, as a workaround <https://console.cron-job.org> was used. Every 10 minutes it sends a get request to the dashboard page, keeping the service alive.
