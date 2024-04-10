import os
from dotenv import load_dotenv
import psycopg2 as psql

load_dotenv()

conn = psql.connect(dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'))

cur = conn.cursor()


def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS "
                "user_table("
                "id SERIAL PRIMARY KEY, "
                "tg_id INTEGER,"
                "bio VARCHAR(30), "
                "telephone VARCHAR(15), "
                "email VARCHAR(25), "
                "epitaph VARCHAR(500))")

    conn.commit()
