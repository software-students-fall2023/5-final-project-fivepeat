"""Database for this application"""
import os
from pymongo import MongoClient

"""DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
CONNECTION_STRING = f"mongodb://{DATABASE_HOST}:27017/"

client = MongoClient(CONNECTION_STRING)
db = client['quiz_game_db']
collection = db['quiz_scores']"""


username = "doadmin"
password = "Si7Hu4p9ln31F026"
host = "db-mongodb-nyc3-33511-709f7b62.mongo.ondigitalocean.com"
database_name = "admin"

uri = f"mongodb+srv://{username}:{password}@{host}/{database_name}?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['quiz_game_db']
collection = db['quiz_scores']


