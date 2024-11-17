import spacy
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from pymongo import MongoClient

class FuzzyEngine:

    def __init__(self, client):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['sports_analysis']
        self.collection = self.db['video_data']

        self.nlp = spacy.load('en_core_web_sm')

        # Fuzzy variable for speed
        self.speed = ctrl.Antecedent(np.arange(0, 101, 1), 'speed')
        self.speed['slow'] = fuzz.trimf(self.speed.universe, [0, 0, 50])
        self.speed['moderate'] = fuzz.trimf(self.speed.universe, [20, 50, 80])
        self.speed['fast'] = fuzz.trimf(self.speed.universe, [50, 100, 100])

        # Fuzzy variable for distance
        self.distance = ctrl.Antecedent(np.arange(0, 5000, 1), 'distance')
        self.distance['near'] = fuzz.trimf(self.distance.universe, [0, 0, 2000])
        self.distance['medium'] = fuzz.trimf(self.distance.universe, [1000, 2500, 4000])
        self.distance['large'] = fuzz.trimf(self.distance.universe, [3000, 5000, 5000])

    def parse_natural_language_query(self, query):
        doc = self.nlp(query)
        types = ["player","referee","goalkeeper","ball"]
        attibute = ["speed","distance"]

        query_attribute = [i for i in attibute if i in query][0]
        query_type = [i for i in types if i in query][0]
        subject, action, attribute, fuzzy_value = "", "", "", ""
        
        for token in doc:
            if token.dep_ == 'nsubj':
                subject = token.text
            elif token.dep_ == 'ROOT':
                action = token.text
            elif token.dep_ == 'attr':
                attribute = token.text
            elif token.pos_ == 'ADJ':
                fuzzy_value = token.text
        
        subject = query_type
        attribute = query_attribute
        return subject, action, attribute, fuzzy_value

    def map_fuzzy_value_to_set(self, attribute, fuzzy_value):
        if attribute == 'speed':
            if fuzzy_value == 'fast':
                return self.speed['fast']
            elif fuzzy_value == 'moderate':
                return self.speed['moderate']
            elif fuzzy_value == 'slow':
                return self.speed['slow']
        elif attribute == 'distance':
            if fuzzy_value == 'near':
                return self.distance['near']
            elif fuzzy_value == 'medium':
                return self.distance['medium']
            elif fuzzy_value == 'large':
                return self.distance['large']
        else:
            raise ValueError(f"Unknown attribute or fuzzy value: {attribute}, {fuzzy_value}")

    def generate_fuzzy_query(self, attribute, fuzzy_set):
        return f"SELECT object_id, {attribute} FROM player_data WHERE {attribute} IS ABOUT {fuzzy_set};"

    def execute_fuzzy_query(self, fuzzy_sets):
        # Query MongoDB for player data, including speed and distance
        player_data = self.collection.find({}, {"_id": 0, "entities": 1,"video_name":1})
        matching_results = []
        for data in player_data:
            for entity in data['entities']:
                if entity['type'] != fuzzy_sets['entity_type']:
                    continue
                speed_input = entity.get("speed", 0)
                distance_input = entity.get("distance", 0)
                
                qci_speed = fuzz.interp_membership(self.speed.universe, fuzzy_sets['speed'].mf, speed_input)
                qci_distance = fuzz.interp_membership(self.distance.universe, fuzzy_sets['distance'].mf, distance_input)
                
                # Combining QCI values for multi-attribute querying
                combined_qci = (qci_speed + qci_distance) / 2  # Average of the two attributes

                if combined_qci > 0:
                    matching_results.append({
                        "entity_id": entity["id"],
                        "type": entity["type"],
                        "video_name": data["video_name"],
                        "speed": speed_input,
                        "distance": distance_input,
                        "qci_speed": qci_speed,
                        "qci_distance": qci_distance,
                        "combined_qci": combined_qci
                    })
        
        return sorted(matching_results, key=lambda x: x["combined_qci"], reverse=True)

    def display_results(self, results):
        print("Ranked Query Results:")
        print(f"{'Video':>10} {'Entity ID':<10} {'type':<15} {'Speed':<10} {'Distance':<10} {'QCI Speed':<10} {'QCI Distance':<15} {'Combined QCI':<15}")
        print("-" * 70)
        
        for result in results[:10]:
            print(f"{result["video_name"]:<} {result['entity_id']:<10} {result['type']:<10} {result['speed']:<10} {result['distance']:<10} "
                  f"{result['qci_speed']:<10.2f} {result['qci_distance']:<15.2f} {result['combined_qci']:<15.2f}")

    def attach(self,fuzzy_sets,attribute,fuzzy_value):
        if attribute == 'speed':
            fuzzy_sets['speed'] = self.map_fuzzy_value_to_set('speed', fuzzy_value)
            fuzzy_sets['distance'] = self.map_fuzzy_value_to_set('distance', 'medium')
        elif attribute == 'distance':
            fuzzy_sets['distance'] = self.map_fuzzy_value_to_set('distance', fuzzy_value)
            fuzzy_sets['speed'] = self.map_fuzzy_value_to_set('speed', 'moderate')

        return fuzzy_sets

# # MongoDB connection
# client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string

# # Example usage
# engine = FuzzyEngine(client)
# query = "Find goalkeeper moving at fast speed"
# subject, action, attribute, fuzzy_value = engine.parse_natural_language_query(query)
# print(fuzzy_value,attribute)
# # Assume the query involves both speed and distance
# fuzzy_sets = {
#     'entity_type':subject
# }

# fuzzy_sets = engine.attach(fuzzy_sets,attribute,fuzzy_value)

# results = engine.execute_fuzzy_query(fuzzy_sets)
# engine.display_results(results)
