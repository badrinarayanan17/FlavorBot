# Establishing database connection

import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    port=3307,
    password="irdab119",
    database="pandeyji_eatery"
)

# Database functionality for getting the total order price by calling user defined function

def getTotalOrderPrice(order_id):
    cursor = cnx.cursor()
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)
    
    result = cursor.fetchone()[0]
    cursor.close()
    return result

# Database functionality for inserting a order by calling the stored procedure

def insertOrderItem(food_item,quantity,order_id):
    try:
        cursor = cnx.cursor()
        
        # calling the stored procedure
        cursor.callproc('insert_order_item',(food_item,quantity,order_id))
        cnx.commit()
        cursor.close()
        print("Order item inserted successfully")
        return 1
    
    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()
        
        return -1
        
    except Exception as e:
        print(f"Error Occured: {e}")
        cnx.rollback()
        
        return -1
        
# Getting the next order id

def getNextOrderId():
    cursor = cnx.cursor()
    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)
    
    # fetching
    res = cursor.fetchone()[0]
    cursor.close()
    
    if res is None:
        return 1
    else:
        return res + 1
    
# Functionality to insert the order tracking
def insertOrderTracking(order_id,status):
    cursor = cnx.cursor()
    insertQuery = "INSERT INTO order_tracking (order_id,status) VALUES (%s,%s)"
    cursor.execute(insertQuery,(order_id,status))
    cnx.commit()
    cursor.close()

# Getting the order status
def getOrderStatus(order_id:int):
    
    # Creating a cursor object
    cursor = cnx.cursor()
    
    # Query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")
    
    # Executing
    cursor.execute(query,(order_id,))
    
    result = cursor.fetchone()
    
    cursor.close()
 
    if result is not None:
        return result[0]
    else:
        None
    
# # Database Functionality for removing a order

# def removeOrder(order_id:int):
    
#     cursor = cnx.cursor()
#     query = "DELETE FROM orders WHERE order_id = %d"
#     cursor.execute(query,(order_id,))
#     result = cursor.fetchone()
#     cursor.close()
    
#     if result is not None:
#         return result[0]
#     else:
#         None
    


