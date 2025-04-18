#!/usr/bin/env python
"""
A small and light module designed to wrap the PokeAPI API
and make working with its endpoints easier and more intuitive.

This module gets imported into the __init__.py file in this
directory to ease the importing process when working in adjacent
directories and for clean importing into the test suite.

For more information on this module and how it works,
please check out the __init__.py file or read the README in
the outer directory.
"""

# TODO add custom limit, offset fields to API queries

import json
import os
import requests


API_URI_STUB = "https://pokeapi.co/api/v2"

# Sets a default resource list in case the resource lookup fails
RESOURCE_TYPES = (
    "ability",
    "berry",
    "berry-firmness",
    "berry-flavor",
    "characteristic",
    "contest-effect",
    "contest-type",
    "egg-group",
    "encounter-condition",
    "encounter-condition-value",
    "encounter-method",
    "evolution-chain",
    "evolution-trigger",
    "gender",
    "generation",
    "growth-rate",
    "item",
    "item-attribute",
    "item-category",
    "item-fling-effect",
    "item-pocket",
    "language",
    "location",
    "location-area",
    "machine",
    "move",
    "move-ailment",
    "move-battle-style",
    "move-category",
    "move-damage-class",
    "move-learn-method",
    "move-target",
    "nature",
    "pal-park-area",
    "pokeathlon-stat",
    "pokedex",
    "pokemon",
    "pokemon-color",
    "pokemon-form",
    "pokemon-habitat",
    "pokemon-shape",
    "pokemon-species",
    "region",
    "stat",
    "super-contest-effect",
    "type",
    "version",
    "version-group",
)

# Set the RESOURCE_TYPES dictionary to be accurate from PokeAPI's categories
RESOURCE_ENDPOINTS = {}
try:
    response = requests.get((API_URI_STUB + "/"), timeout=10)
    response.raise_for_status()

    RESOURCE_ENDPOINTS = {API_URI_STUB: response.json()}
except requests.exceptions.HTTPError as errh:
    print(errh)
except requests.exceptions.ConnectionError as errc:
    print(errc)
except requests.exceptions.Timeout as errt:
    print(errt)
except requests.exceptions.RequestException as err:
    print(err)
finally:
    if len(RESOURCE_ENDPOINTS) == 0:
        RESOURCE_ENDPOINTS = RESOURCE_TYPES


