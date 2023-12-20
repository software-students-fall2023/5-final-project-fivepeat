"""Database for this application"""
import os
from pymongo import MongoClient

"""DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
CONNECTION_STRING = f"mongodb://{DATABASE_HOST}:27017/"

client = MongoClient(CONNECTION_STRING)
db = client['quiz_game_db']
collection = db['quiz_scores']"""

DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "doadmin")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "Si7Hu4p9ln31F026")
DATABASE_HOST = os.getenv("DATABASE_HOST", "mongodb+srv://db-mongodb-nyc3-33511-709f7b62.mongo.ondigitalocean.com")
DATABASE_NAME = os.getenv("DATABASE_NAME", "admin")

CONNECTION_STRING = f"mongodb+srv://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

client = MongoClient(CONNECTION_STRING)
db = client[DATABASE_NAME]
collection = db['quiz_scores']
