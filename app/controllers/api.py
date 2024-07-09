from flask import jsonify, request, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

# Specific to API
from flask_httpauth import HTTPBasicAuth
from bson import json_util

# Import the models
from app.models.users import User
from app.models.package import Package
from app.models.token import UserTokens
from app.models.book import Booking

from app.utils.api import extract_keys

api = Blueprint('api', __name__)

# This is protect the API routes using HTTP Basic Authentication
api_auth = HTTPBasicAuth()

# The API route to get a token
@api.route('/api/user/gettoken', methods=['POST'])
def api_gettoken():
    if request.method == 'POST': 

        # To handle both JSON payloads (commonly used with JavaScript or ReactJS) 
        # and form data (which can be sent from a Python script or a HTML form).
        try:
            data = request.json
            if data: # if using ReactJS
                email = data['email']
                password = data['password']
        except: # if using python
            email = request.form.get('email')
            password = request.form.get('password')

        # from OneMap: 400 - You have to enter a valid email address and valid password to generate a token.
        if not email or not password:
            return jsonify({'error': 'You have to enter a valid email address and valid password'}), 400 

        # from OneMap: 404 - User is not registered in system.
        user = User.getUser(email=email)
        if not user:
            return jsonify({'error': 'User is not registered'}), 404 

        # from OneMap: 401 - Authentication failed, please contact admin at support@onemap.gov.sg
        if not check_password_hash(user.password, password):
            return jsonify({'error': 'Authentication failed'}), 401 

        token =  UserTokens.getToken(email = email)
        
        # If token exists, return the token
        if token:
            return jsonify({'token': token}), 200

        current_datetime = datetime.now()
        datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # Simulated token generation (replace with actual token logic)
        token = generate_password_hash(user.email+datetime_str, method='sha256')
        UserTokens.createToken(email = user.email, token=token)
        token =  UserTokens.getToken(email = email)
        # Return the newly generated token
        return jsonify({'token': token}), 200

# The API route to get all packages  
@api.route('/api/package/getAllPackages', methods=['POST'])
@api_auth.login_required
def getAllPackages():
    allPackages = Package.getAllPackages()
    packages_list = [json.loads(json_util.dumps(package.to_mongo())) for package in allPackages]
    projected_list = [extract_keys(k, idx+1) for idx, k in enumerate(packages_list)]
    return jsonify({'data': projected_list}), 201

# The API route to get all packages  
@api.route('/api/book/newBooking', methods=['POST'])
@api_auth.login_required
def newBooking():
    try:
        # Date Format = 'YYYY-MM-DD'
        check_in_date = request.form.get("check_in_date")
        user_email = request.form.get("user_email")
        hotel_name = request.form.get("hotel_name")
    except Exception as e:
        return jsonify({"error": "Invalid data format"}), 400  # Bad Request

    # Process booking data (replace with your booking logic)
    # This is a placeholder, implement your booking logic here
    if check_in_date == '' or user_email == '' or hotel_name == '':
        return jsonify({"error": "Invalid data format"}), 400

    print(f"Booking received for: {user_email}, Hotel: {hotel_name}, Check-in: {check_in_date}")
    # You would typically save this data to a database or process the booking

    booking_user = User.getUser(email=user_email)
    booking_package = Package.getPackage(hotel_name=hotel_name)
    aBooking = Booking.createBooking(check_in_date, booking_user, booking_package) 

    return jsonify({"message": "Booking created successfully"}), 201  # Created

# The API route to manage bookings 
@api.route('/api/book/manageBooking', methods=['POST'])
@api_auth.login_required
def manageBooking():
    try:
        user_email = request.form.get("user_email")
    except Exception as e:
        return jsonify({f"error": "No booking under {user_email}"}), 400  # Bad Request
    
    booking_user = User.getUser(email=user_email)
    allBookings = Booking.getUserBookingsFromDate(booking_user, '1900-01-01')
    sorted_data_desc = sorted(allBookings, key=lambda d: d['check_in_date'], reverse=True)
    dereferenced_data = Booking.dereferenceBookings(sorted_data_desc)

    return jsonify({"message": "Booking retrieved successfully",
                    "data": dereferenced_data}), 201  # retrieved

# The API route to update a booking
@api.route('/api/book/updateBooking', methods=['POST'])
@api_auth.login_required
def updateBooking():
    try:
        user_email = request.form.get("user_email")
        new_check_in_date = request.form.get("new_check_in_date")
        old_check_in_date = request.form.get("old_check_in_date")
        hotel_name = request.form.get("hotel_name")
    except Exception as e:
        return jsonify({f"error": "No booking under {user_email}, {old_check_in_date} and {hotel_name}"}), 400  # Bad Request
    
    customer = User.getUser(email=user_email)
    if Booking.updateBooking(old_check_in_date, new_check_in_date, customer, hotel_name):
        return jsonify({"message": "Booking updated successfully"}), 201  # retrieved
    else:
        return jsonify({"message": "Booking update failed"}), 400

# The API route to delete a booking
@api.route('/api/book/deleteBooking', methods=['POST'])
@api_auth.login_required
def deleteBooking():
    try:
        user_email = request.form.get("user_email")
        check_in_date = request.form.get("check_in_date")
        hotel_name = request.form.get("hotel_name")
    except Exception as e:
        return jsonify({f"error": "No booking under {user_email}, {check_in_date} and {hotel_name}"}), 400  # Bad Request
    
    customer = User.getUser(email=user_email)

    if Booking.deleteBooking(check_in_date, customer, hotel_name):
        return jsonify({"message": "Booking delete successfully"}), 201  # retrieved
    else:
        return jsonify({"message": "Booking deletion failed"}), 400

# Protected route for authorized users
@api.route('/api/protected')
@api_auth.login_required
def protected():
    return jsonify({'message': 'You are authorized to see this message'}), 201

# Part of the basic authentication
@api_auth.verify_password
def verify_password(email, token):
    user = UserTokens.getToken(email=email)
    if user and user.token==token:
        return True
    else:
        return False
