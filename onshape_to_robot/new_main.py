import os

from colorama import Fore, Back, Style

from .onshape_api.client import Client
from .config import parse_config

config = parse_config('sample_export/')

client = Client(logging=False, creds=config['configPath'])
client.useCollisionsConfigurations = config['useCollisionsConfigurations']

document_id = config['documentId']
document = client.get_document(document_id).json()

# TODO: for now just use the default workspace, more functionality can be added later
workspace_id = document['defaultWorkspace']['id']

# TODO: add options for specifying a version (as was removed and it used to be commented above (enjoy lol :D), but the client function was changed)
assemblies = client.list_elements(document_id, workspace_id, args={'elementType': 'ASSEMBLY'}).json()

# TODO: add other options for specifying the assembly aside from the name
assembly_id = None
assembly_name = None
for assembly in assemblies:
    if assembly['name'] == config['assemblyName']:
        assembly_id = assembly['id']
        assembly_name = assembly['name']
        break
if not assembly_id:
    raise Exception("ERROR: Unable to find assembly of the given name in this document (this is currently the only way to specify the assembly).")

# Retrieving the assembly
# print("\n" + Style.BRIGHT + '* Retrieving assembly "' + assembly_name + '" with id ' + assembly_id + Style.RESET_ALL)
assembly = client.get_assembly(document_id, workspace_id, assembly_id).json()
root_ass = assembly['rootAssembly']

# REVISE: I think we can pretty much say all occurences become links
occurrences = root_ass['occurrences']

# TODO: could probably be improved as for some stupid reason the onshape ids themselves may contain slashes...
for occ in occurrences:
    occ['joinedPath'] = os.path.join(*occ['path'])

root_occ_i = None
for occ_i, occ in enumerate(occurrences):
    if occ['fixed']:
        if root_occ_i is None:
            root_occ_i = occ_i
        else:
            raise Exception('There should be exactly 1 fixed occurrence, found multiple.')

feature_data = client.get_features(document_id, workspace_id, assembly_id).json()
features = feature_data['features']
feature_states = feature_data['featureStates']

mate_connector_is = []
mate_is = []
for feature_i, feature in enumerate(features):
    if feature['typeName'] == 'BTMMateConnector':
        mate_connector_is.append(feature_i)
    elif feature['typeName'] == 'BTMMate':
        mate_is.append(feature_i)


