from app import app, User, db

def check_counselor():
    with app.app_context():
        counselor = User.query.filter_by(username='counselor').first()
        if counselor:
            print("Counselor user found:")
            print(f"Username: {counselor.username}")
            print(f"Email: {counselor.email}")
            print(f"Role: {counselor.role}")
            print(f"Password hash: {counselor.password_hash}")
        else:
            print("Counselor user not found in the database")

if __name__ == "__main__":
    check_counselor()
