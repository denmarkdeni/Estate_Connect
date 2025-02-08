# Use a Slim Python Image (reduces 600MB+)
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY requirements.txt .

# Install dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy only required files (avoid copying venv, .git, __pycache__)
COPY . .

# Expose the required port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
