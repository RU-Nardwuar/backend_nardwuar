from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, auth
from pymongo import MongoClient
from werkzeug.wrappers import Request, Response
from functools import wraps

import spotipy
import pitchfork_api

spotify = spotipy.Spotify()

client = MongoClient('mongodb+srv://admin:greenpizza@cluster0-fhxen.mongodb.net/test?retryWrites=true')
cred = credentials.Certificate('nardwuar-958fc-firebase-adminsdk-4euwu-f815d4afc9.json')
default_app = firebase_admin.initialize_app(cred)

app=Flask(__name__)

#database for users
users_db = client['users-db']

def auth_required(f):
    @wraps(f)
    def verify_token(*args, **kwargs):
        try:
            id_token = request.get_json()["id_token"]
            decoded_token = auth.verify_id_token(id_token)
        except:
            return jsonify({"error": "Bad token or token was revoked"})
        return f(*args, **kwargs)
    return verify_token

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
         users_db.insert_one(newUser)
         response ={
         "status":"Success",
         "message":"Account created!"
         }
         return jsonify(response);

     except ValueError:
         return jsonify({"error": "Bad Token"})
     except auth.AuthError:
         return jsonify({"error:" "Token was revoked"})


@app.route("/artists", methods = ["GET"])
@auth_required
def getInfoForLogin():
    user = users_db.find_one({"id": decoded_token['uid']})
    return jsonify(user["FollowedArtists"])


@app.route("/basicArtistInfo", methods = ["GET"])
def searchArtistInfo(artistName):
    results = spotify.search(artistName,1,0, "artist")
    artist = results['artists']['items'][0]
    artistID = artist['id']
    album = spotify.artist_albums(artistID)
    album = album['items']
    artistInfo = {
    "Artist Name": artist['name'],
    "Albums": album,
    "Genres": artist['genres'],
    "Total Number of Spotify Followers": artist['followers']['total']
    }
    return jsonify(artistInfo)

@app.route("/artistRating", methods = ["GET"])
def getArtistRating(artistName, albumName):
    p = pitchfork.search(artistName, albumName)
    artistInfo ={
    "Album description": p.abstract(),
    "Album year": p.year(),
    "Label": p.label(),
    "Album score": p.score()
    }
    return jsonify(artistInfo)
