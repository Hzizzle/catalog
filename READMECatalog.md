# Item Catalog Project
## Project Description

Code Background:
This ReadMe explains the code behind a RESTful web application that has been built to catalog recipes for particular types of cuisines. The web application lists the recipes under a given cuisine and provides details on the recipe. The application also uses third party Oauth authentication through the oauth2 flow (via Google) to register and authenticate users. Only registered users have the ability to post, edit and delete their own items. The python code is written for python2 and uses the flask framework to construct the application.

Initial Setup:
1. Save the following files in your application directory:
  application.py
  client_secrets.json
  CreateCuisines.py
  database_setup.py
  "templates" folder (which contains 9 html files that form the basis of the website)

2. You will need to register a new project in the Google Developer Console. This will involve setting up a project with OAuth 2.0 access - a Client ID and Client Secret will be provided. These should be used in place of the two current values in the client_secrets.json file as well as renaming the project_id.

3. Run the database_setup.py file in terminal - this will create a SQLite database named recipecatalog.db. This creates three classes (the tables that will be populated and queried); these are User, Cuisine, Recipe.

4. Run CreateCuisines.py in order to pre-populate the Cuisines table in recipecatalog.db. This will create the 10 cuisines that will form the list for the web application.


Running the server:
1. Run the application.py file to launch the server locally. This runs it locally on http://localhost:8000/

2. Logging in will take you to the user login page on Google. This will authenticate you and allow you to add, edit or delete recipes for a particular cuisine. You cannot add a new cuisine but you can add, edit or delete a recipe for a particular cuisine.


API Queries:
There are two options:
1. List all the cuisines and recipes:
Use http://localhost:8000/cuisines/JSON to return a JSON object of all the cuisines and recipes in the database

2. List all the recipes for a given cuisine:
If you know the cuisine_id and recipe_id numbers (which you can identify from the paths in your browser or from the previous API query) then you can retrieve the information on a single recipe as follows:
http://localhost:8000/cuisines/<int:cuisine_id>/<int:recipe_id>/JSON
