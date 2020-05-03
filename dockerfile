FROM python:3.7-alpine

COPY . /app

EXPOSE 8000

WORKDIR /app

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

RUN python manage.py makemigrations

RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]