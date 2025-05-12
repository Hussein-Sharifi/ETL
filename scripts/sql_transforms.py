import psycopg2
from psycopg2 import sql
from config import connect_to_postgresql

conn, cur = connect_to_postgresql()