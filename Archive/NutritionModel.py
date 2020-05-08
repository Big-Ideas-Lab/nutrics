from run import db
from utilities.nlp import Embed #Embed class palatizes items to give them a 30 dim representation
import csv
import json

class NutritionModel(db.model):
    __tablename__ = 'nutrition_table'
    id = db.Column(db.Integer, primary_key = True)
 
    item_name = db.Column(db.String(120), unique = False, nullable = False)
    carbohydrates = db.Column(db.Float, unique = False, nullable = False)
    sugar = db.Column(db.Float, unique = False, nullable = False)
    total_fats = db.Column(db.Float, unique = False, nullable = False)
    sat_fats = db.Column(db.Float, unique = False, nullable = False)
    protein = db.Column(db.Float, unique = False, nullable = False)
    fiber = db.Column(db.Float, unique = False, nullable = False)
    calories = db.Column(db.Float, unique = False, nullable = False)
    cholesterol = db.Column(db.Float, unique = False, nullable = False)
    potassium = db.Column(db.Float, unique = False, nullable = False)
    sodium = db.Column(db.Float, unique = False, nullable = False)
    calcium = db.Column(db.Float, unique = False, nullable = False)
    magnesium = db.Column(db.Float, unique = False, nullable = False)

    embedding = db.Column(db.String(120), unique = False, nullable = False)

    @classmethod
    def create_nutrition_table(cls, csv_path):
    
        with open('utilities/clean_foods.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    nutrient_item = NutritionModel(
                        item_name = row[1]
                        carbohydrates = row[2]
                        sugar = row[3]
                        total_fats = row[4]
                        sat_fats = row[5]
                        protein = row[6]
                        fiber = row[7]
                        calories = row[8]
                        cholesterol = row[9]
                        potassium = row[10]
                        sodium = row[11]
                        calcium = row[12]
                        magnesium = row[13]
                        embedding = json.dumps(list(Embed.palate(row[1])))
                )

                nutrient.save_to_db()
                except:
                    continue
        #save user to database
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()