from scipy.spatial.distance import cosine
from Palate import Palate

'''
This module is designed to be a simple implementation of our recommendation model, based on cosine distances.

Created by Joshua D'Arcy, Sabrina Qi, and Aman Ibrahim on 2/27/2020
'''


class Recommend:
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

    def __init__(self, user_Hx_arg, candidates_arg):
        self.userHx = user_Hx_arg
        self.candidates = candidates_arg

    def calculate_cosine_distance(self):
        all_dist = {}
        for candidate in self.candidates:
            cand_dist = [cosine(hist, candidate) for hist in self.userHx]
            all_dist[candidate] = cand_dist
        return all_dist  # this is a dictionary of lists

    def avg_distance(self):
        all_dist = self.calculate_cosine_distance()
        avg_dist_all_cand = {}
        for candidate, cand_dist in all_dist.items():
            avg_dist = mean(cand_dist)
            avg_dist_all_cand[candidate] = avg_dist
        return avg_dist_all_cand  # this is a dictionary of average distances

    def ranking(self):
        avg_dist_all_cand = self.avg_distance()
        sorted_candidates = sorted(avg_dist_all_cand,
                                   key=avg_dist_all_cand.__getitem__)
        top_five = sorted_candidates[0:4]
        return top_five


def main(candidates, userHx):
    recommender = Recommend(user_Hx_arg=userHx, candidates_arg=candidates)
    recommendations = recommender.ranking()
    avg_dist_all_cand = recommender.avg_distance()
    i = 0
    recommendation_list = []
    for rec in recommendations:
        ind = available_local.index[rec]
        vector = candidates[ind]
        avg_dist = avg_dist_all_cand[vector]
        rec_dict = {"Recommendation_{}".format(i): {"Food Name": rec,
                                                    "Food Vector":
                                                        vector,
                                                    "Avg Cosine "
                                                    "Distance": avg_dist}}
        recommendation_list.append(rec_dict)
        i += 1
    out_file = open("recommendations.json", "w")
    json.dump(recommendation_list, out_file)
    out_file.close()
    return


if __name__ == "__main__":
    pal = Palate()
    # Creating 3 dummy data for userHx, you will probably need to create more
    user_liked = ['cheeseburger', 'french fries', 'steak']
    userHx = [pal.palette_constructor(liked) for liked in user_liked]
    # Creating 3 dummy data for CandidateValues, you will probably need to
    # create more
    available_local = ['kale', 'cheeseburger', 'fruit smoothie']
    candidates = [pal.palette_constructor(available) for available in
                  available_local]
    main(candidates, userHx)
