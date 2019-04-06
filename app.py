from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, auth
from pymongo import MongoClient, errors
from werkzeug.wrappers import Request, Response
from functools import wraps

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pitchfork_api

SPOTIPY_CLIENT_ID = 'e46b04d01bd14ddc881de79291aa9c18'
SPOTIPY_CLIENT_SECRET = 'b8bd7750a5b64a64a8cf4b53c6b4076a'

client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


#SPOTIPY_REDIRECT_URI =


client = MongoClient('mongodb+srv://admin:greenpizza@cluster0-fhxen.mongodb.net/test?retryWrites=true')
cred = credentials.Certificate('nardwuar-7e6fc-firebase-adminsdk-lzorg-8d67ef20d9.json')
default_app = firebase_admin.initialize_app(cred)

app=Flask(__name__)

#database for users
nardwuar_db = client['nardwuar-db']

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
@app.route("/users", methods = ["POST"])
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
         "_id": uid,
         "Name": request.get_json()["name"],
         "Username": request.get_json()["username"],
         "FollowedArtists": []
         }
         users_coll = nardwuar_db['users']
         users_coll.insert_one(newUser)
         response ={
         "status":"Success",
         "message":"Account created!"
         }
         return jsonify(response)

     except errors.DuplicateKeyError:
         return jsonify({"error": "Account already exists"})

     except ValueError as e:
         return jsonify({"error": "Bad Token"})

     except auth.AuthError:
         return jsonify({"error": "Token was revoked"})

@app.route("/artistInfo", methods = ["GET"])
def searchArtistInfo():
    artist_name = request.get_json()["artist_name"]
    results = spotify.search(artist_name,1,0, "artist")
    artist = results['artists']['items'][0]
    artistID = artist['id']

    albumResults = spotify.artist_albums(artistID)
    list_of_albums = albumResults['items']
    list_of_albums_names = []
    for item in list_of_albums:
        list_of_albums_names.append(item['name'])

    artistInfo = {
        "Spotify":{
            "Artist Name": artist['name'],
            "Albums": list_of_albums_names,
            "Genres": artist['genres'],
            "Total Number of Spotify Followers": artist['followers']['total']
        },
        "Pitchfork":{
        }
    }

    for x in range(3):
        try:
            album_name = list_of_albums_names[x]
            p=pitchfork_api.search(artist_name, album_name)
            album_info = {
                "Album description": p.abstract(),
                "Album year": p.year(),
                "Label": p.label(),
                "Album score": p.score()
            }
            artistInfo['Pitchfork'].update({album_name : album_info})

        except IndexError:
            break
    return jsonify(artistInfo)
