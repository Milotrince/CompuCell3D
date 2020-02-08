from cc3d import CompuCellSetup
from cc3d.core.XMLUtils import CC3DXMLListPy
from pathlib import Path


class CC3DCPlusPlusError(Exception):
    def __init__(self, _message):
        self.message = _message

    def __str__(self):
        return repr(self.message)

def set_output_dir(output_dir: str, abs_path: bool = False) -> None:
    """
    Sets output directory to output_dir. If  abs_path is False
    then the directory path will be w.r.t to workspace directory
    Otherwise it is expected that user provides absolute output path
    :param output_dir: directory name - relative (w.r.t to workspace dir) or absolute
    :param abs_path:  flag specifying if user provided absolute or relative path
    :return:
    """
    pg = CompuCellSetup.persistent_globals
    if abs_path:
        pg.set_output_dir(output_dir=output_dir)
    else:
        pg.set_output_dir(output_dir=str(Path(pg.workspace_dir).joinpath(output_dir)))


def stop_simulation():
    """
    Stops simulation
    :return:
    """
    CompuCellSetup.persistent_globals.user_stop_simulation_flag = True


# legacy api
stopSimulation = stop_simulation


def extract_lattice_type():
    """
    Fetches lattice type
    :return:
    """
    # global cc3dXML2ObjConverter
    cc3d_xml2_obj_converter = CompuCellSetup.persistent_globals.cc3d_xml_2_obj_converter

    if cc3d_xml2_obj_converter.root.findElement("Potts"):
        # dealing with regular cc3dml
        if cc3d_xml2_obj_converter.root.getFirstElement("Potts").findElement("LatticeType"):
            return cc3d_xml2_obj_converter.root.getFirstElement("Potts").getFirstElement("LatticeType").getText()
    else:
        # dealing with LDF file
        if cc3d_xml2_obj_converter.root.findElement("Lattice"):
            return cc3d_xml2_obj_converter.root.getFirstElement("Lattice").getAttribute('Type')

    return ''


def extract_type_names_and_ids() -> dict:
    """
    Extracts type_name to type id mapping from CC3DXML
    :return {dict}:
    """

    cc3d_xml2_obj_converter = CompuCellSetup.persistent_globals.cc3d_xml_2_obj_converter
    if cc3d_xml2_obj_converter is None:
        return {}

    plugin_elements = cc3d_xml2_obj_converter.root.getElements("Plugin")

    list_plugin = CC3DXMLListPy(plugin_elements)
    type_id_type_name_dict = {}
    for element in list_plugin:

        if element.getAttribute("Name") == "CellType":
            cell_types_elements = element.getElements("CellType")

            list_cell_type_elements = CC3DXMLListPy(cell_types_elements)
            for cell_type_element in list_cell_type_elements:
                type_name = cell_type_element.getAttribute("TypeName")
                type_id = cell_type_element.getAttributeAsInt("TypeId")
                type_id_type_name_dict[type_id] = type_name

    return type_id_type_name_dict


def extract_material_names_and_ids() -> dict:
    """
    Extracts material name to material id mapping from CC3DXML
    :return {dict}:
    """

    cc3d_xml2_obj_converter = CompuCellSetup.persistent_globals.cc3d_xml_2_obj_converter
    if cc3d_xml2_obj_converter is None:
        return {}

    if not check_ncmaterials_active():
        return {}

    plugin_elements = cc3d_xml2_obj_converter.root.getElements("Plugin")

    list_plugin = CC3DXMLListPy(plugin_elements)
    material_id_material_name_dict = {}
    for element in list_plugin:

        if element.getAttribute("Name") == "NCMaterials":
            material_elements = element.getElements("NCMaterial")

            list_material_elements = CC3DXMLListPy(material_elements)
            material_id = 0
            for material_element in list_material_elements:
                material_name = material_element.getAttribute("Material")
                material_id_material_name_dict[material_id] = material_name
                material_id += 1

    return material_id_material_name_dict


def check_ncmaterials_active():
    """
    Checks status of NCMaterials plugin; returns true if active, false if inactive
    :return {bool}:
    """
    if CompuCellSetup.persistent_globals.simulator is not None:
        return CompuCellSetup.persistent_globals.simulator.pluginManager.isLoaded('NCMaterials')
    else:
        return False


def check_for_cpp_errors(sim):
    if sim.getRecentErrorMessage() != "":
        raise CC3DCPlusPlusError(sim.getRecentErrorMessage())
