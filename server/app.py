from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        all_messages = Message.query.order_by(Message.created_at.asc())

        message_dicts = [message.to_dict() for message in all_messages]

        response = make_response(
            jsonify(message_dicts),
            200
        )

        return response
    
    elif request.method == 'POST':
        new_message = Message(
            body=request.get_json()["body"],
            username=request.get_json()["username"]
        )

        db.session.add(new_message)
        db.session.commit()

        message_dict = new_message.to_dict()

        response = make_response(
            jsonify(message_dict),
            201
        )

        return response


@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()

    if not message:
        response_body = { "message": "Record not found, please try again." }

        response = make_response(
            jsonify(response_body),
            404
        )

        return response
    
    else:
        if request.method == 'GET':
            message_dict = message.to_dict()

            response = make_response(
                jsonify(message_dict),
                200
            )

            return response
        
        elif request.method == 'PATCH':
            for attr in request.get_json():
                setattr(message, attr, request.get_json()[attr])
            
            db.session.add(message)
            db.session.commit()

            message_dict = message.to_dict()

            response = make_response(
                jsonify(message_dict),
                200
            )

            return response
        
        elif request.method == 'DELETE':
            db.session.delete(message)
            db.session.commit()

            response_body = { "message": "Record successfully deleted!" }

            response = make_response(
                jsonify(response_body),
                200
            )

            return response


if __name__ == '__main__':
    app.run(port=5555)
