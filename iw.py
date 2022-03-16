from onshape_to_robot.onshape_api.client import Client
from onshape_to_robot.config import parse_config

cf = parse_config("./sample_export/")
cc = Client(logging=False, creds="./sample_export/config.json")

did = cf['documentId']

doc = cc.get_document(did).json()

wid = doc['defaultWorkspace']['id']

els = cc.list_elements(did, wid, args={'elementType': 'ASSEMBLY'}).json()

aid = els[0]['id']

