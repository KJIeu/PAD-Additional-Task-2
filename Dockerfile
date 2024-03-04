# Use official Redis image as base
FROM redis:latest

# Use an official Python runtime as a parent image
FROM python:3.9

## Set environment variables for MongoDB connection
#ENV MONGO_DB=mydatabase
#ENV MONGO_USER=myuser
#ENV MONGO_PASSWORD=mypassword
#ENV MONGO_HOST=db
#ENV MONGO_PORT=27017

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory into the container at /app
COPY . .


# Expose Redis port to host
#EXPOSE 6379
#
## Expose Mongo DB
#EXPOSE 27017

# Expose Flask port
EXPOSE 5000

# Command to run the Python script
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]



