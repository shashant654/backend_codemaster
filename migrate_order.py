from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate_order_columns():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        try:
            conn.execute(text("ALTER TABLE \"order\" ADD COLUMN payment_proof VARCHAR"))
            conn.execute(text("ALTER TABLE \"order\" ADD COLUMN transaction_id VARCHAR"))
            print("Successfully added columns to order table")
        except Exception as e:
            print(f"Error adding columns (might already exist): {e}")

if __name__ == "__main__":
    migrate_order_columns()
