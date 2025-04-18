"""
Generates the wrapper classes and functions used to effectively
call the api module and connect with the PokeAPI endpoint.

By utilizing these wrapper functions, classes, and values,
use of the PokeAPI becomes abstracted away behind convenient,
user-friendly function calls instead.

Create a new Pokemon object with just the Pokemon name or ID:
>>> new_pokemon = Pokemon("gengar")
>>> print(new_pokemon)
'gengar'

Then access its data using dictionary keys from .content:
>>> poke.data["types"]
"types": [
    {
        "slot": 1,
        "type": {
            "name": "ghost",
            "url": "https://pokeapi.co/api/v2/type/8/"
        }
    },
    {
        "slot": 2,
        "type": {
            "name": "poison",
            "url": "https://pokeapi.co/api/v2/type/4/"
        }
    }
"""

from .api import ApiController


class Pokemon:
    """A Pokemon object that contains an APIController object
    with data returned from a call to the PokeAPI endpoint.
    """

    def __init__(self, name_or_id):
        """Instantiates a new Pokemon class containing an
        APIController container class with the information
        retrieved from the API or cache.
        """
        self._api_data = ApiController(
            resource="pokemon",
            name_or_id=name_or_id
        )

        self.id = self._api_data.id
        self.name = self._api_data.name
        self.url = self._api_data.url

        self.data = self._build_dict()

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<{self.name} #{self.id} at {self.url}>"

    def _build_dict(self):
        """Returns a dictionary object from further inside
        the nested dict structure returned from the API call.
        """
        # Specifically needs to be an indexable list (keys object is not)
        content_keys = [key for key in self._api_data.content_dict]

        uri_key = content_keys[0]
        api_content = {key: self._api_data.content_dict[uri_key][key]
                       for key in self._api_data.content_dict[uri_key].keys()}

        return api_content
