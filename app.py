from flask import Flask, jsonify, request, Response
from database.db import initialize_db
from database.models import Photo, Album
import json
from bson.objectid import ObjectId
import os
import urllib
import base64
import codecs
from flask_mongoengine import MongoEngine
from mongoengine import errors

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'host':'mongodb://mongo:27017/flask-database'
}
db = initialize_db(app)

def str_list_to_objectid(str_list):
    return list(
        map(
            lambda str_item: ObjectId(str_item),
            str_list
        )
    )

def object_list_as_id_list(obj_list):
    return list(
        map(
            lambda obj: str(obj.id),
            obj_list
        )
    )


# ----------
# PHOTO APIs
# ----------
# These methods are a starting point, implement all routes as defined in the specifications given in A+
@app.route('/listPhoto', methods=['POST'])
def add_photo():
    posted_image = request.files['file']
    posted_data = {key:request.form[key] for key in request.form}
    posted_data_arrs = request.form.to_dict(flat=False)

    # Check for default album
    def_album = Album.objects(name='Default').first()
    if not def_album:
        def_album = Album(name='Default', description='Default Album')
        def_album.save()

    photo = Photo(**posted_data)

    if 'tags' in posted_data_arrs:
        photo.tags = posted_data_arrs['tags']
    if 'albums' in posted_data_arrs:
        albums = []
        for album_id in posted_data_arrs['albums']:
            try:
                album = Album.objects(id=album_id).first()
                if album:
                    albums.append(album_id)
            except errors.ValidationError:
                pass
        photo.albums = albums
    elif not 'albums' in posted_data:
        photo.albums = []
    if not str(def_album.id) in photo.albums:
        photo.albums.append(def_album.id)
    photo.image_file.replace(posted_image)
    photo.save()

    output = {
        'message': 'Photo successfully created', 
        'id': str(photo.id) 
    }
    status_code = 201 

    return jsonify(output), status_code

@app.route('/listPhoto/<photo_id>', methods=['GET', 'PUT', 'DELETE'])
def get_photo_by_id(photo_id):
    photo = Photo.objects(id=photo_id).first()
    if photo:
        if request.method == 'GET':
            ## Photos should be encoded with base64 and decoded using UTF-8 in all GET requests with an image before sending the image as shown below
            base64_data = codecs.encode(photo.image_file.read(), 'base64')
            image = base64_data.decode('utf-8')
            ##########

            output =  {
                'name': photo.name, 
                'tags': photo.tags,
                'location': photo.location,
                'albums': [str(i) for i in photo.albums],
                'file': str(image)
            }
            status_code = 200
            return jsonify(output), status_code

        elif request.method == 'PUT':
            posted_data = {key:request.form[key] for key in request.form}
            posted_data_arrs = request.form.to_dict(flat=False)
            if request.files:
                posted_image = request.files['file']
            else:
                posted_image = None

            if 'tags' in posted_data_arrs:
                photo.tags = posted_data_arrs['tags']
            if 'name' in posted_data:
                photo.name = posted_data['name']
            if 'albums' in posted_data_arrs:
                photo.albums = posted_data_arrs['albums']
            if 'location' in posted_data:
                photo.location = posted_data['location']
            if posted_image:
                photo.image_file.replace(posted_image)
            photo.save()
            output = {
                'message': 'Photo successfully updated',
                'id': str(photo.id)
            }
            status_code = 200
            return jsonify(output), status_code

        elif request.method == 'DELETE':
            photo.delete()
            output = {
                'message': 'Photo successfully deleted', 
                'id': str(photo.id)
            }
            status_code = 200
            return jsonify(output), status_code

@app.route('/listPhotos', methods=['GET'])
def get_photos():
    tag = request.args.get('tag')
    albumName = request.args.get('albumName')
    photo_objects = []
    all_photo_objects = Photo.objects.all()
    if albumName is not None:
        album_id = Album.objects(name=albumName)
        photo_objects = Photo.objects(albums__in=album_id)

    elif tag is not None:
        for photo in all_photo_objects:
            for photo_tag in photo.tags:
                if tag == photo_tag:
                    photo_objects.append(photo)

    else:
        photo_objects = all_photo_objects

    photos = []
    for photo in photo_objects:
        base64_data = codecs.encode(photo.image_file.read(), 'base64')
        image = base64_data.decode('utf-8')
        photos.append({'name': photo.name, 'location': photo.location, 'file': image, 'albums': [str(i) for i in photo.album_names()]})
    return jsonify(photos), 200

# ----------
# ALBUM APIs
# ----------
@app.route('/listAlbum', methods=['POST'])
def add_album():
    posted_album = request.get_json()
    existing_album = Album.objects(name=posted_album['name']).first()
    if existing_album is None:
        album = Album(**posted_album)
        album.save()
        output = {
            'message': 'Album successfully created', 
            'id': str(album.id) 
        }
        status_code = 201 
        return jsonify(output), status_code
    else:
        output = {
            'message': 'Album already exists'
        }
        status_code = 409
        return jsonify(output), status_code

@app.route('/listAlbum/<album_id>', methods=['PUT', 'GET', 'DELETE'])
def get_album_by_id(album_id):
    album = Album.objects(id=album_id).first()

    if request.method == 'PUT':
        posted_album = {key:request.form[key] for key in request.form}
        if 'name' in posted_album:
            album.name = posted_album['name']
        if 'description' in posted_album:
            album.description = posted_album['description']
        album.save()
        output = {
            'message': 'Album successfully updated',
            'id': str(album.id)
        }
        status_code = 200
        return jsonify(output), status_code

    elif request.method == 'GET':
        if album:
            output = {
                'id': str(album.id),
                'name': album.name
            }
            status_code = 200
            return jsonify(output), status_code

    elif request.method == 'DELETE':
        if album:
            album.delete()
            output = {
                'message': 'Album successfully deleted', 
                'id': str(album.id)
            }
            status_code = 200
            return jsonify(output), status_code

@app.route('/listAlbums', methods=['GET'])
def all_albums():
    album_objects = Album.objects()

    albums = [{'name': i.name, 'id': str(i.id), 'description': i.description} for i in album_objects]
    output = {'albums': albums}
    status_code = 200
    return jsonify(output), status_code