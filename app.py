from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import AuthError
from pymongo import MongoClient, errors
from werkzeug.wrappers import Request, Response
from functools import wraps
from collections import OrderedDict

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pitchfork

SPOTIPY_CLIENT_ID = 'e46b04d01bd14ddc881de79291aa9c18'
SPOTIPY_CLIENT_SECRET = 'b8bd7750a5b64a64a8cf4b53c6b4076a'

client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


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
            id_token = request.args.get('id_token')
            print('=============')
            print(id_token)
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            return f(user_id = uid, *args, **kwargs)
        except AuthError as autherror:
            print(autherror)
            return jsonify({"error": "Bad token or token was revoked"})
    return verify_token


@app.route("/follow", methods = ["POST"])
@auth_required
def follow(**kwargs):
    artist_id = request.get_json()["artist_id"]
    artist_name = request.get_json()["artist_name"]
    artist_dict = {
    "artist_id": artist_id,
    "artist_name": artist_name
    }
    users_coll = nardwuar_db['users']
    users_coll.update({"_id" : kwargs['user_id']}, { '$push': {"FollowedArtists":artist_dict}})
    return jsonify({"status": "success", "new followed artist" : artist_name})


@app.route("/unfollow", methods = ["POST"])
@auth_required
def unfollow(**kwargs):
    artist_id = request.get_json()["artist_id"]
    artist_name = request.get_json()["artist_name"]
    users_coll = nardwuar_db['users']
    users_coll.update({"_id" : kwargs['user_id']}, { '$pull' :{"FollowedArtists":{"artist_id": artist_id}}})

    return jsonify({"status": "success", "artist unfollowed" : artist_name})

#route for creating new user and getting existing user info
@app.route("/users", methods = ["POST", "GET"])
@auth_required
def users(**kwargs):
    if request.method == "GET":
        users_coll = nardwuar_db['users']
        return jsonify(list(users_coll.find({ '_id': kwargs['user_id']})))
    else:
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

#route for getting top 5 results given query (name of artist)
@app.route("/search", methods = ["GET"])
def searchResults():
    query = request.args.get('query')
    search_results = spotify.search(query,5,0,"artist")
    search_results = search_results['artists']['items']

    five_results= []
    for artist in search_results:
        five_results.append({"Name" : artist['name'], "id" : artist['id']})

    return jsonify(five_results)

#route for getting artist info given query (id of artist)
@app.route("/artist-info/<artist_id>", methods = ["GET"])
def searchArtistInfo(artist_id):
    artist = spotify.artist(artist_id)
    albumResults = spotify.artist_albums(artist_id)
    list_of_albums = albumResults['items']
    list_of_albums_names = []
    for item in list_of_albums:
        list_of_albums_names.append(item['name'])

    seen = set()
    seen_add=seen.add
    list_of_albums_names_no_duplicates = [x for x in list_of_albums_names if not (x in seen or seen_add(x))]
    albumList=[]
    artistInfo = {
        "Spotify":{
            "Artist Name": artist['name'],
            "Artist Photo 600x600": artist['images'][0]['url'],
            "Albums": list_of_albums_names_no_duplicates,
            "Genres": artist['genres'],
            "Total Number of Spotify Followers": artist['followers']['total']
        },
        "Pitchfork": albumList
    }

    for x in range(0,3):
        try:
            artist_name = artist['name']
            album_name = list_of_albums[x]['name']
            album_name_approx = album_name[:5]
            p=pitchfork.search(artist_name, album_name_approx)
            description = p.abstract()
            description = description[:-2]
            album_info = {
                "Album name": album_name,
                "Album description": description,
                "Album photo 640x640": list_of_albums[x]['images'][0]['url'],
                "Album year": p.year(),
                "Label": p.label(),
                "Best New Music":p.best_new_music(),
                "Album score": p.score()
            }
            albumList.append(album_info)
        except IndexError:
            break
    return jsonify(artistInfo)
