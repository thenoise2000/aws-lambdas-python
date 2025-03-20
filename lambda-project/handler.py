import json
import os
import psycopg2
from datetime import datetime

# Conexion Bd
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn
def process_license_plate(event, context):
    body = json.loads(event['body'])
    
    # Validacion de formato
    if not validate_license_plate_format(body):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid format'})
        }
    # Publicidad aplicable
    ad_content = determine_ad(body)

    
    store_reading(body, ad_content)
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processed successfully'})
    }

def get_metrics(event, context):
    # Obtencion de métricas
    metrics = fetch_metrics()
    return {
        'statusCode': 200,
        'body': json.dumps(metrics)
    }
    # Implementacion de validacion
def validate_license_plate_format(body):    
    return True
    # Implementacion de campañas 
def determine_ad(body):    
    return "AD_001"
def store_reading(body, ad_content):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO readings (reading_id, timestamp, license_plate, checkpoint_id, latitude, longitude, ad_content)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (body['reading_id'], body['timestamp'], body['license_plate'], body['checkpoint_id'],
          body['location']['latitude'], body['location']['longitude'], ad_content))
    conn.commit()
    cursor.close()
    conn.close()
def fetch_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM readings GROUP BY checkpoint_id")
    metrics = cursor.fetchall()
    cursor.close()
    conn.close()
    return metrics
