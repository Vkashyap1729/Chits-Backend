from flask import Flask
from models.models import db, User  # Import from models/models.py

app = Flask(__name__)

# Configure your database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:sXR1NoMSViTkVbpWYptU@database-2.cpqmia86eaxm.ap-south-1.rds.amazonaws.com:3306/chitManagementSystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

@app.route('/use', methods=['GET'])
def get_users():
    # Query the User model to get all users
    users = User.query.all()  # This fetches all rows from the users table

    # Format the results as a list of dictionaries
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        })

    return {'users': users_list}

if __name__ == '__main__':
    app.run(debug=True)
