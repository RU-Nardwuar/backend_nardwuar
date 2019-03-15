from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials
from pymongo import MongoClient
from werkzeug.wrappers import Request, Response
# client = MongoClient()
cred = credentials.Certificate('nardwuar-958fc-firebase-adminsdk-4euwu-f815d4afc9.json')
default_app = firebase_admin.initialize_app(cred)
app=Flask(__name__)

#database for users
# users_db = client['users-db']

#route for user registration
@app.route("/register", methods = ["POST"])
def users():
     #need id_token from frontend
     id_token = request.get_json()["id_token"]
     #verify_id_token() verifies signature and data for provided JWT. Returns a dictionary of key-value pairs parsed from the decoded JWTself.
     #raises ValueError if jwt was found t be invalid,
     #raises AuthError if check_revoked is requested and token was revoked
     try:
         decoded_token = auth.verify_id_token(id_token)
         uid = decoded_token['uid']
         newUser = {
         "id": uid,
         "Name": request.get_json()["Name"],
         "Username": request.get_json()["Username"],
         "FollowedArtists": []
         }
         # users_db.insert_one(newUser)
         response ={
         "status":"Success",
         "message":"Account created!"
         }
         return jsonify(data);

     except ValueError:
         return jsonify({"error": "Bad Token"})
     except AuthError:
         return jsonify({"error:" "Token was revoked"})
#
# @app.route("/artists", methods = ["GET"])
# @auth_required
# def getInfoForLogin():
#     return jsonify()
#
#
# class LoginError(werkzeug.exceptions.HTTPException):
#      code = 401
#      def __init__(self, message):
#          self.message = message
#
# app.register_error_handler(LoginError, handle_401)
#
# def auth_required(f):
#    @wraps(f)
#     def verify_token(*args, **kwargs):
#         try:
#             id_token = request.get_json()["id_token"]
#             decoded_token = auth.verify_id_token(id_token)
#         except:
#             response
