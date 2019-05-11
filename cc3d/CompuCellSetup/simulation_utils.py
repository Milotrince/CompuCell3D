from cc3d import CompuCellSetup
from cc3d.core.XMLUtils import CC3DXMLListPy


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


def extract_type_names_and_ids()->dict:
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
