FROM python:3.12.6

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip3 install --upgrade pip
RUN pip3 install --user -r requirements.txt

# Copy project
COPY . /code/

# Make the run script executable
RUN chmod +x docker_run_server.sh

# Expose port 80
EXPOSE 80

# Start server
ENTRYPOINT ["./docker_run_server.sh"]
