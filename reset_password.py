from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash
import getpass

def reset_password():
    db = SessionLocal()
    try:
        print("🔐 Reset User Password")
        email = input("Enter Email: ")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User with email {email} not found.")
            return

        new_password = getpass.getpass("Enter New Password: ")
        confirm_password = getpass.getpass("Confirm New Password: ")
        
        if new_password != confirm_password:
            print("❌ Passwords do not match!")
            return
            
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        print(f"✅ Password for {user.name} ({email}) has been reset successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
