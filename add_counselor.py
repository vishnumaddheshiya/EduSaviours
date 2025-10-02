from app import app, db, User

def add_counselor():
    with app.app_context():
        # Create all database tables
        print("Creating database tables...")
        db.create_all()
        
        # Check if counselor already exists
        if User.query.filter_by(username='counselor').first():
            print("\nCounselor user already exists")
            return
        
        # Create counselor user
        print("\nCreating counselor user...")
        counselor = User(
            username='counselor',
            email='counselor@university.edu',
            role='counselor'
        )
        counselor.set_password('counselor123')
        
        # Add to database
        db.session.add(counselor)
        db.session.commit()
        
        print("\nCounselor user created successfully!")
        print("Username: counselor")
        print("Password: counselor123")

if __name__ == '__main__':
    add_counselor()
