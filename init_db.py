#!/usr/bin/env python3
"""
Database initialization script for the Dropout Prediction System
Creates tables with an admin user
"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create admin user if it doesn't exist"""
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@university.edu',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        return ['admin']
    return []

def create_counselor():
    """Create counselor user if it doesn't exist"""
    if not User.query.filter_by(username='counselor').first():
        counselor = User(
            username='counselor',
            email='counselor@university.edu',
            role='counselor'
        )
        counselor.set_password('counselor123')
        db.session.add(counselor)
        db.session.commit()
        return ['counselor']
    return []

def main():
    """Initialize the database with admin and counselor users"""
    with app.app_context():
        # Create all database tables
        print("Initializing database tables...")
        db.create_all()
        
        # Create admin and counselor users
        print("Creating admin and counselor users...")
        created_users = []
        created_users.extend(create_admin_user())
        created_users.extend(create_counselor())
        
        if created_users:
            print(f"Created users: {', '.join(created_users)}")
        else:
            print("No new users created (already exist)")
        
        print("\nDatabase initialized successfully!")
        print("\nLogin Credentials:")
        print("-" * 50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nCounselor:")
        print("  Username: counselor")
        print("  Password: counselor123")
        
        print("\nYou can now run the application with: python run.py")

if __name__ == "__main__":
    main()
