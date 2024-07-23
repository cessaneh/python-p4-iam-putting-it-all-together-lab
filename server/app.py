#!/usr/bin/env python3

from flask import request, session, jsonify, make_response
from flask_restful import Resource, Api
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            
            if 'username' not in data or 'password' not in data:
                return make_response(jsonify({"error": "Missing username or password field"}), 422)
            
            new_user = User(
                username=data['username'],
                password=data['password'],  
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return make_response(jsonify(new_user.to_dict()), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({"error": "Username already exists"}), 422)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return make_response(jsonify(user.to_dict()), 200)
        return make_response(jsonify({"error": "Unauthorized"}), 401)

class Login(Resource):
    def post(self):
        data = request.get_json()
        if 'username' not in data or 'password' not in data:
            return make_response(jsonify({"error": "Missing username or password field"}), 422)
        
        user = User.query.filter_by(username=data['username']).first()
        if user and user.verify_password(data['password']):
            session['user_id'] = user.id
            return make_response(jsonify(user.to_dict()), 200)
        return make_response(jsonify({"error": "Invalid username or password"}), 401)


class Logout(Resource):
    def delete(self):
        user_id = session.pop('user_id', None)
        if user_id:
            return make_response('', 204)
        return make_response(jsonify({"error": "Unauthorized"}), 401)

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            recipes = Recipe.query.all()
            return make_response(jsonify([recipe.to_dict() for recipe in recipes]), 200)
        return make_response(jsonify({"error": "Unauthorized"}), 401)

    def post(self):
        user_id = session.get('user_id')
        if user_id:
            data = request.get_json()
            try:
                new_recipe = Recipe(
                    title=data['title'],
                    instructions=data['instructions'],
                    minutes_to_complete=data['minutes_to_complete'],
                    user_id=user_id
                )
                db.session.add(new_recipe)
                db.session.commit()
                return make_response(jsonify(new_recipe.to_dict()), 201)
            except KeyError as e:
                return make_response(jsonify({"error": f"Missing {e.args[0]} field"}), 422)
        return make_response(jsonify({"error": "Unauthorized"}), 401)

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
