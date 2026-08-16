import os
import psycopg
import requests
import logging
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/police_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()


def fetch_events():
    try:
        response = requests.get("https://polisen.se/api/events", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("API request failed: %s", e)
        raise
    except ValueError as e:
        logger.error("Invalid JSON received from Polisen API: %s", e)
        raise

def load_events(events):
    try: 
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        ) as connection: 

            inserted_count = 0
            skipped_count = 0

            with connection.cursor() as cursor: 

                for event in events:
                    cursor.execute(
                        """
                        INSERT INTO raw.police_events (
                            event_id,
                            payload,
                            ingested_at
                        )
                        VALUES (%s, %s, NOW())
                        ON CONFLICT (event_id) DO NOTHING;
                        """,
                        (
                            event["id"],
                            Jsonb(event),
                        ),
                    )

                    if cursor.rowcount == 1:
                        inserted_count += 1
                    else:
                        skipped_count += 1

        return inserted_count, skipped_count

    except psycopg.OperationalError as e:
        logger.error("Database connection failed: %s", e)
        raise
    except psycopg.Error as e:
        logger.error("Database error: %s", e)
        raise

def main():
    events = fetch_events()
    inserted_count, skipped_count = load_events(events)
    logger.info("Fetched: %s", len(events))
    logger.info("Inserted: %s", inserted_count)
    logger.info("Skipped: %s", skipped_count)

if __name__ == "__main__":
    main()