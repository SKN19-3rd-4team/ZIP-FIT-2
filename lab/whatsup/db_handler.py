from dotenv import load_dotenv
import os
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np



class DatabaseManager():

    def __init__(self):
        load_dotenv()
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_NAME = os.getenv('DB_NAME')




def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True 
    register_vector(conn) 
    return conn