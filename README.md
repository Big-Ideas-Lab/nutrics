![alt text](Logo.png "Title")

Welcome to the Nutrics project. We think that choosing nutritious, local food should be easy, and we're building an application that does it for you.

[Headers](#headers)

## Local API Runtime Instructions:


```

git clone 'https://github.com/Big-Ideas-Lab/nutrics.git'
cd nutrics
pip3 install -r requirements.txt
python3 main.py
```

Note: clean_foods.csv is not hosted on this GitHub page. We do not have permission to distribute this dataset, as it doesn't belong to us. Please contact a member of the BIG IDEAs Lab for permission to access this dataset.

```

Update 2.27.2020: Try these endpoints once you have flask running on a local server:

{localhost}/get_nutrients/<string>
{localhost}/get_palate/<string>
```

-------------

## **Backend API:**

### main.py

This file contains a Flask application. Think of it as the "hub" by which the other modules (Nutrition, Palate, Recommender, GeoLocal) connect and interact. main.py also interfaces with our Google Firestore, but more on that later.


### Nutrition.py

This file contains two classes. The Nutrients class uses natural language processing to estimate the nutritional value of food, and uses **clean_foods.csv**, which we were lended by Duke Nutrition. The Nutrition_Score class takes those nutrition estimates and gives a score that is related to gender, age, and activity level.

> Note: clean_foods.csv is not hosted on this GitHub page. We do not have permission to distribute this dataset, as it doesn't belong to us. Please ask jsd42@duke.edu for permission to access this dataset.

### Palate.py

This file contains one class. The Palate class uses a dimensionality reduction technique we call "palate deconstruction". It reduces 300 dim embeddings to just 30 dim, based on the food's semantic relationship to different "flavors" defined in **flavors.pickle**. 300 dim embeddings for a large corpus are stored in **unique_foods.pickle** and are in {string:embedding} format.

### GeoLocal.py

This file contains a dummy class for now. Given a latitude, longitude, and radius, the GeoLocal class will find nearby candidate options for menu items within walkable distance.

### Recommender.py

This file contains our recommendation model. It contains a "Recommender" class that accepts a two datasets as inputs -- one representing a user's positive history, and one containing candidate values from GeoLocal.py. Recommender compares these two datasets and makes ranked recommendations based on cosine distance.

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

With the powerful backend API we are building, we can interface with different frontend products. One example was created by [Aman Ibrahim](https://github.com/orgs/Big-Ideas-Lab/people/amanmibra).