class ApiController:
    """An object that manages the connection between PokeAPI
    (https://pokeapi.co/) and the running application.
    """
    def __init__(self, resource, name_or_id):
        """Initializes the ApiController with default uri
        to enable HTTP requests to the API source.

        Takes a resource (the values contained in RESOURCE_TYPES),
        for example 'pokemon' and the name or id of the desired item.

        To retrieve content on a specific pokemon, for instance,
        use resource='pokemon' and name_or_id='gengar' for name,
        or name_or_id=94 for pokemon ID number.
        """
        self.content_dict = {}
        self.cache_path = self._build_cache_path()

        self.endpoint = API_URI_STUB

        self.resource = self._validate_resource(resource)

        self.name, self.id = self.convert_name_or_id(self.endpoint,
                                                     self.resource,
                                                     name_or_id)

        self.url = self._build_api_url(self.endpoint,
                                       self.resource,
                                       self.name)

    def __repr__(self):
        return f"<{self.url} - {self.name}>"

    def __str__(self):
        return f"{self.name}"

    def _build_api_url(self, endpoint, resource, name_or_id):
        """Defines the full URL for the HTTP request."""
        return "/".join((endpoint, resource, name_or_id))

    def _build_cache_path(self):
        """Finds the cwd, then builds the desired path to where
        all cached resources should be saved.
        """
        return os.path.join(os.getcwd(), "cache.json")

    def _convert_id_to_name(self, endpoint, resource, id_):
        """Takes the endpoint and the resource id, then
        returns the resource name as a str.
        """
        url = self._build_api_url(endpoint, resource, str(id_))
        resource_data = self.get_data(url)

        return resource_data[url].get("name", str(id_))

    def _convert_name_to_id(self, endpoint, resource, name):
        """Takes the endpoint and the resource name, then
        returns the resource id as an int.
        """
        url = self._build_api_url(endpoint, resource, name)
        resource_data = self.get_data(url)

        return resource_data[url].get("id")

    def _get_resource(self, url=None, timeout=10):
        """Sends a GET request to the API to receive the needed
        resource and saves it as a dict object before returning it.

        Retrieved data gets saved to self.content_dict with url as key.
        """
        if url is None:
            url = self.url
        try:
            api_response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            self.content_dict[url] = api_response.json()
            return {url: api_response.json()}
        except requests.exceptions.HTTPError as error_h:
            print(error_h)
        except requests.exceptions.ConnectionError as error_c:
            print(error_c)
        except requests.exceptions.Timeout as error_t:
            print(error_t)
        except requests.exceptions.RequestException as error:
            print(error)

        return {url: None}

    def _validate_resource(self, resource):
        """Checks if the endpoint is a valid API endpoint within PokeAPI.
        Raises error if endpoint not in the list of valid resource types.
        """
        if RESOURCE_ENDPOINTS[API_URI_STUB].get(resource) is None:
            raise ValueError(f"Unknown API endpoint '{resource}'")

        return resource

    def cache_load(self):
        """Loads the given data from the cache, if applicable.
        Handles errors that could be thrown based on the possible
        states the cache can exist in (doesn't exist, open, etc.).
        """
        file_data = {}

        try:
            with open(self.cache_path, "r", encoding="utf-8") as file:
                file_data = json.load(file)
        except FileNotFoundError:
            pass
        except OSError as error:
            # Check if cache file is already open
            if error.errno == 11:
                pass
            else:
                raise error

        return file_data

    def cache_save(self):
        """Saves all held information into the cache if an identical
        cache entry doesn't already exist.
        """
        file_data = self.cache_load()

        try:
            for (key, value) in self.content_dict.items():
                if value is not None and key not in file_data.keys():
                    file_data[key] = value

            with open(self.cache_path, "w", encoding="utf-8") as file:
                file.seek(0)
                json.dump(file_data, file)
        except OSError as error:
            # Cache already open
            if error.errno == 11:
                raise KeyError("Cache could not be opened.") from error
            else:
                raise

    def convert_name_or_id(self, endpoint, resource, name_or_id):
        """Converts a name to an ID or an ID to a name,
        depending on type.

        Assumes ID is int and name is str, but if an int
        is passed as a str it will try to convert to int
        before proceeding
        """
        try:
            name_or_id = int(name_or_id)
        except ValueError:
            pass

        if isinstance(name_or_id, str):
            name = name_or_id.lower()
            id_ = self._convert_name_to_id(endpoint, resource, name)
        elif isinstance(name_or_id, int):
            id_ = name_or_id
            name = self._convert_id_to_name(endpoint, resource, id_)
        else:
            raise ValueError(f"'{name_or_id}' could not be converted")

        return name, id_

    def get_data(self, url=None):
        """Tries to retrieve data from the cache in case it already exists.
        Then calls _get_resource() to send GET request to API otherwise.

        Retrieved data gets saved to self.content_dict with url as key.
        """
        if url is None:
            url = self.url

        data = self.cache_load()

        if url in data.keys():
            self.content_dict[url] = data[url]
            return {url: data[url]}

        data = self._get_resource(url)
        self.cache_save()

        return data

    def set_cache(self, new_cache_path=None):
        """Change the cache path to new_cache_path, which can be either
        an absolute or relative path.

        If the directory does not exist, it will be created. If None is passed
        the cache will default to the cwd.

        Ensure the cache is changed BEFORE any work is done using the library,
        if at all. Otherwise errors will arise in discovering the
        cache directory during runtime.
        """
        if new_cache_path is None:
            new_cache_path = self._build_cache_path()

        safe_cache_dir = self.safe_make_dirs(os.path.abspath(new_cache_path))
        safe_api_cache = os.path.join(safe_cache_dir, "cache,json")

        return safe_cache_dir, safe_api_cache

    @staticmethod
    def safe_make_dirs(path):
        """Create a leaf directory and all intermediate directories safely.
        Takes a path as either a relative or absolute directory tree
        to create new directories. Mode sets the directory permissions
        in octal.
        """
        try:
            os.makedirs(path)
        except OSError as error:
            if error.errno != 17:
                # File exists
                raise

        return path


