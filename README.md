![alt text](Logo.png "Title")

Welcome to the Nutrics project. We think that choosing nutritious, local food should be easy, and we're building an application that does it for you.

## Local API Runtime Instructions:


```
git clone 'https://github.com/Big-Ideas-Lab/nutrics.git'
cd nutrics
pip install -r requirements.txt
FLASK_APP=run.py FLASK_DEBUG=1 flask run
```

Note: nutrics.db and clean_foods.csv are not hosted on this GitHub page. We do not have permission to distribute these datasets, as they don't belong to us. Please contact a member of the BIG IDEAs Lab for permissions. 

```
Update 4.15.2020: We restructured the backend and the previous endpoints no longer exist. Please check back in in the next few days when this README is updated. 
```

-------------

- [ ] README needs updating.

## **Backend API:**

### app.py

This file contains a Flask application. Think of it as our central hub that reroutes users based on their endpoint. 

### models.py
This file defines 

### Nutrition.py

This file contains two classes. The Nutrients class uses natural language processing to estimate the nutritional value of food, and uses **clean_foods.csv**, which we were lended by Duke Nutrition. The Nutrition_Score class takes those nutrition estimates and gives a score that is related to gender, age, and activity level.

> Note: clean_foods.csv is not hosted on this GitHub page. We do not have permission to distribute this dataset, as it doesn't belong to us. Please contact a member of the BIG IDEAs Lab for permission to access this dataset.

### Palate.py

This file contains one class. The Palate class uses a dimensionality reduction technique we call "palate deconstruction". It reduces 300 dim embeddings to just 30 dim, based on the food's semantic relationship to different "flavors" defined in **flavors.pickle**. 300 dim embeddings for a large corpus are stored in **unique_foods.pickle** and are in {string:embedding} format.

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

------------

## MVP To Do (Backend): 
- [x] Connect GeoLocal Module to Nutritionix API
- [ ] Connect Recommender Module to Firestore through Firebase Functions
- [x] Update Recommender Module for single analysis
- [ ] Wrap in non-Flask Application for production server


## MVP To Do (Frontend): 
- [ ] Develop non-connected widgets to specification designed [here.](https://gallery.io/projects/MCHbtQVoQ2HCZYjYt-pwv8Nr/files/MCHXG950YxofXVKr92LnNIc6)
- [ ] Connect frontend application to Firestore
- [ ] Establish secure login methods 

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

