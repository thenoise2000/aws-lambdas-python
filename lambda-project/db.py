import os
import psycopg2
from psycopg2 import sql
def get_db_connection():
    """Conexión a la base de datos PostgreSQL."""
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn
def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS readings (
            id SERIAL PRIMARY KEY,
            reading_id VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            license_plate VARCHAR(20) NOT NULL,
            checkpoint_id VARCHAR(255) NOT NULL,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            ad_content VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS exposures (
            id SERIAL PRIMARY KEY,
            reading_id VARCHAR(255) NOT NULL,
            campaign_id VARCHAR(255) NOT NULL,
            exposure_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reading_id) REFERENCES readings (reading_id)
        )
        """
    )
    
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                for command in commands:
                    cursor.execute(command)
    finally:
        conn.close()
def store_reading(reading_id, timestamp, license_plate, checkpoint_id, latitude, longitude, ad_content):    
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO readings (reading_id, timestamp, license_plate, checkpoint_id, latitude, longitude, ad_content)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (reading_id, timestamp, license_plate, checkpoint_id, latitude, longitude, ad_content))
    finally:
        conn.close()
def fetch_metrics():    
    conn = get_db_connection()
    metrics = {}
    try:
        with conn:
            with conn.cursor() as cursor:
                # Tenemos total de lecturas por checkpoint
                cursor.execute("SELECT checkpoint_id, COUNT(*) FROM readings GROUP BY checkpoint_id")
                metrics['total_readings_per_checkpoint'] = cursor.fetchall()
                
                # Publicidades mostradas por campaña
                cursor.execute("""
                    SELECT campaign_id, COUNT(*) FROM exposures GROUP BY campaign_id
                """)
                metrics['total_ads_per_campaign'] = cursor.fetchall()
                
                # Listado de últimas exposiciones
                cursor.execute("""
                    SELECT * FROM exposures ORDER BY exposure_time DESC LIMIT 10
                """)
                metrics['last_exposures'] = cursor.fetchall()
    finally:
        conn.close()
    
    return metrics