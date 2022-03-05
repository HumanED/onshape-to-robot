import json
import os
import sys

from colorama import Fore, Back, Style


class ConfigFieldMissing(Exception):
    pass


class Config(dict):
    def checkField( self, name, default=None, hasDefault=False, valuesList=None):
        if default is not None:
            hasDefault = True

        if name in self:
            if (valuesList is not None) and (self[name] not in valuesList):
                raise ConfigFieldMissing(Fore.RED + f'ERROR: Value for "{name}" should be one of: ' + (','.join(valuesList)) + Style.RESET_ALL)
        else:
            if hasDefault:
                self[name] = default
            else:
                raise ConfigFieldMissing(
                    Fore.RED +
                    f'ERROR: missing key "{name}" in config' +
                    Style.RESET_ALL)


def parse_config(robot_folder_path):
    config_path = robot_folder_path + '/config.json'
    if not os.path.exists(config_path):
        raise Exception( Fore.RED + "ERROR: The file " + config_path + " can't be found" + Style.RESET_ALL)
    config = Config(json.load(open(config_path)))
    config['configPath'] = config_path

    config.checkField('documentId')
    config.checkField('versionId', '')
    config.checkField('workspaceId', '')
    config.checkField('drawFrames', False)
    config.checkField('drawCollisions', False)
    config.checkField('assemblyName', False)
    config.checkField('outputFormat', 'urdf', valuesList=['urdf', 'sdf'])
    config.checkField('useFixedLinks', False)
    config.checkField('configuration', 'default')
    config.checkField('ignoreLimits', False)

    # Using OpenSCAD for simplified geometry
    config.checkField('useScads', True)
    config.checkField('pureShapeDilatation', 0.0)

    # Dynamics
    config.checkField('jointMaxEffort', 1)
    config.checkField('jointMaxVelocity', 20)
    config.checkField('noDynamics', False)

    # Ignore list
    config.checkField('ignore', [])
    config.checkField('whitelist', None, hasDefault=True)

    # Color override
    config.checkField('color', None, hasDefault=True)

    # STLs merge and simplification
    config.checkField('mergeSTLs', 'no', valuesList=[
        'no', 'visual', 'collision', 'all'])
    config.checkField('maxSTLSize', 3)
    config.checkField('simplifySTLs', 'no', valuesList=[
        'no', 'visual', 'collision', 'all'])

    # Post-import commands to execute
    config.checkField('postImportCommands', [])

    config['outputDirectory'] = robot_folder_path
    config['dynamicsOverride'] = {}

    # Add collisions=true configuration on parts
    config.checkField('useCollisionsConfigurations', True)

    # ROS support
    config.checkField('packageName', '')
    config.checkField('addDummyBaseLink', False)
    config.checkField('robotName', 'onshape')

    # additional XML code to insert
    if config['outputFormat'] == 'urdf':
        config.checkField('additionalUrdfFile', '')
        additionalFileName = config['additionalUrdfFile']
    else:                                                           # outputFormat can only be 'urdf' or 'sdf'
        config.checkField('additionalSdfFile', '')
        additionalFileName = config['addionalSdfFile']

    if additionalFileName == '':
        config['additionalXML'] = ''
    else:
        with open(robot_folder_path + additionalFileName, 'r') as additionalXMLFile:
            config['additionalXML'] = additionalXMLFile.read()

    # Creating dynamics override array
    config.checkField('dynamics', {})
    tmp = config['dynamics']
    for key in tmp:
        if tmp[key] == 'fixed':
            config['dynamicsOverride'][key.lower()] = {"com": [0, 0, 0], "mass": 0, "inertia": [
                0, 0, 0, 0, 0, 0, 0, 0, 0]}
        else:
            config['dynamicsOverride'][key.lower()] = tmp[key]

    # Deal with output directory creation/permission verification
    if not (os.path.isdir(config['outputDirectory']) and os.access(config['outputDirectory'], os.W_OK)):
        try:
            os.makedirs(config['outputDirectory'])
        except FileExistsError:
            if os.path.isdir(config['outputDirectory']):
                raise Exception(f'The output directory {config["outputDirectory"]} cannot be used, it seems the directory exists but is not writeable.')
            else:
                raise Exception(f'The output directory {config["outputDirectory"]} cannot be used, it seems there is a file with the same name.')
        except PermissionError:
            raise Exception(f'The output directory {config["outputDirectory"]} cannot be used, it seems there aren\'t sufficient permissions.')

    # Checking that OpenSCAD is present
    if config['useScads']:
        print( Style.BRIGHT + '* Checking OpenSCAD presence...' + Style.RESET_ALL)
        if os.system('openscad -v 2> /dev/null') != 0:
            print(Fore.RED + "Can't run openscad -v, disabling OpenSCAD support" + Style.RESET_ALL)
            # print(Fore.BLUE + "TIP: consider installing openscad" + Style.RESET_ALL)
            # print(Fore.BLUE + "sudo add-apt-repository ppa:openscad/releases" + Style.RESET_ALL)
            # print(Fore.BLUE + "sudo apt-get update" + Style.RESET_ALL)
            # print(Fore.BLUE + "sudo apt-get install openscad" + Style.RESET_ALL)

            config['useScads'] = False

    # Checking that MeshLab is present
    if config['simplifySTLs']:
        print(
            Style.BRIGHT +
            '* Checking MeshLab presence...' +
            Style.RESET_ALL)
        if not os.path.exists('/usr/bin/meshlabserver') != 0:
            print(Fore.RED + "No /usr/bin/meshlabserver, disabling STL simplification support" + Style.RESET_ALL)
            # print(Fore.BLUE + "TIP: consider installing meshlab:" + Style.RESET_ALL)
            # print(Fore.BLUE + "sudo apt-get install meshlab" + Style.RESET_ALL)

            config['simplifySTLs'] = False

    # Checking that versionId and workspaceId are not set on same time
    if config['versionId'] != '' and config['workspaceId'] != '':
        print(Fore.RED + "You can't specify workspaceId AND versionId")

    return config
