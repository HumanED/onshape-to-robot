decently useful
- integrate the Onshape API code better - specifically make the client take the parse config instead of loading the file again
- make sure all paths are done properly through os.path and joins not as strings and concatenation
- exception handling - before it was just print statements and sys.exit so get rid of all of that and then review the Exception classes, maybe make more suitable ones and so on

minor
- review comments in load_robot.py has basic one liners which should be expanded once more understood

very minor
- some more tidying up in config.py could be used but should work all right now

in general
- improve general code quality, both structure and naming/aestethic wise
- review/addd comments

config options to implement:
- specifying a workspace
- specifying a version (if I'm not mistaken this should be either or with selecting a workspace - only one at a time)
