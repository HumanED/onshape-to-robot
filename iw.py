from onshape_to_robot.onshape_api.client import Client
from onshape_to_robot.config import parse_config

cf = parse_config("./sample_export/")
cc = Client(logging=False, creds="./sample_export/config.json")

did = cf['documentId']

doc = cc.get_document(did).json()

wid = doc['defaultWorkspace']['id']

asses = cc.list_elements(did, wid, args={'elementType': 'ASSEMBLY'}).json()

aid = '617633ce069df90a46077e98'

ass = cc.get_assembly(did, wid, aid).json()

fes = cc.get_features(did, wid, aid).json()

fs = fes['features']
fss = fes['featureStates']

mc_is = []
m_is = []
for feature_i, feature in enumerate(fs):
    if feature['typeName'] == 'BTMMateConnector':
        mc_is.append(feature_i)
    elif feature['typeName'] == 'BTMMate':
        m_is.append(feature_i)

joints = []
