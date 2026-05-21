import os
import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from .utils import publish_order_placed

app = FastAPI(
    title="Order-service",
    description="Orchestrates microservice orders and broadcasts async inventory events via RabbitMQ"
)

# Read the internal microservice URLS from envronment variables
USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://flask_users_service:5001"
)

# Request validtaion schemas
class OrderCreate(BaseModel):
    user_id:int
    product_id: int
    quantity: int

    class Config:
        json_schema_extra = {
            "example":{
                "user_id":1,
                "product_id":5,
                "quantity": 2
            }
        }

# creating Endpoints
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy", "service": "orders-service"}

"""
    Creates a new order purchase flow.
    1. Verifies the user exists via the User Service.
    2. Broadcasts a non blocking background inventory reduction message to RabbitMQ.
"""
@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order:OrderCreate):
    #1. Validate user existence
    async with httpx.AsyncClient() as client:
        try:
            # Get user_id from Flask user service GET endpoint: /users/<id>
            user_response = await client.get(f"{USER_SERVICE_URL}/users/{order.user_id}", timeout=3)

            if user_response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order rejected: User ID {order.user_id} does not exist"
                )
            elif user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail = "Failed to communicate realiably with User verification service"
                )
        
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"User verification service is temporarrily unreachable: {exc}"
            )
                
    # 2. Trigger Asynchoronous inventory Allocation
    try:
        publish_order_placed(product_id=order.product_id, quantity=order.quantity)
    except Exception as mq_err:
        # If the broker is atructurally unreachable throw a 500 so client know the transaction failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Örder accepted but critical background worker event broadcast faild: {mq_err}" 
        )

    # 3. Respond back to client
    return{
        "message":"Order processing initiated succesfully",
        "order_details":{
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity
        },
        "delivery_pipeline": "asynchronous_broker_queue"
    }

