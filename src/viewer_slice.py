import vtk
from typing import Tuple, List
from pubsub import pub as Publisher

from slice_data import SliceData
import constants as const
from slice_ import Slice
from styles import CrossInteractorStyle, CrossInteractorStyle_2
from vtk_utils import TextZero
from project import Project

# Single view
class ViewerDemo:
    def __init__(self, orientation="AXIAL") -> None:
        self.number_slices = 1
        self.orientation = orientation
        self.scroll_position = 0
        self.wl_text = None
        self.orientation_texts = []
        self.pointer_actor = None

        self.interactor = vtk.vtkRenderWindowInteractor()
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetSize(500, 500)
        self.interactor.SetRenderWindow(renderWindow)

        self.pick = vtk.vtkWorldPointPicker()
        self.interactor.SetPicker(self.pick)
        
    def create_slice_window(self) -> SliceData:
        renderer = vtk.vtkRenderer()
        self.interactor.GetRenderWindow().AddRenderer(renderer)

        actor = vtk.vtkImageActor()
        # # Turn on/off linear interpolation of the image when rendering.
        actor.InterpolateOn()

        slice_data = SliceData()
        slice_data.SetOrientation(self.orientation)
        slice_data.renderer = renderer
        slice_data.actor = actor

        renderer.AddActor(actor)
        renderer.AddActor(slice_data.text.actor)

        return slice_data
    
    def __build_cross_lines(self) -> None:
        # Generate a 3D cursor representation.
        cross = vtk.vtkCursor3D()
        # Turn every part of the 3D cursor on or off.
        cross.AllOff()
        # Turn on/off the wireframe axes.
        cross.AxesOn()
        self.cross = cross

        cross_mapper = vtk.vtkPolyDataMapper()
        cross_mapper.SetInputConnection(cross.GetOutputPort())
        cross_actor = vtk.vtkActor()
        cross_actor.SetMapper(cross_mapper)
        cross_actor.GetProperty().SetColor(1, 0, 0)
        cross_actor.VisibilityOn()
        cross_actor.PickableOff()
        self.cross_actor = cross_actor

        self.slice_data.renderer.AddActor(cross_actor)

    def get_coordinate_cursor(self, mx: int, my: int, picker=None) -> Tuple:
        '''
        Given the mx, my screen position returns the x, y, z position in world
        coordinates.
        Parameters
            mx (int): x position.
            my (int): y position
            picker: the picker used to get calculate the voxel coordinate.
        Returns:
            world coordinate (x, y, z)
        '''
        if picker is None:
            picker = self.pick

        slice_data = self.slice_data
        renderer = slice_data.renderer

        picker.Pick(mx, my, 0, renderer)
        x, y, z = picker.GetPickPosition()
        bounds = slice_data.actor.GetBounds()
        if bounds[0] == bounds[1]:
            x = bounds[0]
        elif bounds[2] == bounds[3]:
            y = bounds[2]
        elif bounds[4] == bounds[5]:
            z = bounds[4]
        return x, y, z
    
    def __update_camera(self) -> None:
        orientation = self.orientation
        camera = self.camera
        camera.SetFocalPoint(0, 0, 0)
        if orientation == "AXIAL":
            camera.SetViewUp(0, 1, 0)
            camera.SetPosition(0, 0, 1)
        elif orientation == "CORONAL":
            camera.SetViewUp(0, 0, -1)
            camera.SetPosition(0, 1, 0)
        elif orientation == "SAGITAL":
            camera.SetViewUp(0, 0, -1)
            camera.SetPosition(-1, 0, 0)
        camera.ParallelProjectionOn()

    def __update_display_extent(self, image: vtk.vtkImageData) -> None:
        self.slice_data.actor.SetDisplayExtent(image.GetExtent())
        self.slice_data.renderer.ResetCameraClippingRange()

    def SetWLText(self, window_level: int, window_width: int) -> None:
        if self.wl_text:
            self.wl_text.SetValue("WL: %d WW: %d" % (window_level, window_width))

    def EnableText(self) -> None:
        if self.wl_text is None:
            project = Project()

            # Window level text
            wl_text = TextZero()
            wl_text.SetSize(const.TEXT_SIZE_LARGE)
            wl_text.SetPosition(const.TEXT_POS_LEFT_UP)
            self.wl_text = wl_text
            
            self.SetWLText(project.window_level, project.window_width)
            self.slice_data.renderer.AddActor(wl_text.actor)

            # Orientation text
            if self.orientation == "AXIAL":
                values = ["R", "L", "A", "P"]
            elif self.orientation == "SAGITAL":
                values = ["P", "A", "T", "B"]
            else:
                values = ["R", "L", "T", "B"]

            left_text = TextZero()
            left_text.SetSize(const.TEXT_SIZE_LARGE)
            left_text.SetPosition(const.TEXT_POS_VCENTRE_LEFT)
            left_text.SetValue(values[0])

            right_text = TextZero()
            right_text.SetSize(const.TEXT_SIZE_LARGE)
            right_text.SetPosition(const.TEXT_POS_VCENTRE_RIGHT_ZERO)
            right_text.SetValue(values[1])

            up_text = TextZero()
            up_text.SetSize(const.TEXT_SIZE_LARGE)
            up_text.SetPosition(const.TEXT_POS_HCENTRE_UP)
            up_text.SetValue(values[2])

            down_text = TextZero()
            down_text.SetSize(const.TEXT_SIZE_LARGE)
            down_text.SetPosition(const.TEXT_POS_HCENTRE_DOWN_ZERO)
            down_text.SetValue(values[3])

            orientation_texts = [left_text, right_text, up_text, down_text]
            self.orientation_texts = orientation_texts

            for text in orientation_texts:
                self.slice_data.renderer.AddActor(text.actor)

    def calculate_matrix_position(self, coord: Tuple) -> Tuple:
        x, y, z = coord
        xi, xf, yi, yf, zi, zf = self.slice_data.actor.GetBounds()
        if self.orientation == "AXIAL":
            mx = round((x - xi) / self.slice_.spacing[0], 0)
            my = round((y - yi) / self.slice_.spacing[1], 0)
        elif self.orientation == "CORONAL":
            mx = round((x - xi) / self.slice_.spacing[0], 0)
            my = round((z - zi) / self.slice_.spacing[2], 0)
        elif self.orientation == "SAGITAL":
            mx = round((y - yi) / self.slice_.spacing[1], 0)
            my = round((z - zi) / self.slice_.spacing[2], 0)
        return int(mx), int(my)
    
    def get_slice_pixel_coord_by_world_pos(self, wx, wy, wz) -> Tuple:
        coord = (wx, wy, wz)
        px, py = self.calculate_matrix_position(coord)
        return px, py
    
    def calcultate_scroll_position(self, x: int, y: int) -> Tuple:
        # Based in the given coord (x, y), returns a list with the scroll positions for each
        # orientation, being the first position the sagital, second the coronal and the last, axial.
        if self.orientation == "AXIAL":
            axial = self.slice_data.number
            coronal = y
            sagital = x
        elif self.orientation == "CORONAL":
            axial = y
            coronal = self.slice_data.number
            sagital = x
        elif self.orientation == "SAGITAL":
            axial = y
            coronal = x
            sagital = self.slice_data.number
        return sagital, coronal, axial

    def UpdateSlicesPosition(self, position: Tuple) -> None:
        px, py = self.get_slice_pixel_coord_by_world_pos(*position)
        coord = self.calcultate_scroll_position(px, py)
        print(f"sagital={coord[0]}, coronal={coord[1]}, axial={coord[2]}")

    def SetCrossFocalPoint(self, position: List) -> None:
        self.cross.SetFocalPoint(position)

    def UpdateRender(self) -> None:
        self.interactor.Render()

    def SetInteractorStyle(self) -> None:
        # style = vtk.vtkInteractorStyleTrackballCamera()
        style = CrossInteractorStyle(self)
        self.interactor.SetInteractorStyle(style)
        self.style = style

    def set_slice_number(self, index: int) -> None:
        index = max(index, 0)
        max_slice_number = self.slice_.GetNumberOfSlices(self.orientation)
        index = min(index, max_slice_number - 1)

        image = self.slice_.GetSlices(self.orientation, index, self.number_slices)
        self.slice_data.actor.SetInputData(image)

        self.slice_data.SetNumber(index)

        self.__update_display_extent(image)
        self.cross.SetModelBounds(self.slice_data.actor.GetBounds())

    def SetInput(self) -> None:
        self.slice_data = self.create_slice_window()
        self.camera = self.slice_data.renderer.GetActiveCamera()

        self.__build_cross_lines()
        self.EnableText()

        self.slice_ = Slice()
        position = self.slice_.GetNumberOfSlices(self.orientation) // 2
        self.set_slice_number(position)
        self.scroll_position = position

        self.__update_camera()
        self.slice_data.renderer.ResetCamera()

        self.interactor.GetRenderWindow().Render()
        self.SetInteractorStyle()

    def OnScrollForward(self) -> None:
        min = 0
        position = self.scroll_position
        if position >= min:
            position = position - 1
            self.set_slice_number(position)
            self.scroll_position = position
            self.UpdateRender()

    def OnScrollBackward(self) -> None:
        max = self.slice_.GetMaxSliceNumber(self.orientation)
        position = self.scroll_position
        if position <= max:
            position = position + 1
            self.set_slice_number(position)
            self.scroll_position = position
            self.UpdateRender()

