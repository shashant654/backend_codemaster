from app.db.database import engine
from sqlalchemy import text

def add_admin_column():
    """Add is_admin column to user table manually"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='is_admin'"
            ))
            
            if result.fetchone():
                print("✅ Column 'is_admin' already exists.")
                return

            # Add column
            print("🔄 Adding 'is_admin' column...")
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✅ Column 'is_admin' added successfully!")
            
    except Exception as e:
        print(f"❌ Error migrating database: {e}")

if __name__ == "__main__":
    add_admin_column()
