# # celery_app.py
# import os
# from celery import Celery
# from dotenv import load_dotenv

# load_dotenv()

# def make_celery(app_name=__name__):
#     return Celery(
#         app_name,
#         broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
#         backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
#         include=["utils.tasks"]  # ensure tasks are registered
#     )

# celery = make_celery()