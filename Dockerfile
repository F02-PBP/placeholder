FROM python:3.9  

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

RUN python manage.py migrate && python manage.py import_data

CMD ["gunicorn", "jogja_rasa.wsgi:application", "--bind", "0.0.0.0:8000"]