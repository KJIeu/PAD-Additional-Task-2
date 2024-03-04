from flask import Flask, jsonify, request
import mysql.connector
from pymongo import MongoClient
from flask_caching import Cache
import random
import string


app = Flask(__name__)
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://pad_redis:6379/'
cache = Cache(app)


# client = MongoClient('mongodb://localhost:27017/')
client = MongoClient('mongodb://mongodb_master:27017/')
#client2 = MongoClient('mongodb://mongodb_master:27017')
db1 = client['delivery']
orders_collection = db1['orders']
characters = string.ascii_letters + string.digits


# Connect to MySQL
db_connection = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="mysql",
    database="driversdb"
)
db_cursor = db_connection.cursor(dictionary=True)

# Define the table creation query
create_table_query = """
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    location VARCHAR(100),
    availability_status TINYINT(1)
)
"""

# Try to execute the table creation query and handle the case where it fails due to the table already existing
try:
    db_cursor.execute(create_table_query)
    db_connection.commit()
except mysql.connector.Error as err:
    print("Error:", err)

characters = string.ascii_letters + string.digits

@app.route('/get_drivers', methods=['GET'])
@cache.cached(timeout=60)
def get_drivers():
    query_params = request.args.to_dict()
    query_conditions = []
    query_values = []

    if 'id' in query_params:
        query_conditions.append("id = %s")
        query_values.append(query_params['id'])

    if 'name' in query_params:
        query_conditions.append("name = %s")
        query_values.append(query_params['name'])

    if 'location' in query_params:
        query_conditions.append("location = %s")
        query_values.append(query_params['location'])

    if 'availability_status' in query_params:
        query_conditions.append("availability_status = %s")
        query_values.append(query_params['availability_status'])

    query = "SELECT * FROM drivers"
    if query_conditions:
        query += " WHERE " + " AND ".join(query_conditions)

    db_cursor.execute(query, tuple(query_values))
    drivers = db_cursor.fetchall()
    result = []
    for driver in drivers:
        driver_data = {
            'id': driver['id'],
            'name': driver['name'],
            'location': driver['location'],
            'availability_status': driver['availability_status']
        }
        result.append(driver_data)
    return jsonify(result)

@app.route('/create_drivers', methods=['POST'])
@cache.cached(timeout=60)
def create_driver():
    data = request.get_json()
    query = "INSERT INTO drivers (name, location, availability_status) VALUES ( %s, %s, %s)"
    values = (data['name'], data['location'], 1)
    db_cursor.execute(query, values)
    db_connection.commit()
    return jsonify({'message': 'Driver created successfully'}), 201

@app.route('/update_drivers/<int:id>', methods=['PUT'])
@cache.cached(timeout=60)
def update_driver(id):
    data = request.get_json()
    query = "UPDATE drivers SET name = %s, location = %s WHERE id = %s"
    values = (data['name'], data['location'], id)
    db_cursor.execute(query, values)
    db_connection.commit()
    return jsonify({'message': 'Driver updated successfully'})

@app.route('/get_orders', methods=['GET'])
@cache.cached(timeout=60)
def get_orders():
    query_params = request.args.to_dict()
    query = {}

    if 'customer_name' in query_params:
        query['customer_name'] = query_params['customer_name']

    if 'pickup_location' in query_params:
        query['pickup_location'] = query_params['pickup_location']

    if 'delivery_location' in query_params:
        query['delivery_location'] = query_params['delivery_location']

    if 'status' in query_params:
        query['status'] = query_params['status']

    orders = list(orders_collection.find(query))
    # Serialize ObjectId fields to strings
    for order in orders:
        order['_id'] = str(order['_id'])
    return jsonify(orders), 200

@app.route('/create_orders', methods=['POST'])
@cache.cached(timeout=60)
def create_order():
    data = request.get_json()
    new_order = {
        'id': ''.join(random.choice(characters) for _ in range(10)),
        'customer_name': data['customer_name'],
        'pickup_location': data['pickup_location'],
        'delivery_location': data['delivery_location'],
        'status': 1
    }
    orders_collection.insert_one(new_order)
    return jsonify({'message': 'Order created successfully'}), 201

@app.route('/update_orders/<order_id>', methods=['PUT'])
@cache.cached(timeout=60)
def update_order(order_id):
    data = request.get_json()
    updated_order = {
        'customer_name': data['customer_name'],
        'pickup_location': data['pickup_location'],
        'delivery_location': data['delivery_location'],
        'status': data['status']
    }
    orders_collection.update_one({'_id': order_id}, {'$set': updated_order})
    return jsonify({'message': 'Order updated successfully'}), 200


def phase_one(driver, order_id):
    if driver:
        # Phase 1 - Prepare Phase
        # Check if order exists in MongoDB and has status 1 and driver is in the same city as pickup location with availability_status 1
        order = orders_collection.find_one({'id': order_id, 'status': 1})

        if order:
            return 1
    return 0

def phase_two(driver, order_id):
    # Proceed with Phase 2 - Commit Phase
    try:
        # Update order status to 2 and set driver_id
        orders_collection.update_one({'id': order_id}, {'$set': {'status': 2, 'driver_id': driver['id']}})

        # Update driver availability_status to 2 in MySQL
        update_driver_query = "UPDATE drivers SET availability_status = 2 WHERE id = %s"
        db_cursor.execute(update_driver_query, (driver['id'],))

        # Commit changes
        db_connection.commit()
        return jsonify({'message': 'Transaction committed successfully'}), 200
    except Exception as e:
        # If any error occurs, rollback changes
        db_connection.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/create_transaction', methods=['POST'])
@cache.cached(timeout=60)
def create_transaction():
    data = request.get_json()
    order_id = data.get('order_id')

    # Find order in MongoDB
    order = orders_collection.find_one({'id': order_id})
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    # Find driver in the same city as pickup location with availability_status 1 from MySQL
    query = "SELECT * FROM drivers WHERE location = %s AND availability_status = 1 LIMIT 1"
    db_cursor.execute(query, (str(order['pickup_location']),))
    driver = db_cursor.fetchone()

    if phase_one(driver, order_id) == 1:
        return phase_two(driver, order_id)
    elif phase_one(driver, order_id) == 0:
        return jsonify({'message': 'Order not found or status is not valid for processing'}), 400
    elif not driver:
        return jsonify({'message': 'No available driver in the pickup location'}), 404


if __name__ == '__main__':

    app.run(debug=True)

