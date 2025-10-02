from app import app, db, User
from werkzeug.security import generate_password_hash

def create_counselor():
    with app.app_context():
        # Check if counselor already exists
        if User.query.filter_by(username='counselor').first():
            print("Counselor user already exists")
            return
        
        # Create counselor user with properly hashed password
        counselor = User(
            username='counselor',
            email='counselor@university.edu',
            role='counselor'
        )
        counselor.set_password('counselor123')
        
        # Add to database
        db.session.add(counselor)
        db.session.commit()
        print("Counselor user created successfully!")
        print("Username: counselor")
        print("Password: counselor123")

if __name__ == "__main__":
    create_counselor()
