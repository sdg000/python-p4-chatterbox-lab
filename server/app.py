from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# allow cross origin access from frontend
CORS(app)

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return 'backend startup'

@app.route('/messages', methods=['GET', 'POST'])
def messages():

    # handling GET Request
    if request.method == 'GET':

        # fetching all messages
        messages = Message.query.all()

        messages_list = []

        for message in messages:

            messages_dict = {
                'id': message.id,
                'username': message.username,
                'body': message.body,
            }
            messages_list.append(messages_dict)
        response = make_response(
            jsonify(messages_list),
            200
        )

        return response

    # handling POST Request
    if request.method == 'POST':

        # get params from frontend
        data = request.get_json()

        if not data:
            response = make_response(
                'Invalid JSON data'
            )

        new_message = Message(
            username = data.get('username'),
            body = data.get('body') 
        )

        db.session.add(new_message)
        db.session.commit()
        
        mew_message_dict = new_message.to_dict()

        response = make_response(
            mew_message_dict,
            200
        )

        return response


@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    
    message = Message.query.filter(Message.id == id).first()

    if not message:
        response = make_response(
            'not found',
            404
        )
        return response
    
    # handling DELETE Request 
    if request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
            'delete_successful': True,
            'message': 'Messaege Deleted'
        }

        response = make_response(
            response_body,
            200
        )

        return response
    

    # handling PATCH requests
    if request.method == 'PATCH':

        # get UPDATE params from frontend
        data = request.get_json()

        # check if update param contains values that can update found INSTANCE
        if 'username' in data:
            message.username = data['username']

        if 'body' in data:
            message.body = data['body']

        # save updated instance
        db.session.add(message)
        db.session.commit()

        # convert updated INSTANCE to dictionary and return
        message_dict = message.to_dict()
        response = make_response(
            message_dict,
            200
        )

        return response




if __name__ == '__main__':
    app.run(port=5555, debug=True)
