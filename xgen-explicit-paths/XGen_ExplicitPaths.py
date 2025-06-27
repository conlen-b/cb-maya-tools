# -*- coding: utf-8 -*-

"""
XGen_ExplicitPaths.py: A script to set XGen file paths to explicit when batch rendering, and back to relative when done.
Updated 6/17/2025
After running this script, in the xGen window press File > Export Patches for Batch Render
"""

__author__ = "Conlen Breheny"
__copyright__ = "Copyright 2025, Conlen Breheny"
__version__ = "1.3"

import maya.cmds as cmds
import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.XgExternalAPI as xge
from enum import Enum

def _path_to_forward_slashes(in_path) -> str:
    """
    A helper function to convert file paths to file paths with forward slashes

    :param in_path: string argument representing a path on disk to be converted
    :return: string representing a path on disk with slashes ensured as forward slashes
    """

    if type(in_path) is not str: 
        raise TypeError("in_path argument must be string!")
    return ''.join([char if char != '\\' else '/' for char in in_path])

class _ZspcXgenPathsMode(Enum):
    """
    Enum representing the XGen path setting mode.

    Attributes:
        EXPLICIT: Set all XGen paths to absolute paths.
        RELATIVE: Set all XGen paths to project-relative paths.
    """
    EXPLICIT = 0
    RELATIVE = 1

def _zspc_xgen_paths_GUI() -> None:
    """
    Opens the Maya GUI window for the script

    :return: Void
    """

    #If GUI window is already open, close it
    if cmds.window("zspc_xgen_paths",exists=True):
        cmds.deleteUI("zspc_xgen_paths")

    #Initialize window
    inputWindow_xgenPaths = cmds.window("zspc_xgen_paths",title="XGen Set Explicit Paths", w=300, h=300)
    cmds.columnLayout(adj=True)

    #UI Elements
    cmds.text(label='Before rendering, use this script to set paths to explicit, then\n' \
                    'in XGen go to File > Export Patches for Batch Render\n\n' \
                    'If you need to set the paths back to relative and the paths\n' \
                    'do not match the current project directory listed below, replace\n' \
                    'the below path with the matching project directory\n')

    #Run button UI elements
    project_dir = cmds.workspace(q=True, rd=True)
    input_project_path = cmds.textFieldGrp(l = "Project Directory", editable=True, text=project_dir)
    #Reading value from UI element when pressed
    cmds.button(label = "Set Explicit Paths",
                command=lambda *args:_zspc_xgen_paths_run(mode=_ZspcXgenPathsMode.EXPLICIT,
                                                            project_path=cmds.textFieldGrp(input_project_path,
                                                                                            query=True,
                                                                                            text=True)))
    cmds.text(label=' ')
    cmds.button(label = "Set Relative Paths",
                command=lambda *args: _zspc_xgen_paths_run(mode=_ZspcXgenPathsMode.RELATIVE,
                                                            project_path=cmds.textFieldGrp(input_project_path,
                                                                                            query=True,
                                                                                            text=True)))

    #Open window
    cmds.showWindow(inputWindow_xgenPaths)


def _zspc_xgen_paths_run(mode: _ZspcXgenPathsMode, project_path: str, *args) -> None: #*args because maya button always passes boolean argument
    """
    Sets the XGen paths to explicit or relative depending on the mode
    
    :param mode: _ZspcXgenPathsMode Enum argument representing a mode
    :param project_path: string argument representing a path to the Maya project directory.
        If the paths are currently explicitly set to a path not matching the current project, this
        can be changed to reflect those to properly set the path back to relative.
    :return: Void
    """
    root_path = _path_to_forward_slashes(project_path)
    root_path = root_path if (root_path[-1] == "/") else (root_path + "/")
    description_expression_string = "${DESC}"
    project_expression_string = "${PROJECT}"

    if not xgg.Maya:
        cmds.error("XGen isn't loaded!")
        return

    #palette is collection, use palettes to get collections first.
    collections = xg.palettes()
    for collection in collections:

        #Set collection path to explicit/relative
        collection_path = xg.getAttr("xgDataPath", collection )
        if mode == _ZspcXgenPathsMode.EXPLICIT:
            newcollection_path = collection_path.replace(project_expression_string, root_path)
            xg.setAttr("xgDataPath", newcollection_path, collection )
        if mode == _ZspcXgenPathsMode.RELATIVE:
            newcollection_path = collection_path.replace(root_path, project_expression_string)
            xg.setAttr("xgDataPath", newcollection_path, collection )

        #Use descriptions to get description of each collection
        descriptions = xg.descriptions(collection)
        for description in descriptions:
            objects = xg.objects(collection, description, True)

            #Get active objects, e.g. SplinePrimtives
            for object in objects:
                attrs = xg.allAttrs(collection, description, object)
                for attr in attrs:

                    #Set object path attributes to explicit/relative
                    value = xg.getAttr(attr, collection, description, object)
                    path = root_path + "xGen/collections/" + collection + "/" + description
                    search_string = path if mode == _ZspcXgenPathsMode.RELATIVE else description_expression_string
                    if search_string not in value:
                        continue

                    if mode == _ZspcXgenPathsMode.EXPLICIT:
                        newValue = value.replace(description_expression_string, path)
                        xg.setAttr(attr, newValue, collection, description, object)
                    elif mode == _ZspcXgenPathsMode.RELATIVE:
                        newValue = value.replace(path, description_expression_string)
                        xg.setAttr(attr, newValue, collection, description, object)

    #Refresh the UI to reflect path changes
    de = xgg.DescriptionEditor
    de.refresh("Full")

if __name__ == "__main__":
    _zspc_xgen_paths_GUI()
