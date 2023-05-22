from flask import request
import json
import logging
from ..utility import db 
from datetime import datetime 
from flask_restx import Namespace, Resource, fields
from ..models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from .serializer import signup_expect_model, signup_model, auth_namespace, login_expect_model


class DateTimeEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o , datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


@auth_namespace.route('/signup')
class SignUp(Resource):
   
   @auth_namespace.expect(signup_expect_model)
   @auth_namespace.marshal_with(signup_model)
   @auth_namespace.doc(description="Signup user")
   
   def post(self):
      
      logger = logging.getLogger(__name__)
      logger.info("Signup is called")
     
         
      data = request.get_json()
         
      first_name = data.get('first_name')
      last_name = data.get('last_name')     
      email = data.get('email')
      password = data.get('password')
         
      signup_try = User.query.filter_by(email=email).first()
         
      if signup_try:
         response = {"message" : "Email already exist"} 
         return response, HTTPStatus.BAD_REQUEST  
         
      new_user  = User (
         email=email, 
         password_hash = generate_password_hash(password)
      )
         
      try:
         new_user.save()
            
      except:
         db.session.rollback()
         response = {"message" : "An error occured"}
             
         return response, HTTPStatus.INTERNAL_SERVER_ERROR
         
      access_token = create_access_token(identity=new_user.email)
      refresh_token = create_refresh_token(identity=new_user.email)
      tokens = {
         'access_token' : access_token ,
            'refresh_token' : refresh_token
         }
         
      response = {
         'id': new_user.id,
         'email': new_user.email,
         'tokens': tokens
      }
      return response , HTTPStatus.CREATED 
  
  
@auth_namespace.route('/login')
class Login(Resource):
   
   @auth_namespace.expect(login_expect_model)
   @auth_namespace.doc(description = "Login user",
                       params = {"user input": "Email and password"})
   def post(self):
      
      
      logger = logging.getLogger(__name__)
      logger.info("Login is called")
      
      data = request.get_json()

      email = data.get("email")
      password = data.get("password")

      user = User.query.filter_by(email=email).first()

      if (user is not None) and check_password_hash(user.password, password):
         access_token = create_access_token(identity=user.email)
         refresh_token = create_refresh_token(identity=user.email)

         response = {
            'access_token': access_token,
            'refresh_token': refresh_token
         }
         
         logger.debug(f"User {user} logged in")

         return response, HTTPStatus.CREATED
      
      else:
         logger.warning("Invalid credentials")
         response = {"message": "Invalid credentials"} 
         return response , HTTPStatus.NOT_FOUND
     
@auth_namespace.route('/refresh')
class Refresh(Resource):

   @auth_namespace.doc(description = "Refresh access token of user login")
   @jwt_required(refresh=True)
   def post(self):
      email = get_jwt_identity()

      access_token = create_access_token(identity=email)

      return {"access_token": access_token}, HTTPStatus.OK