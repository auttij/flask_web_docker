## Introduction
The code in this repo is part of an assignment for the Aalto-university course CS-E4190 - Cloud Software and Systems

The goal of the assignment was to implement and dockerize a web-bvased service leveraging [Flask](https://flask.palletsprojects.com/en/2.0.x/).

As the assignment was about getting the server and database working together, there is no front-end, and the use of a service such as [Postman](https://www.postman.com/) is adviced.

You can run the container with 
```
docker-compose up -d
```

## Schemas
`Photo`, used in the '**photo**' collection:
|Attribute|Type|Conditions|Values|
|:--:|:--:|:--:|:--:|
|name|String|required: true|Any valid string|
|tags|List|-|[Any valid strings]|
|location|String|-|Any vlaid string|
|image_file|Image|required: true|Any valid image file|
|albums|List of Album|-|[albumIds]|

`Album`, used in the '**album**' collection:
|Attribute|Type|Conditions|Values|
|:--:|:--:|:--:|:--:|
|name|String|required: true unique:true|Any valid string|
|description|String|-|Any valid string|

## Operations
`Photo`:
|Request|Type|Route|Request Body|Response Body|Response Status Code|
|:--:|:--:|:--:|:--:|:--:|:--:|
|Create|POST|/listPhoto|Photo (**)|{message: 'Photo succesfully created', id: `photo_id`}|201|
|Read|GET|/listPhoto/{photo_id}|-|	Single database object { name: `name`, tags: [`tags`], location: `location`, albums: [`albums`], file: `image_file` }|200|
|Read|GET|/listPhotos|tag (*)|Multiple database objects [{name: `name`, location: `location`, file: `image_file`}]|200|
|Read|GET|/listPhotos|albumName (*)|Multiple database objects [{name: `name`, location: `location`, file: `image_file`}]|200|
|Update|PUT|/listPhoto/{photo_id}|Photo (~)|	{ message: ‘Photo successfully updated’, id: `photo_id`}|200|
|Delete|DELETE|/listPhoto/{photo_id}|-|	{ message: ‘Photo successfully deleted’, id: `photo_id` }|200|

(*) This is a query string
(**) The request body is a multi-part form
(~) `image_file` is not sent as part of request body. The remaining `Photo` is sent as json.

All the images by default are placed in an `Album` with the name `Default`. When any `Photo` entry is created the POST method should check if the default album exists and create it if it does not. Each image belongs to the default Album as well as to any additional albums to which it is added to. The albumName in GET /listPhotos is optional, thus, it could be empty. In the latter case, the default `Album` should be used.

`Album`
|Request|Type|Route|Request Body|Response Body|Response Status Code|
|:--:|:--:|:--:|:--:|:--:|:--:|
|Create|POST|/listAlbum|Album|{ message: ‘Album successfully created’, id: `album_id` }|201|
|Read|GET|/listAlbum/{album_id}|-|Single database object { id: `album_id`, name: `name`}|200|
|Update|PUT|/listAlbum/{album_id}|Album|{ message: ‘Album successfully updated’, id: `album_id` }|200|
|Delete|DELETE|/listAlbum/{album_id}|-|{ message: ‘Album successfully deleted’, id: `album_id` }|200|


All /listAlbum requests use JSON in their request body.