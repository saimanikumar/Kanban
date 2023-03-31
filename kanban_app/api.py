from datetime import datetime
from flask import make_response
from flask_restful import Resource
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash

from .model import User, Todo_list, Card
from .database import db
import json



user_fields = {
    'id':   fields.Integer,
    'name':    fields.String,
    'email':    fields.String
}

list_fields = {
    'list_id' : fields.Integer,
    'list_name': fields.String,
    'description': fields.String,
    'tasks_completed': fields.Integer,
    'tasks_remaining': fields.Integer
}

card_fields = {
    'card_id' : fields.Integer,
    'card_title' : fields.String,
    'content': fields.String,
    'deadline': fields.String,
    'is_complete': fields.Integer,
}

summary_fields = {
    'tasks_completed' : fields.Integer,
    'tasks_remaining' : fields.Integer
}



get_user_parser = reqparse.RequestParser()
get_user_parser.add_argument('email', location='args')
get_user_parser.add_argument('password', location='args')

create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username', location='args')
create_user_parser.add_argument('email', location='args')
create_user_parser.add_argument('password', location='args')

update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('name', location='args')
update_user_parser.add_argument('email', location='args')
update_user_parser.add_argument('password', location='args')


###################################################

create_list_parser = reqparse.RequestParser()
create_list_parser.add_argument('email', location='args')
create_list_parser.add_argument('password', location='args')
create_list_parser.add_argument('list_name', location='args')
create_list_parser.add_argument('description', location='args')

get_delete_list_parser = reqparse.RequestParser()
get_delete_list_parser.add_argument('email', location='args')
get_delete_list_parser.add_argument('password', location='args')
get_delete_list_parser.add_argument('list_id', location='args')

update_list_parser = reqparse.RequestParser()
update_list_parser.add_argument('email', location='args')
update_list_parser.add_argument('password', location='args')
update_list_parser.add_argument('list_id', location='args')
update_list_parser.add_argument('list_name', location='args')
update_list_parser.add_argument('description', location='args')

#####################################################

create_card_parser = reqparse.RequestParser()
create_card_parser.add_argument('email')
create_card_parser.add_argument('password')
create_card_parser.add_argument('card_title')
create_card_parser.add_argument('content')
create_card_parser.add_argument('deadline')
create_card_parser.add_argument('percent')
create_card_parser.add_argument("list_id")

get_delete_card_parser = reqparse.RequestParser()
get_delete_card_parser.add_argument('email')
get_delete_card_parser.add_argument('password')
get_delete_card_parser.add_argument('card_id')

update_card_parser = reqparse.RequestParser()
update_card_parser.add_argument('email')
update_card_parser.add_argument('password')
update_card_parser.add_argument('card_title')
update_card_parser.add_argument('card_id')
update_card_parser.add_argument('content')
update_card_parser.add_argument('deadline')
update_card_parser.add_argument('percent')
update_card_parser.add_argument("list_id")


#############################################################

class NotFoundError(HTTPException):
    def __init__(self, status_code, message = ''):
        self.response = make_response(message, status_code)


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)


##############################################################

class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self):
        args = get_user_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        user = User.query.filter_by(email=email).first()
        if user is None:
            raise NotFoundError(status_code=404)
        elif not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="password is invalid" )
        else:
            return user

    @marshal_with(user_fields)
    def put(self):
        args = update_user_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        name = args.get("name", None)


        user = User.query.filter_by(email=email).first()

        if user is None:
            raise NotFoundError(status_code=404)
        elif not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )
        elif name is None:
            return user
        else:
            user.name = name
            db.session.commit()
            return user


    @marshal_with(user_fields)
    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username", None)
        email = args.get("email", None)
        password = args.get("password", None)
        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")

        if email is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="email is required")

        if "@" not in email:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Invalid email")

        user = db.session.query(User).filter((User.name == username) | (User.email == email)).first()
        if user:
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="Duplicate user") 
        
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=email,
            name=username,
            password=hash_and_salted_password,
        )

        db.session.add(new_user)
        db.session.commit()
        return new_user


#################################################################
 
class ListAPI(Resource):
    @marshal_with(list_fields)
    def get(self):
        
        args = get_delete_list_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        list_id = args.get("list_id", None)

        user = User.query.filter_by(email=email).first()
        if user is None:
            raise NotFoundError(status_code=404)
        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )

        li = Todo_list.query.filter_by(list_id=int(list_id)).first()
        if li is None or li.user_id != user.id:
            raise NotFoundError(status_code=404)
        else:
            return li

    @marshal_with(list_fields)  
    def put(self):
        
        args = update_list_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        list_id = args.get("list_id", None)
        list_title = args.get("list_name")
        list_description = args.get("description")

        user = User.query.filter_by(email=email).first()

        if user is None:
            raise NotFoundError(status_code=404)

        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )
        
        li = Todo_list.query.filter_by(list_id=list_id).first()
        if li is None or li.user_id != user.id:
            raise NotFoundError(status_code=404)

        if list_title != None:
            li.list_name = list_title
            db.session.commit()
        if list_description != None:
            li.description = list_description
            db.session.commit()

        return li


    @marshal_with(list_fields)   
    def post(self):

        args = create_list_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        name = args.get("list_name", None)
        description = args.get("description", None)

        user = User.query.filter_by(email=email).first()
        if user is None:
            raise NotFoundError(status_code=404)

        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )

        new_list = Todo_list(
            list_name=name,
            description=description,
            user_id=user.id
        )

        db.session.add(new_list)
        db.session.commit()
        return new_list


    def delete(self):
        args = get_delete_list_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        list_id = args.get("list_id", None)

        user = User.query.filter_by(email= email).first()
        if user is None:
            raise NotFoundError(status_code=404)


        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )

        li = Todo_list.query.filter_by(list_id=list_id).first()
        if li is None or li.user_id != user.id:
            raise NotFoundError(status_code=404)
        
        db.session.delete(li)
        db.session.commit()

###############################################################


class CardAPI(Resource):

    @marshal_with(card_fields)
    def get(self):
        args = get_delete_card_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        card_id = args.get("card_id", None)

        user = User.query.filter_by(email=email).first()
        if user is None:
            raise NotFoundError(status_code=404)

        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )
        
        if card_id is None:
            raise BusinessValidationError(status_code=400, error_code="BE4001", error_message="valid Card id is required")
        
        ci = Card.query.filter_by(card_id=int(card_id)).first()
        if ci is None:
            raise NotFoundError(status_code=404)

        li = Todo_list.query.filter_by(list_id=ci.li).first()
        if li is None or li.user_id != user.id:
            raise NotFoundError(status_code=404)
        else:
            return ci


    @marshal_with(card_fields)
    def put(self):

        args = update_card_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        list_id = args.get("list_id", None)
        card_id = args.get("card_id", None)
        card_title = args.get("card_title", None)
        content = args.get("content", None)
        deadline = args.get("deadline", None)
        percent = args.get("percent", None)

        user = User.query.filter_by(email=email).first()
        if user is None:
            raise NotFoundError(status_code=404)

        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )
        
        if list_id is None:
            raise BusinessValidationError(status_code=400, error_code="BE3001", error_message="valid List id is required")

        li = Todo_list.query.filter_by(list_id=int(list_id)).first()
    
        if li is None:
            raise NotFoundError(status_code=404)
        if li not in user.lists:
            raise BusinessValidationError(status_code=400, error_code="BE4001", error_message="valid card id is required")
        
        if card_id is None:
            raise NotFoundError(status_code=404)

       
        c1 = Card.query.filter_by(card_id=card_id).first()


        if c1 is None:
            raise NotFoundError(status_code=404) 
        if c1 not in li.cards:
            raise BusinessValidationError(status_code=400, error_code="BE4002", error_message="valid Card id is required")
        
        format = '%Y-%m-%d'
        if deadline != None:
            new_date = datetime.strptime(deadline, format)
            deadline = new_date
            c1.deadline = deadline
        if content != None:
            c1.content = content
        if percent != None:
            c1.is_complete = percent
        c1.li = list_id
        if card_title != None:
            c1.card_title = card_title

        todo_list = li
        todo_list.tasks_remaining += 1
        if percent == '100': 
            todo_list.tasks_completed += 1
            todo_list.tasks_remaining -= 1

        db.session.commit()
        return c1

    @marshal_with(card_fields)
    def post(self):

        args = create_card_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        list_id = args.get("list_id", None)
        card_title = args.get("card_title", None)
        content = args.get("content", None)
        deadline = args.get("deadline", None)
        percent = args.get("percent", None)

        user = User.query.filter_by(email=email).first()
        if user is None:
            raise NotFoundError(status_code=404)

        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )
        
        li = Todo_list.query.filter_by(list_id=list_id).first()
        if li is None:
            raise NotFoundError(status_code=404)
        
        format = '%Y-%m-%d'
        new_date = datetime.strptime(deadline, format)


        deadline = new_date


        todo_list = li
        todo_list.tasks_remaining += 1
        if percent == '100': 
            todo_list.tasks_completed += 1
            todo_list.tasks_remaining -= 1
        

        new_card = Card(
            card_title=card_title,
            content=content,
            deadline=deadline,
            li=list_id,
            is_complete=percent,
        )

        db.session.add(new_card)
        db.session.commit()
        return new_card


    def delete(self):
        args = get_delete_card_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        card_id = args.get("card_id", None)

        user = User.query.filter_by(email= email).first()
        if user is None:
            raise NotFoundError(status_code=404)


        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )

        if card_id is None:
            raise BusinessValidationError(status_code=400, error_code="BE4001", error_message="valid Card id is required")
        
        l = Card.query.filter_by(card_id=card_id).first()
        if l is None:
            raise NotFoundError(status_code=404)
        todo_list = Todo_list.query.filter_by(list_id=l.li).first()        
        if l.is_complete == 100:
            todo_list.tasks_completed -= 1
        else:
            todo_list.tasks_remaining -= 1

        db.session.delete(l)
        db.session.commit()



class summaryAPI(Resource):
    @marshal_with(summary_fields)
    def get(self):
        args = get_delete_list_parser.parse_args()
        email = args.get("email", None)
        password = args.get("password", None)
        list_id = args.get("list_id", None)
        user = User.query.filter_by(email= email).first()
        if user is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="valid email is required")


        if not check_password_hash(user.password, password):
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="Invalid password" )

        if list_id is None:
            raise BusinessValidationError(status_code=400, error_code="BE3001", error_message="valid List id is required")
        
        li = Todo_list.query.filter_by(list_id=list_id).first()
        if li is None or li.user_id != user.id:
            raise NotFoundError(status_code=404)
        
        return li
