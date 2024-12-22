FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

RUN python manage.py collectstatic --noinput

CMD gunicorn jogja_rasa.wsgi:application --bind 0.0.0.0:$PORT