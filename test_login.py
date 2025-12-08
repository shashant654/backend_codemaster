from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import verify_password
import getpass

def test_login():
    db = SessionLocal()
    try:
        print("🕵️ Test Login Logic")
        email = input("Enter Email: ")
        password = getpass.getpass("Enter Password: ")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User with email {email} NOT FOUND in DB.")
            return

        print(f"✅ User found: {user.name}")
        print(f"   Is Admin: {user.is_admin}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Hashed Password: {user.hashed_password[:10]}...")
        
        if verify_password(password, user.hashed_password):
            print("✅ Password VERIFIED successfully!")
        else:
            print("❌ Password verification FAILED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_login()
