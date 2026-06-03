# from celery.result import AsyncResult
# from utils.celery_app import app
# from test import send_email

# result = send_email.delay("user@example.com", "Welcome!")

# print(f"Task ID: {result.id}")          # Get task ID immediately
# print(f"Result: {result.get()}")
# print(f"Status: {result.status}")


# # task = AsyncResult("your-task-id", app=app)

# # print(task.status)   # PENDING, STARTED, SUCCESS, FAILURE
# # print(task.result)   # Return value once 

# # command 
# # celery -A filename worker --pool=solo --loglevel=info