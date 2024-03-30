from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import database
import generic

app = FastAPI()

inprogressOrders = {} # For order-complete intent

# Functionality for handling the dialogflow request
@app.post("/")
async def handleRequest(request:Request):
    
    # Retriving the JSON data from the request
    payload = await request.json()
    
    # Extracting the information from dialogflow payload
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    outputContexts = payload['queryResult']['outputContexts']
    
    sessionId = generic.extractSessionId(outputContexts[0]['name']) # Extracting session Id
    
    intentHandlerDict = {
        'order.add-context:ongoing-order': addToOrder,
        'order.complete-context:ongoing-order':completeOrder,
        'track.order-context:ongoing-tracking': track_order,
        'order.remove-context:ongoing-order': removingOrder
    }
    return intentHandlerDict[intent](parameters,sessionId)

# Add to order functionality
def addToOrder(parameters:dict,session_id:str):
    foodItems = parameters["food-item"]
    quantities = parameters["number"]
    
    if len(foodItems) != len(quantities):
        fulfillmentText = "I didn't understand, please specify quantities clearly"
    else:
        new_food_dict = dict(zip(foodItems,quantities))
        if session_id in inprogressOrders:
            current_food_dict = inprogressOrders[session_id]
            current_food_dict.update(new_food_dict)
            inprogressOrders[session_id] = current_food_dict
        else:
            inprogressOrders[session_id] = new_food_dict
        
        order_str = generic.getStringFromFood(inprogressOrders[session_id])
        fulfillmentText = f"So far you have: {order_str}, do you need anything!"
        
    print(inprogressOrders)
    return JSONResponse(content={
            "fulfillmentText": fulfillmentText
    })
      
      
# Functionality for removing a particular order

def removingOrder(parameters:dict,session_id:str):
    if session_id not in inprogressOrders:
        fulfillmentText = "Having a trouble finding your order, place a new order"
    else:
        currentOrder = inprogressOrders[session_id]
        food_items = parameters['food-item']
        
        
        # Keeping track of removed items and no such items
        removedItems = []
        noSuchItems = []
        
        # This for loop defined which items are removed from the order, which items doesn't exist
        for item in food_items:
            if item not in currentOrder: # If item is not in current order
                noSuchItems.append(item)
            else:
                removedItems.append(item)
                del currentOrder[item]

        # Logic for prompts to be given by the chatbot
        if len(removedItems) > 0:
            fulfillmentText = f'Removed {",".join(removedItems)} from your order!'
        if len(noSuchItems) > 0:
            fulfillmentText = f'Your current order does not have {",".join(noSuchItems)} '
        if (currentOrder.keys()) == 0:
            fulfillmentText = "Your order is empty"
        
        else:
            orderStr = generic.getStringFromFood(currentOrder)
            fulfillmentText = f"Here is what is left in your order {orderStr}"
            
    return JSONResponse(content={
            "fulfillmentText": fulfillmentText
    })
            
# Functionality for order completion intent
def completeOrder(parameters:dict,session_id:str):
    if session_id not in inprogressOrders:
        fulfillmentText = "Having a trouble finding your order, place a new order"
    else:
        order = inprogressOrders[session_id]
        order_id = saveToDb(order)
        
        if order_id == -1:
            fulfillmentText = "Sorry, I couldn't process the order, place a new order"
        else:
            orderTotal = database.getTotalOrderPrice(order_id)
            fulfillmentText = f"Awesome. We have placed your order. "\
                f"Here is your order id # {order_id}."\
                f" Order Total {orderTotal}, you can pay at the time of delivery."
        
        del inprogressOrders[session_id] # removing the placed order from the in_progress order
        
    return JSONResponse(content={
            "fulfillmentText": fulfillmentText
    })
        
            
# Inserting the orders to the database
def saveToDb(order:dict):
    nextOrderId = database.getNextOrderId()
    for food_item,quantity in order.items():
        returnCode = database.insertOrderItem(
            food_item,
            quantity,
            nextOrderId
        )
        if returnCode == -1:
            return -1
    
    database.insertOrderTracking(nextOrderId,"In Progress")
    return nextOrderId
        
# Functionality for tracking the order
def track_order(parameters:dict,session_id:str):
    order_id = parameters['order_id']
    status = database.getOrderStatus(order_id)
    
    if status:
        fulfillmentText = f"The order status for order id {order_id} is: {status}"
    else:
        fulfillmentText = f"No order found with order id : {order_id}"
    return JSONResponse(content={
            "fulfillmentText": fulfillmentText
    })
        