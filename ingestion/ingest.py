import os
import psycopg
import requests
import logging
from dotenv import load_dotenv
from psycopg.types.json import Jsonb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "police_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

def get_database_config():
    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_variables)}"
        )

    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def fetch_events():
    try:
        response = requests.get("https://polisen.se/api/events", timeout=30)
        response.raise_for_status()
        events = response.json()
        validate_events(events)
        return events
    except requests.RequestException as e:
        logger.error("API request failed: %s", e)
        raise
    except ValueError as e:
        logger.error("Invalid JSON received from Polisen API: %s", e)
        raise

def validate_events(events):
    if not isinstance(events, list):
        raise ValueError("API response is not a list")

    for event in events:
        if not isinstance(event, dict):
            raise ValueError("API response contains a non-object event")

        if "id" not in event:
            raise ValueError("Event is missing required field: id")

def load_events(events):
    db_config = get_database_config()
    try: 
        with psycopg.connect(**db_config) as connection: 

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