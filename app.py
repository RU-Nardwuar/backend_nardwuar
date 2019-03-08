from flask import Flask
# import firebase_admin
# from firebase_admin import credentials, auth
# from pymongo import MongoClient
# from werkzeug.wrapper import Request, Reponse
# client = MongoClient()
# cred = credentials.Certificate('/Users/jameswo/Documents/nardwuar-958fc-firebase-adminsdk-4euwu-f815d4afc9.json')
# default_app = firebase_admin.initialize_app(cred)
app = Flask(__name__)

# users_db = client['users-db']

@app.route("/")
def index():
    return "hello, world"

#route for user registration
# @app.route("/register", methods = ["POST"])
#
# def users():
#     #need id_token from frontend
#     id_token = request.get_json()["id token"]
#     #verify_id_token() verifies signature and data for provided JWT. Returns a dictionary of key-value pairs parsed from the decoded JWTself.
#     #raises ValueError if jwt was found t be invalid,
#     #raises AuthError if check_revoked is requested and token was revoked
#     try:
#         decoded_token = auth.verify_id_token(id_token)
#         uid = decoded_token['uid']
#         newUser = {
#         #have shared documentation
#         "id": uid,
#         "Name": request.get_json()["Name"],
#         "Username": request.get_json()["Username"]
#         }
#         users_db.insert_one(newUser)
#     except ValueError:
#         raise LoginError("fdsfjsdf")
#     except AuthError:
#         raise LoginError("fsdlj")


#authentication error --> http error 401
#value error --> http error 400
#https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vii-error-handling
#https://github.com/Salamander1012/FlaskDecoratorExample/blob/master/app.py#L27
#https://firebase.google.com/docs/reference/js/firebase.auth.Error.html#code

#An error handler is a normal view function that return a response, but instead of being registered for a route, it is registered for an exception or HTTP status code that would is raised while trying to handle a request.

#
# class LoginError(...):
#     code = 401
#     def __init__(self, message):
#         self.message = message
# @app.errorhandler(werkzeug.exceptions.HTTPException.BadRequest) #this refers to 400 error
# def valueError(error):
#     return 'Incorrect formatting, make sure all fields are completed', 400
#
# @app.errorhandler(werkzeug.exceptions.HTTPException.Unauthorized) #this refers to 401 error
# def authError(error):
#     return 'Authentication error, make sure email and password is correct', 401
#
#





#route for searching artists
#@app.route("/search", methods = ["GET"])
#def search():

#@app.route("/artists/{}")
