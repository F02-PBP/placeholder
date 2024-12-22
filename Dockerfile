FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p staticfiles
RUN chmod 755 db.sqlite3  # Make sure SQLite database is writable

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN python manage.py collectstatic --noinput

CMD gunicorn jogja_rasa.wsgi:application --bind 0.0.0.0:$PORT