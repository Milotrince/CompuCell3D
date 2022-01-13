
from weakref import ref
import cc3d.player5.DefaultData as DefaultData
import cc3d.player5.Configuration as Configuration
import cc3d
from cc3d.core.enums import *
from cc3d.core.GraphicsOffScreen.GenericDrawer import GenericDrawer
from cc3d.player5.Graphics.GraphicsWindowData import GraphicsWindowData
from cc3d.core.GraphicsUtils.ScreenshotData import ScreenshotData
import cc3d.CompuCellSetup
from cc3d.player5.Utilities import qcolor_to_rgba, cs_string_to_typed_list
import sys
from collections import OrderedDict

MODULENAME = '---- JupyterGraphicsFrameWidget.py: '

# new stuff
import vtk
from ipyvtklink.viewer import ViewInteractiveWidget
from cc3d import CompuCellSetup


class JupyterGraphicsFrameWidget():
    def __init__(self):
       
        self.is_screenshot_widget = False

        # MDIFIX

        self.plane = None
        self.planePos = None

        self.status_bar = None

        self.proj_combo_box_act = None
        self.proj_combo_box = None
        self.proj_spin_box = None
        self.field_combo_box_act = None
        self.field_combo_box = None
        self.screenshot_act = None

        self.currentProjection = None
        self.xyPlane = None
        self.xzPlane = None
        self.yzPlane = None
        self.xyMaxPlane = None
        self.xzMaxPlane = None
        self.yzMaxPlane = None

        self.draw3DFlag = False

        self.fieldTypes = None


        # todo 5 - adding generic drawer

        sim = cc3d.CompuCellSetup.persistent_globals.simulator
        boundary_strategy = None
        if sim:
            boundary_strategy = sim.getBoundaryStrategy()

        self.gd = GenericDrawer(boundary_strategy=boundary_strategy)
        self.gd.set_interactive_camera_flag(True)
        self.gd.set_pixelized_cartesian_scene(Configuration.getSetting("PixelizedCartesianFields"))

        # placeholder for current screenshot data
        self.current_screenshot_data = None


        self.camera2D = self.gd.get_active_camera()
        self.camera3D = self.gd.get_renderer().MakeCamera()

        
        
#         set bsd basic simulation data
#         access through pg > screenshot manager . bsd
        # placeholder for currently used basic simulation data
        self.pg = CompuCellSetup.persistent_globals
        self.current_bsd = self.pg.screenshot_manager.bsd
        
        
        self.ren = self.gd.get_renderer()
        
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.SetOffScreenRendering(1)
        self.renWin.SetSize(600, 600)
        self.renWin.AddRenderer(self.ren)
        
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renWin)
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.iren.SetInteractorStyle(style)

        # Add actor to scene
