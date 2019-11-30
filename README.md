# Pug or Ugh Django API

## Context

This project aims to allow **registered users** to search for **dogs** that are looking for a pet owner. Users can set up dog preferences (gender, age and/or size). Then, the dogs from the database are displayed and the user can classify them as: **liked, disliked** or **undecided**.

The following project uses **Django REST framework** to connect models, serializers, and views with an Angular application (provided code). 

HTML and CSS code has been provided for the mobile-friendly design. 

An [import data script](https://github.com/AaronMillOro/pug-or-ugh_django_rest/blob/master/backend/pugorugh/scripts/data_import.py) allows to import **Dogs information** from a JSON file. To be used, `DogSerializer` and `Dog` model have to be properly declared.

## Project details 

* Dogs information was imported usign  a `data_import` script: 

		python data_import.py

* The following **models** and associated field names are present as they will be expected by the JavaScript application.

	* `Dog` - This model represents a dog in the app. Fields:
		* `name`
		* `image_filename`
		* `breed`
		* `age`, integer for months
		* `gender`, "m" for male, "f" for female, "u" for unknown
		* `size`, "s" for small, "m" for medium, "l" for large, "xl" for extra large, "u" for unknown

	* `UserDog` -  This model represents a link between a user an a dog. Fields:
		* `user`
		* `dog`
		* `status`, "l" for liked, "d" for disliked

	* `UserPref` - This model contains the user's preferences. Fields:
		* `user`
		* `age`, "b" for baby, "y" for young, "a" for adult, "s" for senior
		* `gender`, "m" for male, "f" for female
		* `size`, "s" for small, "m" for medium, "l" for large, "xl" for extra  large
		* `age`, `gender`, and `size` can contain multiple, comma-separated values

* Serializers need to be created for both the `Dog` and `UserPref` models. Each of them should reveal all of the fields with one exception: the `UserPref` serializer doesn't need to reveal the user.


* The following routes are expected by the JavaScript application.

	* To get the next liked/disliked/undecided dog
		* `/api/dog/<pk>/liked/next/`
		* `/api/dog/<pk>/disliked/next/`
		* `/api/dog/<pk>/undecided/next/`

	* To change the dog's status
		* `/api/dog/<pk>/liked/`
		* `/api/dog/<pk>/disliked/`
		* `/api/dog/<pk>/undecided/`

	* To change or set user preferences
		* `/api/user/preferences/`

## Test the app on terminal

Create a virtualenv and install the project requirements, which are listed in `requirements.txt`

		pipenv install
		pipenv shell
		pip install -r requirements.txt

Run the app.

		python manage.py runserver 0.0.0.0:5000
		
Open your favorite web browser and type:
		
		http://localhost:50000/
		
![Figure display](https://github.com/AaronMillOro/pug-or-ugh_django_rest/blob/master/Screenshot_pug_or_ugh.png)

Enjoy! :shipit: