from sqlalchemy import create_engine, text
from app.core.config import settings

def check_columns():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Try to select the new columns
            conn.execute(text('SELECT payment_proof, transaction_id FROM "order" LIMIT 1'))
            print("Columns exist!")
        except Exception as e:
            print(f"Error selecting columns: {e}")

if __name__ == "__main__":
    check_columns()