#         self.ren.AddActor(actor)
        
    

        self.metadata_fetcher_dict = {
            'CellField': self.get_cell_field_metadata,
            'ConField': self.get_con_field_metadata,
            'ScalarField': self.get_con_field_metadata,
            'ScalarFieldCellLevel': self.get_con_field_metadata,
            'VectorField': self.get_vector_field_metadata,
            'VectorFieldCellLevel': self.get_vector_field_metadata,
        }

        
        

    def copy_camera(self, src, dst):
        """
        Copies camera settings
        :param src: 
        :param dst: 
        :return: None
        """
        dst.SetClippingRange(src.GetClippingRange())
        dst.SetFocalPoint(src.GetFocalPoint())
        dst.SetPosition(src.GetPosition())
        dst.SetViewUp(src.GetViewUp())

    def get_metadata(self, field_name, field_type):
        """
        Fetches a dictionary that summarizes graphics/configs settings for the current scene
        :param field_name: {str} field name
        :param field_type: {str} field type
        :return: {dict}
        """
        try:
            metadata_fetcher_fcn = self.metadata_fetcher_dict[field_type]
        except KeyError:
            return {}

        metadata = metadata_fetcher_fcn(field_name=field_name, field_type=field_type)

        return metadata

    def get_cell_field_metadata(self, field_name, field_type):
        """
        Returns dictionary of auxiliary information needed to cell field
        :param field_name:{str} field_name
        :param field_type: {str} field type
        :return: {dict}
        """

        metadata_dict = self.get_config_metadata(field_name=field_name, field_type=field_type)
        return metadata_dict

    def get_config_metadata(self, field_name, field_type):
        """
        Returns dictionary of auxiliary information needed to render borders
        :param field_name:{str} field_name
        :param field_type: {str} field type
        :return: {dict}
        """
        metadata_dict = {}
        metadata_dict['BorderColor'] = qcolor_to_rgba(Configuration.getSetting('BorderColor'))
        metadata_dict['ClusterBorderColor'] = qcolor_to_rgba(Configuration.getSetting('ClusterBorderColor'))
        metadata_dict['BoundingBoxColor'] = qcolor_to_rgba(Configuration.getSetting('BoundingBoxColor'))
        metadata_dict['AxesColor'] = qcolor_to_rgba(Configuration.getSetting('AxesColor'))
        metadata_dict['ContourColor'] = qcolor_to_rgba(Configuration.getSetting('ContourColor'))
        metadata_dict['WindowColor'] = qcolor_to_rgba(Configuration.getSetting('WindowColor'))
        # todo - fix color of fpp links
        metadata_dict['FPPLinksColor'] = qcolor_to_rgba(Configuration.getSetting('FPPLinksColor'))

        metadata_dict['ShowHorizontalAxesLabels'] = Configuration.getSetting('ShowHorizontalAxesLabels')
        metadata_dict['ShowVerticalAxesLabels'] = Configuration.getSetting('ShowVerticalAxesLabels')

        # type-color map
        type_color_map_dict = OrderedDict()
        config_type_color_map = Configuration.getSetting("TypeColorMap")
        for type_id, qt_color in list(config_type_color_map.items()):
            type_color_map_dict[type_id] = qcolor_to_rgba(qt_color)

        metadata_dict['TypeColorMap'] = type_color_map_dict

        return metadata_dict

    def get_con_field_metadata(self, field_name, field_type):
        """
        Returns dictionary of auxiliary information needed to render a give scene
        :param field_name:{str} field_name
        :param field_type: {str} field type
        :return: {dict}
        """

        # metadata_dict = {}
        metadata_dict = self.get_config_metadata(field_name=field_name, field_type=field_type)
        con_field_name = field_name
        metadata_dict['MinRangeFixed'] = Configuration.getSetting("MinRangeFixed", con_field_name)
        metadata_dict['MaxRangeFixed'] = Configuration.getSetting("MaxRangeFixed", con_field_name)
        metadata_dict['MinRange'] = Configuration.getSetting("MinRange", con_field_name)
        metadata_dict['MaxRange'] = Configuration.getSetting("MaxRange", con_field_name)
        metadata_dict['ContoursOn'] = Configuration.getSetting("ContoursOn", con_field_name)
        metadata_dict['NumberOfContourLines'] = Configuration.getSetting("NumberOfContourLines", field_name)
        metadata_dict['ScalarIsoValues'] = cs_string_to_typed_list(
            Configuration.getSetting("ScalarIsoValues", field_name))
        metadata_dict['LegendEnable'] = Configuration.getSetting("LegendEnable", field_name)
        metadata_dict['DisplayMinMaxInfo'] = Configuration.getSetting("DisplayMinMaxInfo")

        return metadata_dict

    def get_vector_field_metadata(self, field_name, field_type):
        """
        Returns dictionary of auxiliary information needed to render a give scene
        :param field_name:{str} field_name
        :param field_type: {str} field type
        :return: {dict}
        """

        metadata_dict = self.get_con_field_metadata(field_name=field_name, field_type=field_type)
        metadata_dict['ArrowLength'] = Configuration.getSetting('ArrowLength', field_name)
        metadata_dict['FixedArrowColorOn'] = Configuration.getSetting('FixedArrowColorOn', field_name)
        metadata_dict['ArrowColor'] = qcolor_to_rgba(Configuration.getSetting('ArrowColor', field_name))
        metadata_dict['ScaleArrowsOn'] = Configuration.getSetting('ScaleArrowsOn', field_name)

        return metadata_dict
    
    def compute_current_screenshot_data(self):
        """
        Computes/populates Screenshot Description data based ont he current GUI configuration
        for the current window
        :return: {screenshotData}
        """

        scr_data = ScreenshotData()
        self.store_gui_vis_config(scr_data=scr_data)

