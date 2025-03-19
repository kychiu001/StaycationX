import os
import subprocess
import time
import json
import pytest
from dotenv import load_dotenv
import shutil

from app.extensions import db, login_manager, cors
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app import create_app
from bson import decode_all
from app.extensions import db

load_dotenv()

# # The "autouse=True" means that this fixture will be automatically used by all the tests.
# @pytest.fixture(scope='session', autouse=True)
# def setup_app():

# Define the path for the test database
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_db')  # This will create a 'test_db' directory in the 'tests' folder

# Use the same DB path as your application
TEST_DB_NAME = 'test_staycation'

# Fixture to start MongoDB
@pytest.fixture(scope='session', autouse=True)
def start_mongodb():
    print("Starting MongoDB...")
    host = get_host('db')
    try:
        client = MongoClient(host, 27017, serverSelectionTimeoutMS=1000)
        client.admin.command('ping')
        print("MongoDB is already running.")
    except ConnectionFailure:
        # Create test_db directory if it doesn't exist
        os.makedirs(TEST_DB_PATH, exist_ok=True)
        
        # Modified MongoDB startup command
        process = subprocess.Popen([
            'mongod',
            '--dbpath', TEST_DB_PATH,
            '--unixSocketPrefix', TEST_DB_PATH,  # Use test directory for sockets
            '--bind_ip', host             # Explicit local binding
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait longer for startup
        time.sleep(10)
        yield
        process.terminate()
        process.wait()
    else:
        yield

# Setup Flask app
@pytest.fixture(scope='session', autouse=True)
def setup_app():
    # Configure test environment
    original_env = os.environ.copy()
    
    # Set required environment variables
    os.environ.update({
        'MOZ_HEADLESS': '1',  # Add other variables as needed
        'SELF_TESTING' : '1'
    })
    
    app = create_app()
    
    app.config['MONGODB_SETTINGS'] = {
        'db': TEST_DB_NAME,
        'host': get_host('db')  # Use the helper function to determine the database host
    }
    
    with app.app_context():    
        db.init_app(app)
        yield app
        
    os.environ.clear()
    os.environ.update(original_env)

# Fixture to load data into MongoDB
@pytest.fixture(scope='session', autouse=True)
def load_db_data(start_mongodb, setup_app):
    
    # Get raw PyMongo connection from MongoEngine
    try:
        # Attempt to establish connection
        pymongo_db = db.connection[TEST_DB_NAME]
        
        # Verify connection is working by executing a simple command
        pymongo_db.command('ping')
        
        print(f"Successfully connected to MongoDB test database: {TEST_DB_NAME}")
        
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise e
    
    # Load BSON files directly into collections
    collections = {
        'appUsers': 'db_seed/staycation/appUsers.bson',
        'booking': 'db_seed/staycation/booking.bson',
        'staycation': 'db_seed/staycation/staycation.bson'
    }

    for collection_name, file_path in collections.items():
        with open(file_path, 'rb') as f:
            # Decode BSON documents
            documents = decode_all(f.read())
            if documents:
                # Insert using PyMongo but maintain MongoEngine compatibility
                pymongo_db[collection_name].insert_many(documents)

    yield

    # Cleanup using MongoEngine connection
    db.connection.drop_database(TEST_DB_NAME)
    
    # Remove the database directory from the file system
    db_path = os.path.join(TEST_DB_PATH)
    if os.path.exists(db_path):
        shutil.rmtree(db_path)

# Add new fixture to run the Flask server
@pytest.fixture(scope="session")
def live_server(setup_app):
    # Configure app
    app = setup_app
    server_name = f'{get_host("app")}:5000'  # Use the helper function to determine the application server name
    app.config.update(SERVER_NAME=server_name)
    
    # Start server thread
    import threading
    server = threading.Thread(
        target=app.run,
        kwargs={
            'use_reloader': False,
            'host': '0.0.0.0',  # Explicit host binding
            'port': 5000
        }
    )
    server.daemon = True  # Ensures thread dies with parent process
    server.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield

# Client fixture for testing
@pytest.fixture()
def client(setup_app):
    return setup_app.test_client()

def get_host(host_type='app'):
    """
    Determine the host based on the FLASK_ENV environment variable and the type of host requested.
    
    Args:
        host_type (str): The type of host to determine. Can be 'app' for the application server or 'db' for the database.
    
    Returns:
        str: The appropriate host based on the environment and type.
    """
    env = os.getenv('FLASK_ENV', 'development')
    if host_type == 'db':
        if env == 'development':
            return 'localhost'
        else:
            return 'db'
    else:  # host_type == 'app'
        if env == 'development':
            return 'localhost'
        else:
            return 'frontend'