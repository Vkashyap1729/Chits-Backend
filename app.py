from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.models import db, User, Chit, ChitManager,ChitMembers  
import pytz  # For timezone conversion
from flask_mail import Mail, Message
import random
app = Flask(__name__)

CORS(app)
# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "managementchit@gmail.com"  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = "avzr qeso zaei jwrq"    # Replace with the generated App Password

mail = Mail(app)
# Configure your database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:sXR1NoMSViTkVbpWYptU@database-2.cpqmia86eaxm.ap-south-1.rds.amazonaws.com:3306/chitManagementSystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Define IST Timezone
IST = pytz.timezone('Asia/Kolkata')

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

@app.route('/signUp', methods=['POST'])
def signUp():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    role = 1
    password = data.get('password')
    validated = False

    # Check if the user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User with this email already exists"}), 400
    
    # Create the new user instance
    new_user = User(email=email, name=name, password=password, role=role, validated=validated)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Respond with a success message
    return jsonify({'message': 'User created successfully', 'user': {
        'id': new_user.id,
        'email': new_user.email,
        'name': new_user.name,
        'role': new_user.role,
        'validated': new_user.validated,
        'otp': new_user.otp
    }}), 200

def generate_otp():
    return str(random.randint(100000, 999999))  # 6-digit OTP

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    type = data.get('type')

    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User dont have account"}), 400
    
    otp = generate_otp()  # Generate OTP

    if type == 'forgot_password':
        user.forgot_opt = otp
    elif type == 'signup':
        user.otp = otp
    else:
        return jsonify({"message": "Invalid type"}), 400
    
    # Save OTP in the database
    db.session.commit()
    msg = Message("Your OTP Code", sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f"Your OTP is {otp}. It is valid for 10 minutes."

    try:
        mail.send(msg)
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    type = data.get('type')
    if not id or not otp:
        return jsonify({"error": "Input fields are missing."}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "No user found."}), 400
    if type =='forgot_password':
        if user.forgot_opt == otp:
            return jsonify({"message": "Successfully validated"}), 200
        else:
            return jsonify({"message": "Invalid otp."}), 400
    # Assuming OTP is stored as a string
    if otp == user.otp:
        user.validated = 1
        db.session.commit()  # Commit to DB after successful validation
        return jsonify({"message": "Successfully validated"}), 200
    else:
        user.validated = 0
        db.session.commit()  # Commit to DB after invalid OTP
        return jsonify({"message": "Invalid otp."}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Querying the user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "You dont have an account yet SignUp."}), 400
    elif not user.validated :
        return jsonify({"message": "Please verify your email with otp."}), 400
    elif user.password != password:
        return jsonify({"message": "Invalid password."}), 400
    else:
        return jsonify({"message": "Login successful."}), 200
    
