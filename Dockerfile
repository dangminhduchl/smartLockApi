FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN apt-get -y update
# for dlib
RUN apt-get install -y build-essential cmake
# for opencv
RUN apt-get install -y libopencv-dev
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]