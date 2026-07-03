# Use the official slim Python runtime image
FROM python:3.11-slim

# Set an isolated internal build working directory environment
WORKDIR /app

# Copy dependency mappings and install caching optimization layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all remaining repository source data elements into the execution framework context
COPY . .

# Expose target network port standard bound mapping endpoint
EXPOSE 8080

# Configure environment defaults to instruct Streamlit to pass traffic cleanly through Google's networking routing proxy
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
