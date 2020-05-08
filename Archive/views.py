from run import app
from flask import jsonify


#building a home page
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to home directory for nutrics. Please access the /login endpoint to log in.'})