@app.route('/resetPassword', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validate input
    if not email or not password:
        return jsonify({"message": "Input data is missing."}), 400

    # Querying the user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "You don't have an account yet. Sign up."}), 400
    
    user.password = password
    # Commit changes to the database
    db.session.commit()

    return jsonify({"message": "Password reset was successful."}), 200
    
@app.route('/createChit', methods=['POST'])
def create_chit():
    try:
        data = request.get_json()
        
        # Convert provided startDate and endDate to IST
        start_date_ist = datetime.strptime(data.get('startDate'), '%Y-%m-%d').replace(tzinfo=pytz.utc).astimezone(IST)
        end_date_ist = datetime.strptime(data.get('endDate'), '%Y-%m-%d').replace(tzinfo=pytz.utc).astimezone(IST)

        new_chit = Chit(
            name=data.get('name'),
            tenure=data.get('tenure'),
            noOfPeople=data.get('noOfPeople'),
            amountPerMonth=data.get('amountPerMonth'),
            totalAmount=data.get('totalAmount'),
            startDate=start_date_ist,
            endDate=end_date_ist
        )

        db.session.add(new_chit)
        db.session.commit()
        
        chit_id = new_chit.id
        user_id = data.get('userId')  # Get the manager userId
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        
        new_manager = ChitManager(managerId=user_id, chitId=new_chit.id)
        db.session.add(new_manager)
        db.session.commit()

        return jsonify({'message': 'Chit created successfully', 'chit_id': chit_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/editChit', methods=['PUT'])
def edit_chit():
    try:
        data = request.get_json()
        chit_id = data.get('id')

        if not chit_id:
            return jsonify({'error': 'Chit ID is required'}), 400

        chit = Chit.query.get(chit_id)
        if not chit:
            return jsonify({'error': 'Chit not found'}), 404

        # Update fields if provided
        if 'name' in data:
            chit.name = data['name']
        if 'tenure' in data:
            chit.tenure = data['tenure']
        if 'noOfPeople' in data:
            chit.noOfPeople = data['noOfPeople']
        if 'amountPerMonth' in data:
            chit.amountPerMonth = data['amountPerMonth']
        if 'totalAmount' in data:
            chit.totalAmount = data['totalAmount']
        if 'startDate' in data:
            chit.startDate = datetime.strptime(data['startDate'], '%Y-%m-%d').replace(tzinfo=pytz.utc).astimezone(IST)
        if 'endDate' in data:
            chit.endDate = datetime.strptime(data['endDate'], '%Y-%m-%d').replace(tzinfo=pytz.utc).astimezone(IST)
        
        db.session.commit()
        return jsonify({'message': 'Chit updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/deleteChit', methods=['DELETE'])
def delete_chit():
    try:
        data = request.get_json()
        chit_id = data.get('id')

        if not chit_id:
            return jsonify({'error': 'Chit ID is required'}), 400

        # Step 1: Find the chit
        chit = Chit.query.get(chit_id)
        if not chit:
            return jsonify({'error': 'Chit not found'}), 404

        # Step 2: Delete all ChitManager entries related to this chit_id
        chit_manager_records = ChitManager.query.filter_by(chitId=chit_id).all()
        for record in chit_manager_records:
            db.session.delete(record)

        # Step 3: Delete all ChitMembers entries related to this chit_id
        chit_member_records = ChitMembers.query.filter_by(chitId=chit_id).all()
        for record in chit_member_records:
            db.session.delete(record)

        # Step 4: Now, delete the Chit record
        db.session.delete(chit)
        db.session.commit()

        return jsonify({'message': 'Chit and related records deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# @app.route('/addChitMember', methods=['POST'])
# def add_chit_member():
#     try:
#         data = request.get_json()

#         chit_id = data.get('chitId')
#         manager_id = data.get('managerId')
#         lifted_month = data.get('liftedMonth')
#         name = data.get('name')

#         if not all([chit_id, manager_id, lifted_month, name]):
#             return jsonify({'error': 'All fields are required'}), 400

#         new_member = ChitMembers(
#             chitId=chit_id,
#             managerId=manager_id,
#             liftedMonth=lifted_month,
#             name=name
#         )

#         db.session.add(new_member)
#         db.session.commit()

#         return jsonify({'message': 'Chit member added successfully'}), 201

#     except Exception as e:
#         return jsonify({'error': str(e)}), 400


# @app.route('/editChitMember', methods=['PUT'])
# def edit_chit_member():
#     try:
#         data = request.get_json()
#         member_id = data.get('id')

#         if not member_id:
#             return jsonify({'error': 'Member ID is required'}), 400

#         chit_member = ChitMembers.query.get(member_id)

#         if not chit_member:
#             return jsonify({'error': 'Chit member not found'}), 404

#         # Update fields only if they are provided in the request
#         chit_member.chitId = data.get('chitId', chit_member.chitId)
#         chit_member.managerId = data.get('managerId', chit_member.managerId)
#         chit_member.liftedMonth = data.get('liftedMonth', chit_member.liftedMonth)
#         chit_member.name = data.get('name', chit_member.name)

#         db.session.commit()

#         return jsonify({'message': 'Chit member updated successfully'}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @app.route('/removeChitMember', methods=['DELETE'])
# def remove_chit_member():
#     try:
#         member_id = request.args.get('id')

#         if not member_id:
#             return jsonify({'error': 'Member ID is required'}), 400

#         chit_member = ChitMembers.query.get(member_id)

#         if not chit_member:
#             return jsonify({'error': 'Chit member not found'}), 404

#         db.session.delete(chit_member)
#         db.session.commit()

#         return jsonify({'message': 'Chit member removed successfully'}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @app.route('/updateChitStatus', methods=['POST'])
# def update_chit_status():
#     try:
#         data = request.get_json()
#         chit_id = data.get('chitId')
#         user_id = data.get('userId')
#         lifted_month = data.get('liftedMonth')

#         if not all([chit_id, user_id, lifted_month]):
#             return jsonify({'error': 'chitId, userId, and liftedMonth are required'}), 400

#         # Check if the chit exists
#         chit = Chit.query.get(chit_id)
#         if not chit:
#             return jsonify({'error': 'Chit not found'}), 404

#         # Check if the user exists
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({'error': 'User not found'}), 404

#         # Check if a record already exists for this chit and month
#         chit_member = ChitMembers.query.filter_by(chitId=chit_id, liftedMonth=lifted_month).first()

#         if chit_member:
#             # Update the existing record
#             chit_member.managerId = user_id
#         else:
#             # Create a new record if not exists
#             chit_member = ChitMembers(
#                 chitId=chit_id,
#                 managerId=user_id,
#                 liftedMonth=lifted_month,
#                 name=user.name  # Assuming we store the name of the user lifting the chit
#             )
#             db.session.add(chit_member)

#         db.session.commit()

#         return jsonify({'message': 'Chit status updated successfully'}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
