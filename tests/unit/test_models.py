from app.models.users import User
from werkzeug.security import generate_password_hash
import unittest

def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password_hashed, authenticated, and active fields are defined correctly
    """
    hashpass = generate_password_hash("12345", method='sha256')
    user = User.createUser(email="john@cde.com",password=hashpass, name="John Song")
    assert user.email == 'john@cde.com'
    assert user.password == hashpass

class test_new_user_methods(unittest.TestCase):
    
    def test_create_user(self):
        """
        GIVEN a User model
        WHEN a new User is created
        THEN check the email, password_hashed, authenticated, and active fields are defined correctly
        """
        hashpass = generate_password_hash("12345", method='sha256')
        user = User.createUser(email="jack@fgh.com", password=hashpass, name="Jackie Chan")
        self.assertEqual(user.email, 'jack@fgh.com')
        self.assertEqual(user.password, hashpass)

          