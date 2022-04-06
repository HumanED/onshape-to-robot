'''
client
======

Convenience functions for working with the Onshape API
'''

from .onshape import Onshape

import mimetypes
import random
import string
import os
import json
import hashlib


def double_escape_slash(s):
    return s.replace('/', '%252f')


def escape_slash(s):
    return s.replace('/', '%2f')


class Client():
    '''
    Defines methods for testing the Onshape API. Comes with several methods:

    - Create a document
    - Delete a document
    - Get a list of documents

    Attributes:
        - stack (str, default='https://cad.onshape.com'): Base URL
        - logging (bool, default=True): Turn logging on or off
    '''

    def __init__(
            self,
            stack='https://cad.onshape.com',
            logging=True,
            creds='./config.json'):
        '''
        Instantiates a new Onshape client.

        Args:
            - stack (str, default='https://cad.onshape.com'): Base URL
            - logging (bool, default=True): Turn logging on or off
        '''

        self._metadata_cache = {}
        self._massproperties_cache = {}
        self._stack = stack
        self._api = Onshape(stack=stack, logging=logging, creds=creds)
        self.useCollisionsConfigurations = True

    def cache_get(self, method, key, callback, isString=False):
        if isinstance(key, tuple):
            key = '_'.join(list(key))
        fileName = method + '__' + key
        dirName = os.path.dirname(os.path.abspath(__file__)) + '/cache'
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        fileName = dirName + '/' + fileName
        if os.path.exists(fileName):
            f = open(fileName, 'rb')
            result = f.read()
            f.close()
        else:
            result = callback().content
            f = open(fileName, 'wb')
            f.write(result)
            f.close()
        if isString and isinstance(result, bytes):
            result = result.decode('utf-8')
        return result

#-------------------------------------------------------------------------------

    def list_documents(self):
        '''
        Get list of documents for current user.

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/documents')

    def get_document(self, did, args={}):
        '''
        Get details for a specified document.

        Args:
            - did (str): Document ID

        Returns:
            - requests.Response: Onshape response data
        '''
        return self._api.request('get', '/api/documents/' + did, query=args)

    def list_workspaces(self, did, args={}):
        '''
        Get list of workspaces of a given document.

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/documents/d/' + did + '/workspaces', query=args)

    def get_workspace(self, did, wid, args={}):
        '''
        Get details of a given workspace of a given document.

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/documents/d/' + did + '/workspaces/' + wid, query=args)

    def list_elements(self, did, wid, type='w', args={}):
        '''
        Get the list of elements in a given document
        '''

        return self._api.request(
            'get',
            '/api/documents/d/' +
            did +
            '/' +
            type +
            '/' +
            wid +
            '/elements', query=args)

    def get_assembly(self, did, wid, eid, type='w', configuration='default', args={}):
        return self._api.request(
            'get',
            '/api/assemblies/d/' +
            did +
            '/' +
            type +
            '/' +
            wid +
            '/e/' +
            eid,
            query={
                'includeMateFeatures': 'true',
                'includeMateConnectors': 'true',
                'includeNonSolids': 'true',
                'configuration': configuration} | args)

    def get_features(self, did, wid, eid, type='w', args={}):
        '''
        Gets the feature list for specified document / workspace / part studio.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request(
            'get',
            '/api/assemblies/d/' +
            did +
            '/' +
            type +
            '/' +
            wid +
            '/e/' +
            eid +
            '/features',
            query=args)

    def get_assembly_features(self, did, wid, eid, args={}):
        '''
        Gets the feature list for specified document / workspace / part studio.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request(
            'get',
            '/api/assemblies/d/' +
            did +
            '/w/' +
            wid +
            '/e/' +
            eid +
            '/features',
            query=args)

    def get_partstudio_tessellatededges(self, did, wid, eid, args={}):
        '''
        Gets the tessellation of the edges of all parts in a part studio.

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request(
            'get',
            '/api/partstudios/d/' +
            did +
            '/w/' +
            wid +
            '/e/' +
            eid +
            '/tessellatededges',
            query=args)

    def get_sketches(self, did, mid, eid, configuration='default', args={}):
        def invoke():
            return self._api.request(
                'get',
                '/api/partstudios/d/' +
                did +
                '/m/' +
                mid +
                '/e/' +
                eid +
                '/sketches',
                query={
                    'includeGeometry': 'true',
                    'configuration': configuration})

        return json.loads(
            self.cache_get(
                'sketches',
                (did,
                 mid,
                 eid,
                 configuration),
                invoke))

    def get_parts(self, did, mid, eid, configuration):
        def invoke():
            return self._api.request(
                'get',
                '/api/parts/d/' +
                did +
                '/m/' +
                mid +
                '/e/' +
                eid,
                query={
                    'configuration': configuration})

        return json.loads(
            self.cache_get(
                'parts_list',
                (did,
                 mid,
                 eid,
                 configuration),
                invoke))

