# Nutrics

Welcome to the Nutrics project. We think that choosing nutritious, local food should be easy, and we're building an application that does it for you.


## Local API Runtime Instructions:

```
git clone 'https://github.com/Big-Ideas-Lab/nutrics.git'
cd nutrics
conda create --name nutrics --file requirements.txt
conda activate nutrics
FLASK_APP=run.py FLASK_DEBUG=1 flask run
```

> Note: nutrics.db is not hosted on this GitHub page. We do not have permission to distribute this dataset, as much of the data in it doesn't belong to us. Please contact a member of the BIG IDEAs Lab for permission, or feel free to create your own using db_prep.py.

> Updated by Joshua D'Arcy on 4.22.2020

-------------

## Server API **Preparation:**

-------------

In order to keep our production API response times as quick as possible, the nutrics.db database is constructed offline using modules developed by the BIG IDEAs Lab. These modules include Nutrition.py and Palate.py. A file called db_prep.py offers a streamlined terminal application to facilitate this process.

### Nutrition.py

This file contains two classes. The Nutrients class uses natural language processing to estimate the nutritional value of food, and uses **clean_foods.csv**, which we were lended by Duke Nutrition. The Nutrition_Score class takes those nutrition estimates and gives a score that is related to gender, age, and activity level.

> Note: clean_foods.csv is not hosted on this GitHub page. We do not have permission to distribute this dataset, as it doesn't belong to us. Please contact a member of the BIG IDEAs Lab for permission to access this dataset.

### Palate.py

This file contains one class. The Palate class uses a dimensionality reduction technique we call "palate deconstruction". It reduces 300 dim embeddings to just 30 dim, based on the food's semantic relationship to different "flavors" defined in **flavors.pickle**.

### db_prep.py
This file contains one class, and depends on the Nutrition.py and Palate.py modules described above. It accepts one argument in the form of a csv file with columns defined below. It returns a sqlite3 database with additional columns for a nutrition score (provided by Nutrition.py) and an embedded representation of the food item (provided by Palate.py). Each row of the returned sqlite3 database contains the following information: 

1. food_item
2. food_description
3. restaurant_name
4. latitude
5. longitude
6. price
7. palate
8. nutrition

### Example
```
#Build a csv file with the above 8 headers and copy it into the nutrics folder.

#navigate to nutrics folder
>> cd nutrics

#run conversion pipeline code
>> python db_prep.py [CSVFILENAME].csv

#check directory, there should be a recently added 'nutrics.db'
```

> The API is dependent on nutrics.db. Ensure it is within the same directory for the Docker container to successfully initialize.

-------------

## Server API **Production:**

-------------

### app.py

This file contains a Flask application and RESTful API logic. Think of it as our central hub that reroutes users based on their chosen endpoint. The API constructs and manages a separate online database named "app.db". app.db is defined in models.py, and controlled by resources.py.

#### models.py
 This file defines our user model, preference model, and token model. Each model is a class with various convenience methods. This file forms the "Model" in the classic model-view-controller (MVC) design. Models include: 

1. UserModel
   
   UserModel coordinates with the 'users' table in our app.db. It handles user access data (registration / login / tokens / authorized roles).

2. PreferenceModel

    PreferenceModel coordinates with the 'user_preferences' table in our app.db. It handles user preference data (historical items the user has enjoyed).

3. RevokedTokenModel
   
   RevokedTokenModel coordinates with the 'revoked_tokens' table in our app.db. It allows us to blacklist tokens and adds another layer of security to our application.


