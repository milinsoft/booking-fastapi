FROM python:3.12-slim
LABEL authors="aleksander"

RUN mkdir /booking

WORKDIR /booking

# Separate step to make sure re-build uses cached requirements
COPY requirements.txt .

# install requirements
RUN pip install -r requirements.txt

# Copy all project files into booking
COPY . .
COPY docker/* /booking/scripts/


# make shell scripts executable
RUN chmod a+x /booking/scripts/*.sh




CMD ["gunicorn", "app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]
