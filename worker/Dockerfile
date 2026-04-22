FROM python:3.11-slim

# prevent unnecessary scripts from running during installation
ENV PYTHONUNBUFFERED=1

# system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# create root user 
RUN useradd -m appuser

# set the working directory
WORKDIR /app

# install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy app source code
COPY . .

# change ownership of the app files to the non-root user
RUN chown -R appuser:appuser /app

# switch to the non-root user
USER appuser

# run worker file
CMD ["python", "worker.py"]