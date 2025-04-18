#!/usr/bin/env python

"""
pikawrap
A small Python wrapper for PokeAPI (https://pokeapi.co)

Usage:
>>> import pikawrap
>>> new_pokemon = pokewrap.ApiController("gengar")
>>> new_pokemon.name
'gengar'
"""

__author__ = "Arya Shah"
__email__ = "aryaforhire@gmail.com"
__version__ = "1.0.0"
__copyright__ = "Copyright Arya Shah 2025"
__license__ = "Apache-2.0"


from .api import API_URI_STUB, RESOURCE_ENDPOINTS, RESOURCE_TYPES
from .api import ApiController, ApiResourceList
from .wrappers import Pokemon
