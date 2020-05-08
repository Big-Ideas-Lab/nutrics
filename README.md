# Nutrics

Welcome to the Nutrics project. We think that choosing nutritious, local food should be easy, and we're building an application that does it for you.


## Local API Runtime Instructions:

```
git clone 'https://github.com/Big-Ideas-Lab/nutrics.git'
cd nutrics
pip install -r requirements.txt
FLASK_APP=run.py FLASK_DEBUG=1 flask run
```
> Updated by Joshua D'Arcy on 5.8.2020

-------------

## Backend (API)

-------------

#### run.py

This file contains a Flask application and RESTful API logic. Think of it as our central hub that reroutes users to their chosen endpoints. The API constructs and manages a database named "app.db". app.db is defined in **models**, controlled by **resources**, and connected by **endpoints** in run.py.

### Models

1. UserModel.py
   
   UserModel coordinates with the 'users' table in our app.db. It handles user access data and login / registration / session management / tokens.

2. PreferenceModel.py

   PreferenceModel coordinates with the 'user_preferences' table in our app.db. It handles user preference data (historical items the user has enjoyed).

3. FoodModel.py

   FoodModel coordinates with the 'food' table in our app.db. FoodModel builds and adds convenience functions to edit our database of local items to offer.

4. RevokedTokenModel.py
   
   RevokedTokenModel coordinates with the 'revoked_tokens' table in our app.db. It allows us to blacklist tokens and adds another layer of security to our application.

### Resources

1. UserResources.py
   
   UserResources defines resources accessible by any user (including admins). Classes (tied to **endpoints** in run.py) are defined in this table:

| Class | Authorization Header | Endpoint | Required Params | 
| ------------- |:-------------:| :-----:| :-----:|
| UserRegistration | Open | *~/registration* | username (string), password (string), email (string), age (int), gender_identity (int), activity_level (int) |
| UserLogin | JWT required | *~/login* | username (string), password (string) |
| UserLogoutAccess | JWT required | *~/logout/access* | None |
| UserLogoutRefresh | JWT required |*~/logout/refresh* | None |
| TokenRefresh | JWT required | *~/token/refresh* | None |
| GetUserPreference | JWT required | *~/prefs* | None
| EditPreference | JWT required | *~/edit* | preference (string), preference_action ('add' or 'remove') |
| EmailVerification | JWT required | *~/verification* | clickable URL |
| Recommender | JWT required | *~/recommendation* | latitude (float), longitude (float), distance (m) (float) |

2. AdminResources.py
   
   AdminResources defines resources accessible by only those with **admin privelages**. Classes (tied to **endpoints** in run.py) are defined in this table:

| Class | Authorization Header | Endpoint | Required Params | 
| ------------- |:-------------:| :-----:| :-----:|
| AdminUserInfo | JWT required | *~/admin/user/info* | None |
| AdminUserPreferences | JWT required | *~/admin/user/preferences* | None |
| AdminAccess | JWT required | *~/admin/access* | new_admin (string) |
| AdminFoodDump | JWT required | *~/admin/food/dump* | None |
| AdminFoodAdd | JWT required | *~/admin/food/add* | item_name (string), latitude (float), longitude (float), restaurant_name (string), item_description (string), price (float), nutrition (JSON string) |
| AdminFoodEdit | JWT required | *~/admin/food/edit* | item_name (string), latitude (float), longitude (float), restaurant_name (string), item_description (string), price (float), nutrition (JSON string) | 
| AdminFoodRemove | JWT required | *~/admin/food/remove* | item_name (string), latitude (float), longitude (float) |


### Utilities

1. natural_language.py

   natural_language contains two classes to assist with our natural language processing -- Distance and Embed. Distance is a simple numpy implementation for cosine similarity (or difference if you choose) between two vectors. Embed is an implementation of our palate reduction technique, which is a dimensionality reduction method we developed to compress 300 dim food representations to just 30 dim vectors. The smaller vector size allows for non-abritrary optimizations in our recommendation model.

2. nutrition_scoring.py

   nutrition_scoring contains one class (Nutrition_Score) that scores a food item's nutritional value (from FoodModel) based on age, gender identity, and activity level. The model was developed by Sabrina Qi with guidance from Duke Nutrition. The more positive (less negative) a score is, the more nutritional value the food has for you. 

3. request_parsers.py

   request_parsers were abstracted out from our resources file for readability.

4. flavors.pickle

   flavors.pickle is a Python list of ~30 palate features (umami, sweet, salty, etc) that we use for our dimensionality reduction technique.

5. unique_foods.pickle

   unique_foods is a Python dictionary of several thousand food items with a 300 dim vector representation from the Google News Corpus. They are organized as key:value pairs (food:vector). They were put in a python dictionary to limit the number of vectors from the Google News Corpus, and thus can load much more quickly (file size 1.5GB to 3.5 MB)

### Demo.ipynb

This is a jupyter notebook that uses each of the above described modules and endpoints for demonstration purposes. **NOTE**: Change the administrator password prior to production, since it is included in this demo.

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

