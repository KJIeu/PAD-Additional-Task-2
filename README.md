# PAD-Additional-Task-2

# Flask Application

This Flask application provides endpoints for managing drivers and orders. It integrates with MongoDB for order management and MySQL for driver management.

## Running the Application

1. Install dependencies:    pip install Flask pymongo mysql-connector-python flask-caching
   
2. Run the application:     python app.py



## Endpoints

### Get Drivers

- **URL:** `/get_drivers`
- **Method:** `GET`
- **Description:** Retrieve a list of drivers based on query parameters.
- **Query Parameters:**
- `id`: Filter drivers by ID.
- `name`: Filter drivers by name.
- `location`: Filter drivers by location.
- `availability_status`: Filter drivers by availability status.
- **Example Request:**

### Create Driver

- **URL:** `/create_drivers`
- **Method:** `POST`
- **Description:** Create a new driver.
- **Request Body:**
json:
{
  "name": "John Doe",
  "location": "New York"
}

### Update Driver
URL: /update_drivers/<id>
Method: PUT
Description: Update an existing driver.
Request Body:
json:
{
  "name": "John Smith",
  "location": "Los Angeles"
}


### Get Orders
URL: /get_orders
Method: GET
Description: Retrieve a list of orders based on query parameters.
Query Parameters:
customer_name: Filter orders by customer name.
pickup_location: Filter orders by pickup location.
delivery_location: Filter orders by delivery location.
status: Filter orders by status.


### Create Order
URL: /create_orders
Method: POST
Description: Create a new order.
Request Body:
{
  "customer_name": "Alice",
  "pickup_location": "New York",
  "delivery_location": "Los Angeles"
}


### Update Order
URL: /update_orders/<order_id>
Method: PUT
Description: Update an existing order.
Request Body:
{
  "customer_name": "Alice Smith",
  "pickup_location": "Chicago",
  "delivery_location": "San Francisco",
  "status": 2
}


Create Transaction
URL: /create_transaction
Method: POST
Description: Create a transaction for processing orders.
Request Body:
{
  "order_id": "123"
}



