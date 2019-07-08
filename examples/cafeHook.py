"""
Example for a Hook that responds with a cafe for a city
"""
# System imports

# 3rd party imports
from btHook import Hook
import requests
import random
from geotext import GeoText # only works with the english names of the cities



# local imports

class CafeHook(Hook):
    """
    Example for a Hook that responds with a cafe for a city
    """

    def onMessage(self, originalTxt, intent, language, entities, slots, branchName, peer):
        """
        respond with a cafe name for a city
        """
        cities = []
        text = ""
        for word in originalTxt.split():    # make all word with a captial first letter
            text += word[0].upper() + word[1:] + " "


        for i in range(len(text.split())):
            chunk = " ".join(text.split()[i:i + 5]) # assuming no cities with more than 5 words
            chunkCities = GeoText(chunk).cities
            cities.extend(chunkCities)
        cities = list(set(cities))#remove dublicates

        cities.sort(key=len, reverse=True)

        print (cities)
            
        message = "Ich kann leider nichts passendes finden :/"


        try:
            for i, city in enumerate(cities):
                if city in text:                #filter cities with names of more than one word that overlap with other cities like york and new york
                    text = text.replace(city, "")
                else:
                    continue
                print(city)
                r = requests.get('https://nominatim.openstreetmap.org/search?format=json&city={}&amenity=cafe&addressdetails=1&limit=100'.format(city))
                resp = r.json()
                cafes = []
                for cafe in resp:
                    if 'cafe' in cafe['address']:
                        cafes.append(cafe)
                cafe = random.choice(cafes)
                name = cafe['address']['cafe']
                suburb = ""
                if 'suburb' in cafe['address']:
                    suburb = cafe['address']['suburb']
                if not i:
                    message = "Probier doch mal {} in {} {}. ".format(name, city, suburb)
                else:
                    message += "Oder {} in {} {}. ".format(name, city, suburb)
        except Exception:
            message = "Ich kann leider nichts passendes finden :/"
        
        self.say(peer, {'answer':message})

if __name__ == "__main__":
    h = CafeHook()  # setup the .btnexusrc in your project