#### resources.py
This file defines resources and aligns with the Flask endpoints identified in app.py. Think of it as the "C" or "Controller" in the MVC pattern. All endpoints are POST calls with parameters identified below. JWT stands for JSON web token, and more information can be found [here](https://jwt.io/introduction/). Our resources include:

| Resource | Authorization Header | Endpoint | Required Params | 
| ------------- |:-------------:| :-----:| :-----:|
| UserRegistration | Open | *~/registration* | username / password / role|
| UserLogin | JWT required | *~/login* | username / password |
| UserLogoutAccess | JWT required | *~/logout/access* | None |
| UserLogoutRefresh | JWT required |*~/logout/refresh* | None |
| TokenRefresh | JWT required | *~/token/refresh* | None |
| GetUserPreference | JWT required | *~/prefs* | None
| EditPreference | JWT required | *~/edit* | preference / preference_action
| Admin  | JWT w/Admin access required | *~/admin* | action


### nutrics_database_manager.py
This file acts as a database manager for the nutrics.db we defined in the "preperation" stage. It is wrapped in a [SQLAlchemy](https://www.sqlalchemy.org/) application that allows for ORM database references. It contains a single class that allows us to interface with models.py and resources.py. It was separated from app.db to allow for modularity and updatability, and to help isolate user information in their own protected database.

## Frontend (Mobile Application)

### Design Principles

Our frontend was maticulously and thoughtfully designed by @Ryan_Bolick, with guidance from behavioral psychologists at Duke University. We follow AI design guidelines that have been inspired by [Google](https://pair.withgoogle.com/).

You can find Ryan's most up to date work [here](https://gallery.io/projects/MCHbtQVoQ2HCZYjYt-pwv8Nr/files/MCHXG950YxofXVKr92LnNIc6) with his permission.

### Why do we plan to use Flutter?

We considered multiple platforms to build on, and tested iOS and React Native prototypes. We decided [Flutter](https://flutter.dev/) was the most appropriate platform to suit our needs. 

| Platform        | Pros           | Cons  |
| ------------- |:-------------:| :-----:|
| iOS (Swift)    | Fast, native | Single platform use |
| Android (Kotlin)      | Fast, native      |   Single platform use |
| React Native (Javascript) | Multiplatform design, easy to learn, supported by Facebook      | Compiles through javascript bridge (slow) |
| Flutter (Dart) | Multiplatform design, easy to learn, compiles to native code (fast), supported by Google | Still a developing language and online community. 

## Frontend (Search Engine)

### NLP Food Searching

With the powerful backend API we are building, we can interface with different frontend products. One example was created by [Aman Ibrahim](https://github.com/orgs/Big-Ideas-Lab/people/amanmibra) and can be found at this [repo](https://github.com/Big-Ideas-Lab/nutrics-search-webapp).


<!-- ------------

## MVP To Do (Backend): 
- [x] Connect GeoLocal Module to Nutritionix API
- [ ] Connect Recommender Module to Firestore through Firebase Functions
- [x] Update Recommender Module for single analysis
- [ ] Wrap in non-Flask Application for production server -->


<!-- ## Nice to have: 
- [ ] Enhance NLP model with food blogs -->

<!-- ## Future Projects

Phase 0a (What we already have):
- A limited food database
- A working recommendation model for nutritious food items
- A nutrition content estimator based on semantic relationships and deep learning
- Cloud architecture that responds to a mobile application
- Progressing user interface design created in collaboration with a UX designer and behavioral economist
 Phase 0b (What we are currently working on): 
- Building and scaling our database with an online server (Limiting factor: $$ for quality managed databases)
- Using deep and reinforcement learning to improve our recommendation model (Limiting factor: Time to develop)
- Submitting our nutrition estimator to MLHC for external validation (Limiting factor: Time to publish)
- Refining the cloud architecture (Limiting factor: Time to refine and $$ for managed services)
- Building the mobile application itself (Limiting factor: Time for quality and data security, $$ for development time and server costs)
- IRB Approval (Limiting factor: OIT and ISO approval)
 Phase 1 (Summer 2020):
A mobile application that tracks Duke employees at high risk for cardiometabolic disease and offers real-time suggestions for nutritious options on Duke's campus. 
 Phase 2 (Late Fall 2020):
Offer our application to members of the wider Durham community and offer real-time suggestions for nearby nutritious options in restaurants.
Phase 3 (Summer 2021):
Expand our application to grocery stores and at-home meals in Durham using the data we get from Phase 1 and 2 on eating habits. 
Phase 4 (By Spring 2022):
Expand our application nationally, and then globally with the help of DGHI expertise and local communities. Our database is designed to be scalable and extensible, and our recommendation model will be adaptable to preferences. We expect there to be many unforeseen challenges in a global rollout (connectivity, access to food data, and GPS capability of note), but through early and careful planning, we can start addressing these challenges early.  -->