class ApiResourceList():
    """An object that connects to pokeapi (https://pokeapi.co/)
    in order to catalog resources available to the user.
    """
    def __init__(self, resource, limit=None, offset=None):
        """Instantiates an ApiResourceList object containing
        a list of possible resources at the given resource endpoint.

        Optionally allows for specification of a [limit] and [offset],
        where limit sets the max number of items returned per page,
        and offset sets the max number of pages queried
        """
        self.endpoint = "/".join((API_URI_STUB, resource))
        self.cache_path = self._build_cache_path()

        # Dictionary version of results for caching
        self.response = self.get_data(limit, offset)
        self.cache_save()

        self._results = [i for i in self.response["results"]]
        self.count = self.response["count"]

    def __iter__(self):
        return iter(self._results)

    def __len__(self):
        return self.count

    def __str__(self):
        return f"{self._results}"

    def _build_cache_path(self):
        """Finds the cwd, then builds the desired path to where
        all cached resources should be saved.
        """
        return os.path.join(os.getcwd(), "cache.json")

    def _build_query_uri(self, limit=None, offset=None):
        """In the case a get request includes a custom limit and/or offset,
        a new URI gets built adding the query parameters to ensure
        PokeAPI knows to return the correct amount of data

        [limit] is an int representing the number of items you want to see
        from a given page,
        [offset] is an int representing the number of pages you'd like to
        pull results from in the event they span past a single page
        """
        query_url = self.endpoint

        if limit is not None:
            query_url += f"/?limit={limit}"
            if offset is not None:
                query_url += f"&offset={offset}"
        elif offset is not None:
            query_url += f"/?offset={offset}"

        return query_url

    def _get_resource(self, limit, offset, timeout=10):
        """Sends a GET request to the API to receive the needed
        resource and saves it as a dict object before returning it.

        Retrieved data gets saved to self.content_dict as dict with url as key.
        """
        query_url = self._build_query_uri(limit, offset)

        try:
            api_response = requests.get(query_url, timeout=timeout)
            response.raise_for_status()

            return api_response.json()
        except requests.exceptions.HTTPError as error_h:
            print(error_h)
        except requests.exceptions.ConnectionError as error_c:
            print(error_c)
        except requests.exceptions.Timeout as error_t:
            print(error_t)
        except requests.exceptions.RequestException as error:
            print(error)

        return {}

    def cache_load(self):
        """Loads the given data from the cache, if applicable.
        Handles errors that could be thrown based on the possible
        states the cache can exist in (doesn't exist, open, etc.).
        """
        file_data = {}

        try:
            with open(self.cache_path, "r", encoding="utf-8") as file:
                file_data = json.load(file)
        except FileNotFoundError:
            pass
        except OSError as error:
            # Cache already open
            if error.errno == 11:
                pass
            else:
                raise error

        return file_data

    def cache_save(self):
        """Saves all held information into the cache if an identical
        cache entry doesn't already exist.
        """
        if self.response is None or self.endpoint is None:
            return

        file_data = self.cache_load()

        try:
            file_data[self.endpoint] = self.response

            with open(self.cache_path, "w", encoding="utf-8") as file:
                file.seek(0)
                json.dump(file_data, file)
        except OSError as error:
            # Cache already open
            if error.errno == 11:
                raise KeyError("Cache could not be opened.") from error
            else:
                raise

    def get_data(self, limit, offset, timeout=10):
        """Tries to retrieve data from the cache in case it already exists.
        Then calls _get_resource() to send GET request to API otherwise.

        Retrieved data gets saved to self.content_dict as dict with url as key.
        """
        data = self.cache_load()

        if self.endpoint in data.keys():
            contents = data[self.endpoint]
        else:
            contents = self._get_resource(limit, offset, timeout)

        return contents


if __name__ == "__main__":
    # Quick demos if run as script instead of imported as module
    tmp = ApiController("pokemon", "gengar")
    print(repr(tmp))

    print(f"id: {tmp.id}, name: {tmp.name}")

    tmp.get_data()
    print(repr(tmp))

    new_tmp = ApiResourceList("pokemon", limit=100)
    print(new_tmp)
