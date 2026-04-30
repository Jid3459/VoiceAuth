"""
Script to create a superuser/admin account
Run: python create_superuser.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, init_db
from app.models import User, SystemSettings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_superuser():
    """Create a superuser account"""
    init_db()
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("CREATE SUPERUSER")
        print("=" * 50)
        
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        password_confirm = input("Confirm Password: ").strip()
        
        if password != password_confirm:
            print("❌ Passwords do not match!")
            return
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return
        
        # Create superuser
        hashed_password = pwd_context.hash(password)
        
        superuser = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=True,
            is_superuser=True
        )
        
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        print("\n✅ Superuser created successfully!")
        print(f"   ID: {superuser.id}")
        print(f"   Username: {superuser.username}")
        print(f"   Email: {superuser.email}")
        print(f"   Is Admin: {superuser.is_admin}")
        print(f"   Is Superuser: {superuser.is_superuser}")
        print("\n" + "=" * 50)
        
        # Initialize system settings if not exists
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings()
            db.add(settings)
            db.commit()
            print("✅ System settings initialized with default values")
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()