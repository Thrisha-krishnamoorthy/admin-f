from flask import Flask, request, jsonify
import mysql.connector
from db_config import db_config
from flask_cors import CORS
import bcrypt
from mysql.connector import Error
import os
import logging

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        logger.info("Attempting to connect with config: %s", {k: v for k, v in db_config.items() if k != 'password'})  # Log config without password
        connection = mysql.connector.connect(**db_config)
        logger.info("Database connection successful")
        return connection
    except mysql.connector.Error as err:
        logger.error("Database connection error: %s", err)
        logger.error("Error code: %s", err.errno)
        logger.error("Error message: %s", err.msg)
        return None

@app.route('/products', methods=['GET'])
def get_products():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        return jsonify(products)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/register-admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    print("Received data:", data)  # Debug: Print received data

    # Validate required fields
    required_fields = ['name', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Check if the email already exists
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT email FROM admins WHERE email = %s", (email,))
    existing_admin = cursor.fetchone()

    if existing_admin:
        cursor.close()
        connection.close()
        return jsonify({"error": f"Admin with email {email} already exists"}), 400

    # Insert the new admin
    query = "INSERT INTO admins (name, email, password_hash) VALUES (%s, %s, %s)"
    values = (name, email, hashed_password.decode('utf-8'))  # Store the hashed password

    try:
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Admin registered successfully"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Route to login as an admin
@app.route('/login-admin', methods=['POST'])
def login_admin():
    data = request.get_json()
    print("Received data:", data)  # Debug: Print received data

    # Validate required fields
    required_fields = ['email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    email = data.get('email')
    password = data.get('password')

    # Fetch the admin from the database
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admins WHERE email = %s", (email,))
    admin = cursor.fetchone()

    if not admin:
        cursor.close()
        connection.close()
        return jsonify({"error": "Admin not found"}), 404

    # Verify the password
    stored_hashed_password = admin['password_hash'].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        cursor.close()
        connection.close()
        return jsonify({"message": "Admin login successful"}), 200
    else:
        cursor.close()
        connection.close()
        return jsonify({"error": "Invalid password"}), 401

@app.route('/products', methods=['POST'])
def add_product():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    required_fields = ['name', 'description', 'price', 'image_url', 'category']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO Products (name, description, price, image_url, category, quantity, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # Validate and convert data types according to schema
        try:
            name = str(data['name'])[:255]  # VARCHAR(255)
            description = str(data['description'])  # TEXT
            price = float(data['price'])  # DECIMAL(10,2)
            image_url = str(data['image_url'])[:255]  # VARCHAR(255)
            category = str(data['category'])[:255]  # VARCHAR(255)
            quantity = int(data.get('quantity', 0))  # Default to 0
            status = str(data.get('status', 'in_stock'))[:50]  # Default to 'in_stock'
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Invalid data format: {str(e)}"}), 400

        values = (name, description, price, image_url, category, quantity, status)
        
        cursor.execute(query, values)
        connection.commit()
        
        return jsonify({
            "message": "Product added successfully",
            "product_id": cursor.lastrowid
        }), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/orders', methods=['GET'])
def get_orders():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            Orders.order_id,
            Users.name AS customer_name,
            Users.email,
            Users.phone,
            Orders.order_status,
            Orders.total_price,
            Orders.delivery_type,
            Orders.delivery_address,
            Products.name AS product_name,
            Order_Items.quantity,
            Order_Items.price AS item_price
        FROM 
            Orders
        JOIN 
            Users ON Orders.user_id = Users.user_id
        JOIN 
            Order_Items ON Orders.order_id = Order_Items.order_id
        JOIN 
            Products ON Order_Items.product_id = Products.product_id
        """
        cursor.execute(query)
        orders = cursor.fetchall()
        return jsonify(orders)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/update_status', methods=['PUT'])
def update_order_status():
    """Update order status to 'shipped' or 'delivered' in MySQL"""
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    order_id = data.get("order_id")
    new_status = data.get("new_status")

    # Allowed statuses
    allowed_statuses = ["shipped", "delivered"]
    if new_status not in allowed_statuses:
        return jsonify({"error": "Invalid status. Allowed: 'shipped', 'delivered'"}), 400

    try:
        cursor = connection.cursor()
        query = "UPDATE Orders SET order_status = %s WHERE order_id = %s"
        cursor.execute(query, (new_status, order_id))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Order not found"}), 404
        
        return jsonify({"message": f"Order {order_id} updated to {new_status}"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Products WHERE product_id = %s", (product_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify({"message": "Product deleted successfully"})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status_endpoint(order_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    try:
        cursor = connection.cursor()
        query = "UPDATE Orders SET order_status = %s WHERE order_id = %s"
        cursor.execute(query, (new_status, order_id))
        connection.commit()
        
        if cursor.rowcount > 0:
            return jsonify({"success": True, "message": "Order status updated successfully"})
        else:
            return jsonify({"error": "Order not found"}), 404
            
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        cursor = connection.cursor()

        # Build update query dynamically based on provided fields
        update_fields = []
        values = []

        if 'name' in data:
            update_fields.append("name = %s")
            values.append(str(data['name'])[:255])

        if 'description' in data:
            update_fields.append("description = %s")
            values.append(str(data['description']))

        if 'price' in data:
            update_fields.append("price = %s")
            values.append(float(data['price']))

        if 'image_url' in data:
            update_fields.append("image_url = %s")
            values.append(str(data['image_url'])[:255])

        if 'category' in data:
            update_fields.append("category = %s")
            values.append(str(data['category'])[:255])

        update_status = False  # Flag to track status update
        
        if 'quantity' in data:
            quantity = int(data['quantity'])
            update_fields.append("quantity = %s")
            values.append(quantity)

            # Fetch current product status
            cursor.execute("SELECT status FROM Products WHERE product_id = %s", (product_id,))
            result = cursor.fetchone()

            if result:
                current_status = result[0]
                if current_status == "out_of_stock" and quantity > 0:
                    update_fields.append("status = %s")
                    values.append("in_stock")
                    update_status = True
                elif quantity == 0:
                    update_fields.append("status = %s")
                    values.append("out_of_stock")
                    update_status = True

        if 'status' in data and not update_status:  # Prevent overriding auto-update
            update_fields.append("status = %s")
            values.append(str(data['status'])[:50])

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        query = f"UPDATE Products SET {', '.join(update_fields)} WHERE product_id = %s"
        values.append(product_id)

        cursor.execute(query, tuple(values))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"message": "Product updated successfully"})
    except (mysql.connector.Error, ValueError) as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)