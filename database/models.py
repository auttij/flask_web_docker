from .db import db

class Album(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField()

class Photo(db.Document):
    name = db.StringField(required=True)
    tags = db.ListField(db.StringField())
    location = db.StringField()
    image_file = db.ImageField(required=True)
    albums = db.ListField()

    def album_names(self):
        return [Album.objects(id=i).first().name for i in self.albums]