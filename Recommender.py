'''
This module is designed to be a simple implementation of our recommendation model, based on cosine distances.

Created by Joshua D'Arcy, Sabrina Qi, and Aman Ibrahim on 2/27/2020
'''

from Palate import Palate
pal = Palate()

#Creating 3 dummy data for userHx, you will probably need to create more
user_liked = ['cheeseburger', 'french fries', 'steak']
userHx = [pal.palette_constructor(liked) for liked in user_liked]

#Creating 3 dummy data for CandidateValues, you will probably need to create more
available_local = ['kale', 'cheeseburger', 'fruit smoothie']
candidates = [pal.palette_constructor(available) for available in available_local]


class Recommender(): 

'''
Inputs: 
    1. User History of Liked Palate Vectors - {UserHx}
  
    2. Candidate Table - {candidates}

Process: 

    1. Compare each value in {UserHx} to each value in {Candidates} using cosine distance
   
    2. Sort closest matches in area

Outputs: 
    1. Return Top 5 closest matches. JSON file should be structured as: 

    [{Recommendation_1:
        - Candidate food name
        - Candidate food vector 
        - UserHx food name
        - UserHx food vector
        - cosine distance between Candidate food vector and UserHx food vector},
    {...},
    {...},
    {...},
    {...}]
'''