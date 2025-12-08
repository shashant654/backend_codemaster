from app.db.database import SessionLocal
from app.models.models import User
from app.core.security import get_password_hash
import getpass

def create_admin():
    db = SessionLocal()
    try:
        print("🚀 Create New Admin User")
        name = input("Enter Name: ")
        email = input("Enter Email: ")
        password = getpass.getpass("Enter Password: ")
        
        # Check if exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"⚠️  User with email {email} already exists.")
            choice = input(f"Do you want to promote {user.name} to Admin? (y/n): ")
            if choice.lower() == 'y':
                user.is_admin = True
                db.commit()
                print(f"✅ User {user.name} is now an Admin!")
            return

        # Create new user
        new_user = User(
            name=name,
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_instructor=False,
            is_admin=True,
            avatar="https://github.com/shadcn.png" # Default avatar
        )
        
        db.add(new_user)
        db.commit()
        print(f"✅ Admin user {name} ({email}) created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