# Multi view
class SliceViewer:
    def __init__(self) -> None:
        self.number_slices = 1
        self.scroll_position_axial = 0
        self.scroll_position_coronal = 0
        self.scroll_position_sagital = 0
        
        # Axial view
        renderWindow_axial = vtk.vtkRenderWindow()
        renderWindow_axial.SetWindowName("AXIAL")
        renderWindow_axial.SetSize(350, 350)
        renderWindow_axial.SetPosition(0, 0)

        self.renderer_axial = vtk.vtkRenderer()
        renderWindow_axial.AddRenderer(self.renderer_axial)

        self.interactor_axial = vtk.vtkRenderWindowInteractor()
        self.interactor_axial.SetRenderWindow(renderWindow_axial)
        self.pick_axial = vtk.vtkWorldPointPicker()
        self.interactor_axial.SetPicker(self.pick_axial)

        # Coronal view
        renderWindow_coronal = vtk.vtkRenderWindow()
        renderWindow_coronal.SetWindowName("CORONAL")
        renderWindow_coronal.SetSize(350, 350)
        renderWindow_coronal.SetPosition(350, 0)

        self.renderer_coronal = vtk.vtkRenderer()
        renderWindow_coronal.AddRenderer(self.renderer_coronal)

        self.interactor_coronal = vtk.vtkRenderWindowInteractor()
        self.interactor_coronal.SetRenderWindow(renderWindow_coronal)
        self.pick_coronal = vtk.vtkWorldPointPicker()
        self.interactor_coronal.SetPicker(self.pick_coronal)

        # Sagital view
        renderWindow_sagital = vtk.vtkRenderWindow()
        renderWindow_sagital.SetWindowName("SAGITAL")
        renderWindow_sagital.SetSize(350, 350)
        renderWindow_sagital.SetPosition(700, 0)

        self.renderer_sagital = vtk.vtkRenderer()
        renderWindow_sagital.AddRenderer(self.renderer_sagital)

        self.interactor_sagital = vtk.vtkRenderWindowInteractor()
        self.interactor_sagital.SetRenderWindow(renderWindow_sagital)
        self.pick_sagital = vtk.vtkWorldPointPicker()
        self.interactor_sagital.SetPicker(self.pick_sagital)

        self.__bind_events()

    def __bind_events(self) -> None:
        Publisher.subscribe(self.SetInput, "Load mpr")
        Publisher.subscribe(self.startApp, "Start app")
        Publisher.subscribe(self.SetCrossFocalPoint, "Set cross focal point")
        Publisher.subscribe(self.UpdateRender, "Update mpr")
        
    def create_slice_window(self, orientation: str) -> SliceData:
        actor = vtk.vtkImageActor()
        # Turn on/off linear interpolation of the image when rendering.
        actor.InterpolateOn()

        slice_data = SliceData()
        slice_data.SetOrientation(orientation)
        slice_data.actor = actor

        if orientation == "AXIAL":
            renderer = self.renderer_axial
        elif orientation == "CORONAL":
            renderer = self.renderer_coronal
        else:
            renderer = self.renderer_sagital
        
        renderer.AddActor(actor)
        renderer.AddActor(slice_data.text.actor)
        return slice_data
    
    def __build_cross_lines(self) -> None:
        # Generate a 3D cursor representation.
        cross_axial = vtk.vtkCursor3D()
        # Turn every part of the 3D cursor on or off.
        cross_axial.AllOff()
        # Turn on/off the wireframe axes.
        cross_axial.AxesOn()
        self.cross_axial = cross_axial

        # Create a vtkUnsignedCharArray container and store the colors in it.
        color_array_axial = vtk.vtkUnsignedCharArray()
        color_array_axial.SetNumberOfComponents(3)
        color_array_axial.SetNumberOfTuples(3)
        color_array_axial.SetTuple(0, [0, 0, 255])
        color_array_axial.SetTuple(1, [0, 255, 0])
        color_array_axial.SetTuple(2, [255, 0, 0])
        self.color_array_axial = color_array_axial

        cross_mapper_axial = vtk.vtkPolyDataMapper()
        cross_mapper_axial.SetInputConnection(cross_axial.GetOutputPort())
        cross_actor_axial = vtk.vtkActor()
        cross_actor_axial.SetMapper(cross_mapper_axial)
        # cross_actor_axial.GetProperty().SetColor(1, 0, 0)
        # cross_actor_axial.GetProperty().SetLineWidth(2)
        cross_actor_axial.VisibilityOn()
        cross_actor_axial.PickableOff()

        self.renderer_axial.AddActor(cross_actor_axial)

        # Generate a 3D cursor representation.
        cross_coronal = vtk.vtkCursor3D()
        # Turn every part of the 3D cursor on or off.
        cross_coronal.AllOff()
        # Turn on/off the wireframe axes.
        cross_coronal.AxesOn()
        self.cross_coronal = cross_coronal

        # Create a vtkUnsignedCharArray container and store the colors in it.
        color_array_coronal = vtk.vtkUnsignedCharArray()
        color_array_coronal.SetNumberOfComponents(3)
        color_array_coronal.SetNumberOfTuples(3)
        color_array_coronal.SetTuple(0, [255, 0, 0])
        color_array_coronal.SetTuple(1, [0, 0, 255])
        color_array_coronal.SetTuple(2, [0, 255, 0])
        self.color_array_coronal = color_array_coronal

        cross_mapper_coronal = vtk.vtkPolyDataMapper()
        cross_mapper_coronal.SetInputConnection(cross_coronal.GetOutputPort())
        cross_actor_coronal = vtk.vtkActor()
        cross_actor_coronal.SetMapper(cross_mapper_coronal)
        # cross_actor_coronal.GetProperty().SetColor(1, 0, 0)
        # cross_actor_coronal.GetProperty().SetLineWidth(2)
        cross_actor_coronal.VisibilityOn()
        cross_actor_coronal.PickableOff()

        self.renderer_coronal.AddActor(cross_actor_coronal)

        # Generate a 3D cursor representation.
        cross_sagital = vtk.vtkCursor3D()
        # Turn every part of the 3D cursor on or off.
        cross_sagital.AllOff()
        # Turn on/off the wireframe axes.
        cross_sagital.AxesOn()
        self.cross_sagital = cross_sagital

        # Create a vtkUnsignedCharArray container and store the colors in it.
        color_array_sagital = vtk.vtkUnsignedCharArray()
        color_array_sagital.SetNumberOfComponents(3)
        color_array_sagital.SetNumberOfTuples(3)
        color_array_sagital.SetTuple(0, [0, 255, 0])
        color_array_sagital.SetTuple(1, [255, 0, 0])
        color_array_sagital.SetTuple(2, [0, 0, 255])
        self.color_array_sagital = color_array_sagital

        cross_mapper_sagital = vtk.vtkPolyDataMapper()
        cross_mapper_sagital.SetInputConnection(cross_sagital.GetOutputPort())
        cross_actor_sagital = vtk.vtkActor()
        cross_actor_sagital.SetMapper(cross_mapper_sagital)
        # cross_actor_sagital.GetProperty().SetColor(1, 0, 0)
        # cross_actor_sagital.GetProperty().SetLineWidth(2)
        cross_actor_sagital.VisibilityOn()
        cross_actor_sagital.PickableOff()

        self.renderer_sagital.AddActor(cross_actor_sagital)

    def get_coordinate_cursor(self, mx: int, my: int, orientation: str, picker: vtk.vtkWorldPointPicker) -> Tuple:
        if orientation == "AXIAL":
            slice_data = self.slice_data_axial
            renderer = self.renderer_axial
        elif orientation == "CORONAL":
            slice_data = self.slice_data_coronal
            renderer = self.renderer_coronal
        else:
            slice_data = self.slice_data_sagital
            renderer = self.renderer_sagital

        picker.Pick(mx, my, 0, renderer)
        x, y, z = picker.GetPickPosition()
        bounds = slice_data.actor.GetBounds()
        if bounds[0] == bounds[1]:
            x = bounds[0]
        elif bounds[2] == bounds[3]:
            y = bounds[2]
        elif bounds[4] == bounds[5]:
            z = bounds[4]
        return x, y, z
    
    def __update_camera(self, orientation: str) -> None:
        if orientation == "AXIAL":
            camera_axial = self.renderer_axial.GetActiveCamera()
            camera_axial.SetFocalPoint(0, 0, 0)
            camera_axial.SetViewUp(0, 1, 0)
            camera_axial.SetPosition(0, 0, 1)
            camera_axial.ParallelProjectionOn()
        elif orientation == "CORONAL":
            camera_coronal = self.renderer_coronal.GetActiveCamera()
            camera_coronal.SetFocalPoint(0, 0, 0)
            camera_coronal.SetViewUp(0, 0, -1)
            camera_coronal.SetPosition(0, 1, 0)
            camera_coronal.ParallelProjectionOn()
        else:
            camera_sagital = self.renderer_sagital.GetActiveCamera()
            camera_sagital.SetFocalPoint(0, 0, 0)
            camera_sagital.SetViewUp(0, 0, -1)
            camera_sagital.SetPosition(-1, 0, 0)
            camera_sagital.ParallelProjectionOn()

    def __update_display_extent(self, image: vtk.vtkImageData, orientation: str) -> None:
        if orientation == "AXIAL":
            self.slice_data_axial.actor.SetDisplayExtent(image.GetExtent())
            self.renderer_axial.ResetCameraClippingRange()
        elif orientation == "CORONAL":
            self.slice_data_coronal.actor.SetDisplayExtent(image.GetExtent())
            self.renderer_coronal.ResetCameraClippingRange()
        else:
            self.slice_data_sagital.actor.SetDisplayExtent(image.GetExtent())
            self.renderer_sagital.ResetCameraClippingRange()

    def EnableText(self, orientation: str) -> None:
        project = Project()

        # Window level text
        wl_text = TextZero()
        wl_text.SetSize(const.TEXT_SIZE_SMALL)
        wl_text.SetPosition(const.TEXT_POS_LEFT_UP)
        wl_text.SetValue("WL: %d WW: %d" % (project.window_level, project.window_width))

        # Orientation text
        if orientation == "AXIAL":
            renderer = self.renderer_axial
            values = ["R", "L", "A", "P"]
        elif orientation == "SAGITAL":
            renderer = self.renderer_sagital
            values = ["P", "A", "T", "B"]
        else:
            renderer = self.renderer_coronal
            values = ["R", "L", "T", "B"]

        renderer.AddActor(wl_text.actor)

        left_text = TextZero()
        left_text.SetSize(const.TEXT_SIZE_SMALL)
        left_text.SetPosition(const.TEXT_POS_VCENTRE_LEFT)
        left_text.SetValue(values[0])

        right_text = TextZero()
        right_text.SetSize(const.TEXT_SIZE_SMALL)
        right_text.SetPosition(const.TEXT_POS_VCENTRE_RIGHT_ZERO)
        right_text.SetValue(values[1])

        up_text = TextZero()
        up_text.SetSize(const.TEXT_SIZE_SMALL)
        up_text.SetPosition(const.TEXT_POS_HCENTRE_UP)
        up_text.SetValue(values[2])

        down_text = TextZero()
        down_text.SetSize(const.TEXT_SIZE_SMALL)
        down_text.SetPosition(const.TEXT_POS_HCENTRE_DOWN_ZERO)
        down_text.SetValue(values[3])

        orientation_texts = [left_text, right_text, up_text, down_text]
        for text in orientation_texts:
            renderer.AddActor(text.actor)

    def calculate_matrix_position(self, orientation: str, coord: Tuple) -> Tuple:
        x, y, z = coord
        if orientation == "AXIAL":
            xi, xf, yi, yf, zi, zf = self.slice_data_axial.actor.GetBounds()
            mx = round((x - xi) / self.slice.spacing[0], 0)
            my = round((y - yi) / self.slice.spacing[1], 0)
        elif orientation == "CORONAL":
            xi, xf, yi, yf, zi, zf = self.slice_data_coronal.actor.GetBounds()
            mx = round((x - xi) / self.slice.spacing[0], 0)
            my = round((z - zi) / self.slice.spacing[2], 0)
        else:
            xi, xf, yi, yf, zi, zf = self.slice_data_sagital.actor.GetBounds()
            mx = round((y - yi) / self.slice.spacing[1], 0)
            my = round((z - zi) / self.slice.spacing[2], 0)
        return int(mx), int(my)
    
    def get_slice_pixel_coord_by_world_pos(self, orientation: str, wx: float, wy: float, wz: float) -> Tuple:
        coord = (wx, wy, wz)
        px, py = self.calculate_matrix_position(orientation, coord)
        return px, py
    
    def calcultate_scroll_position(self, orientation: str, x: int, y: int) -> Tuple:
        # Based in the given coord (x, y), returns a list with the scroll positions for each
        # orientation, being the first position the sagital, second the coronal and the last, axial.
        if orientation == "AXIAL":
            axial = self.slice_data_axial.number
            coronal = y
            sagital = x
        elif orientation == "CORONAL":
            axial = y
            coronal = self.slice_data_coronal.number
            sagital = x
        else:
            axial = y
            coronal = x
            sagital = self.slice_data_sagital.number
        return sagital, coronal, axial

    def UpdateSlicesPosition(self, orientation: str, position: List) -> None:
        px, py = self.get_slice_pixel_coord_by_world_pos(orientation, *position)
        sagital, coronal, axial = self.calcultate_scroll_position(orientation, px, py)
        if orientation == "AXIAL":
            self.set_slice_number(coronal, "CORONAL")
            self.scroll_position_coronal = coronal
            self.set_slice_number(sagital, "SAGITAL")
            self.scroll_position_sagital = sagital
            orientations = ["CORONAL", "SAGITAL"]
        elif orientation == "CORONAL":
            self.set_slice_number(axial, "AXIAL")
            self.scroll_position_axial = axial
            self.set_slice_number(sagital, "SAGITAL")
            self.scroll_position_sagital = sagital
            orientations = ["AXIAL", "SAGITAL"]
        else:
            self.set_slice_number(axial, "AXIAL")
            self.scroll_position_axial = axial
            self.set_slice_number(coronal, "CORONAL")
            self.scroll_position_coronal = coronal
            orientations = ["AXIAL", "CORONAL"]

        self.UpdateRender()
        # 3D
        Publisher.sendMessage("Update slice 3d", orientations=orientations)
        Publisher.sendMessage("Update volume")
        # Endoscopy
        # Publisher.sendMessage("Update camera position", position=position)
        # Publisher.sendMessage("Update volume")

    def SetCrossFocalPoint(self, position: List) -> None:
        self.cross_axial.SetFocalPoint(position)
        self.cross_axial.Update()
        self.cross_axial.GetOutput().GetCellData().SetScalars(self.color_array_axial)

        self.cross_coronal.SetFocalPoint(position)
        self.cross_coronal.Update()
        self.cross_coronal.GetOutput().GetCellData().SetScalars(self.color_array_coronal)
        
        self.cross_sagital.SetFocalPoint(position)
        self.cross_sagital.Update()
        self.cross_sagital.GetOutput().GetCellData().SetScalars(self.color_array_sagital)

    def UpdateRender(self) -> None:
        self.interactor_axial.Render()
        self.interactor_coronal.Render()
        self.interactor_sagital.Render()

    def SetInteractorStyle(self) -> None:
        style_axial = CrossInteractorStyle_2(self, "AXIAL")
        self.interactor_axial.SetInteractorStyle(style_axial)
        self.style_axial = style_axial

        style_coronal = CrossInteractorStyle_2(self, "CORONAL")
        self.interactor_coronal.SetInteractorStyle(style_coronal)
        self.style_coronal = style_coronal

        style_sagital = CrossInteractorStyle_2(self, "SAGITAL")
        self.interactor_sagital.SetInteractorStyle(style_sagital)
        self.style_sagital = style_sagital

    def set_slice_number(self, index: int, orientation: str) -> None:
        index = max(index, 0)
        index = min(index, self.slice.GetNumberOfSlices(orientation) - 1)
        image = self.slice.GetSlices(orientation, index, self.number_slices)

        if orientation == "AXIAL":
            self.slice_data_axial.actor.SetInputData(image)
            self.slice_data_axial.SetNumber(index)

            self.__update_display_extent(image, orientation)

            self.cross_axial.SetModelBounds(self.slice_data_axial.actor.GetBounds())
            self.cross_axial.Update()
            self.cross_axial.GetOutput().GetCellData().SetScalars(self.color_array_axial)
        elif orientation == "CORONAL":
            self.slice_data_coronal.actor.SetInputData(image)
            self.slice_data_coronal.SetNumber(index)

            self.__update_display_extent(image, orientation)

            self.cross_coronal.SetModelBounds(self.slice_data_coronal.actor.GetBounds())
            self.cross_coronal.Update()
            self.cross_coronal.GetOutput().GetCellData().SetScalars(self.color_array_coronal)
        else:
            self.slice_data_sagital.actor.SetInputData(image)
            self.slice_data_sagital.SetNumber(index)

            self.__update_display_extent(image, orientation)

            self.cross_sagital.SetModelBounds(self.slice_data_sagital.actor.GetBounds())
            self.cross_sagital.Update()
            self.cross_sagital.GetOutput().GetCellData().SetScalars(self.color_array_sagital)

    def SetInput(self) -> None:
        self.slice_data_axial = self.create_slice_window("AXIAL")
        self.slice_data_coronal = self.create_slice_window("CORONAL")
        self.slice_data_sagital = self.create_slice_window("SAGITAL")

        self.__build_cross_lines()

        self.EnableText("AXIAL")
        self.EnableText("CORONAL")
        self.EnableText("SAGITAL")

        self.slice = Slice()

        position_axial = self.slice.GetNumberOfSlices("AXIAL") // 2
        self.set_slice_number(position_axial, "AXIAL")
        self.scroll_position_axial = position_axial

        position_coronal = self.slice.GetNumberOfSlices("CORONAL") // 2
        self.set_slice_number(position_coronal, "CORONAL")
        self.scroll_position_coronal = position_coronal

        position_sagital = self.slice.GetNumberOfSlices("SAGITAL") // 2
        self.set_slice_number(position_sagital, "SAGITAL")
        self.scroll_position_sagital = position_sagital

        self.__update_camera("AXIAL")
        self.renderer_axial.ResetCamera()

        self.__update_camera("CORONAL")
        self.renderer_coronal.ResetCamera()

        self.__update_camera("SAGITAL")
        self.renderer_sagital.ResetCamera()

        self.interactor_axial.GetRenderWindow().Render()
        self.interactor_coronal.GetRenderWindow().Render()
        self.interactor_sagital.GetRenderWindow().Render()

        self.SetInteractorStyle()

    def OnScrollForward(self, orientation: str) -> None:
        min = 0
        if orientation == "AXIAL":
            position = self.scroll_position_axial
        elif orientation == "CORONAL":
            position = self.scroll_position_coronal
        else:
            position = self.scroll_position_sagital

        if position >= min:
            position = position - 1
            self.set_slice_number(position, orientation)
            if orientation == "AXIAL":
                self.scroll_position_axial = position
                x, y, z = self.cross_axial.GetFocalPoint()
                self.SetCrossFocalPoint([x, y, z])
            elif orientation == "CORONAL":
                self.scroll_position_coronal = position
                x, y, z = self.cross_coronal.GetFocalPoint()
                self.SetCrossFocalPoint([x, y, z])
            else:
                self.scroll_position_sagital = position
                x, y, z = self.cross_sagital.GetFocalPoint()
                self.SetCrossFocalPoint([x, y, z])

            self.UpdateRender()
            # 3D
            Publisher.sendMessage("Update slice 3d", orientations=[orientation])
            Publisher.sendMessage("Update volume")

    def OnScrollBackward(self, orientation: str) -> None:
        max = self.slice.GetMaxSliceNumber(orientation)
        if orientation == "AXIAL":
            position = self.scroll_position_axial
        elif orientation == "CORONAL":
            position = self.scroll_position_coronal
        else:
            position = self.scroll_position_sagital

        if position <= max:
            position = position + 1
            self.set_slice_number(position, orientation)
            if orientation == "AXIAL":
                self.scroll_position_axial = position
                x, y, z = self.cross_axial.GetFocalPoint()
                self.SetCrossFocalPoint([x, y, z])
            elif orientation == "CORONAL":
                self.scroll_position_coronal = position
                x, y, z = self.cross_coronal.GetFocalPoint()
                self.SetCrossFocalPoint([x, y, z])
            else:
                self.scroll_position_sagital = position
                x, y, z = self.cross_sagital.GetFocalPoint()
                self.SetCrossFocalPoint([x, y, z])

            self.UpdateRender()
            # 3D
            Publisher.sendMessage("Update slice 3d", orientations=[orientation])
            Publisher.sendMessage("Update volume")

    def startApp(self):
        self.interactor_axial.Start()