#-------------------------------------------------------------------------------

    def find_new_partid(
            self,
            did,
            mid,
            eid,
            partid,
            configuration_before,
            configuration):
        before = self.get_parts(did, mid, eid, configuration_before)
        name = None
        for entry in before:
            if entry['partId'] == partid:
                name = entry['name']

        if name is not None:
            after = self.get_parts(did, mid, eid, configuration)
            for entry in after:
                if entry['name'] == name:
                    return entry['partId']
        else:
            print("OnShape ERROR: Can't find new partid for " + str(partid))

        return partid

    def hash_partid(self, data):
        m = hashlib.sha1()
        m.update(data.encode('utf-8'))
        return m.hexdigest()

    def part_studio_stl(self, did, wid, eid):
        '''
        Exports STL export from a part studio

        Args:
            - did (str): Document ID
            - wid (str): Workspace ID
            - eid (str): Element ID

        Returns:
            - requests.Response: Onshape response data
        '''

        req_headers = {
            'Accept': 'application/vnd.onshape.v1+octet-stream'
        }
        return self._api.request(
            'get',
            '/api/partstudios/d/' +
            did +
            '/w/' +
            wid +
            '/e/' +
            eid +
            '/stl',
            headers=req_headers)

    def part_studio_stl_m(
            self,
            did,
            mid,
            eid,
            partid,
            configuration='default'):
        if self.useCollisionsConfigurations:
            configuration_before = configuration
            parts = configuration.split(';')
            partIdChanged = False
            result = ''
            for k, part in enumerate(parts):
                kv = part.split('=')
                if len(kv) == 2:
                    if kv[0] == 'collisions':
                        kv[1] = 'true'
                        partIdChanged = True
                parts[k] = '='.join(kv)
            configuration = ';'.join(parts)

            if partIdChanged:
                partid = self.find_new_partid(
                    did, mid, eid, partid, configuration_before, configuration)

        def invoke():
            req_headers = {
                'Accept': 'application/vnd.onshape.v1+octet-stream'
            }
            return self._api.request(
                'get',
                '/api/parts/d/' +
                did +
                '/m/' +
                mid +
                '/e/' +
                eid +
                '/partid/' +
                escape_slash(partid) +
                '/stl',
                query={
                    'mode': 'binary',
                    'units': 'meter',
                    'configuration': configuration},
                headers=req_headers)

        return self.cache_get(
            'part_stl',
            (did,
             mid,
             eid,
             self.hash_partid(partid),
             configuration),
            invoke)

    def part_get_metadata(
            self,
            did,
            mid,
            eid,
            partid,
            configuration='default'):
        def invoke():
            return self._api.request(
                'get',
                '/api/parts/d/' +
                did +
                '/m/' +
                mid +
                '/e/' +
                eid +
                '/partid/' +
                double_escape_slash(partid) +
                '/metadata',
                query={
                    'configuration': configuration})

        return json.loads(
            self.cache_get(
                'metadata',
                (did,
                 mid,
                 eid,
                 self.hash_partid(partid),
                 configuration),
                invoke,
                True))

    def part_mass_properties(
            self,
            did,
            mid,
            eid,
            partid,
            configuration='default'):
        def invoke():
            return self._api.request(
                'get',
                '/api/parts/d/' +
                did +
                '/m/' +
                mid +
                '/e/' +
                eid +
                '/partid/' +
                escape_slash(partid) +
                '/massproperties',
                query={
                    'configuration': configuration})

        return json.loads(
            self.cache_get(
                'massproperties',
                (did,
                 mid,
                 eid,
                 self.hash_partid(partid),
                 configuration),
                invoke,
                True))
