FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app
COPY ./cidr_api2.py /app
COPY ./cidr_ipattr.py /app
COPY ./docker/api/requirements.txt /app

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "uvicorn", "cidr_api2:app", "--reload", "--host", "0.0.0.0"]