#         projection_name = str(self.proj_combo_box.currentText())
        projection_name = '2D'
#         projection_position = int(self.proj_spin_box.value())
        projection_position = 0

#         field_name, field_type = self.get_current_field_name_and_type()
        field_name = ''
        field_type = ''
        scr_data.plotData = (field_name, field_type)

        metadata = self.get_metadata(field_name=scr_data.plotData[0], field_type=scr_data.plotData[1])

        if projection_name == '3D':
            scr_data.spaceDimension = '3D'
        else:
            scr_data.spaceDimension = '2D'
            scr_data.projection = projection_name
            scr_data.projectionPosition = projection_position

        scr_data.metadata = metadata

        return scr_data
    

    def initialize_scene(self):
        """
        initialization function that sets up field extractor for the generic Drawer
        :return:
        """
        self.current_screenshot_data = self.compute_current_screenshot_data()
        self.gd.set_field_extractor(field_extractor=self.pg.persistent_holder['field_extractor'])


    def draw(self):
        """
        Main drawing function - calls ok_to_draw fcn from the GenericDrawer. All drawing happens there
        :param basic_simulation_data: {instance of BasicSimulationData}
        :return: None
        """
#         we are setting bsd in init
#         self.current_bsd = basic_simulation_data

        if self.current_screenshot_data is None:
            self.initialize_scene()

        self.gd.clear_display()

        self.gd.draw(screenshot_data=self.current_screenshot_data, bsd=self.current_bsd, screenshot_name='')

        # this call seems to be needed to refresh qvtk widget
        self.gd.get_renderer().ResetCameraClippingRange()
        
        # essential call to refresh screen . otherwise need to move/resize graphics window
#         qt stuff >:(
#         self.Render() 
        # get_view_test.render()
    
    
    

    def store_gui_vis_config(self, scr_data):
        """
        Stores visualization settings such as cell borders, on/or cell on/off etc...

        :param scr_data: {instance of ScreenshotDescriptionData}
        :return: None
        """
#         tvw = self.parentWidget()

#         scr_data.cell_borders_on = tvw.border_act.isChecked()
#         scr_data.cells_on = tvw.cells_act.isChecked()
#         scr_data.cluster_borders_on = tvw.cluster_border_act.isChecked()
#         scr_data.cell_glyphs_on = tvw.cell_glyphs_act.isChecked()
#         scr_data.fpp_links_on = tvw.fpp_links_act.isChecked()
        scr_data.lattice_axes_on = Configuration.getSetting('ShowHorizontalAxesLabels') or Configuration.getSetting(
            'ShowVerticalAxesLabels')
        scr_data.lattice_axes_labels_on = Configuration.getSetting("ShowAxes")
        scr_data.bounding_box_on = Configuration.getSetting("BoundingBoxOn")

        invisible_types = Configuration.getSetting("Types3DInvisible")
        invisible_types = invisible_types.strip()

        if invisible_types:
            scr_data.invisible_types = list([int(x) for x in invisible_types.split(',')])
        else:
            scr_data.invisible_types = []
    
            
    def view_widget(self):
        self.ren.ResetCamera()
        return ViewInteractiveWidget(self.renWin)