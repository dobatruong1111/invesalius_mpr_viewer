import vtk
from pubsub import pub as Publisher
from typing import List

from slice_ import Slice
from converters import to_vtk

class VolumeViewer:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.slice_plane = None
        self.pointer_actor = None

        render_window = vtk.vtkRenderWindow()
        render_window.SetWindowName("Volume")
        render_window.SetSize(350, 350)
        render_window.SetPosition(1050, 0)
        # Turn off warning
        render_window.GlobalWarningDisplayOff()

        self.renderer = vtk.vtkRenderer()
        render_window.AddRenderer(self.renderer)

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(render_window)
        picker = vtk.vtkPointPicker()
        self.interactor.SetPicker(picker)
        self.SetInteractor()

        self.__bind_events()

    def __bind_events(self) -> None:
        Publisher.subscribe(self.LoadVolume, "Load volume")
        Publisher.subscribe(self.UpdateSlice3D, "Update slice 3d")
        Publisher.subscribe(self.UpdateRender, "Update volume")

    def UpdateRender(self) -> None:
        self.interactor.Render()

    def SetWidgetInteractor(self, widget: vtk.vtk3DWidget) -> None:
        widget.SetInteractor(self.interactor)

    def LoadSlicePlane(self) -> None:
        self.slice_plane = SlicePlane()

    def SetInteractor(self, style=None) -> None:
        if style is None:
            style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)

    def LoadImage(self) -> None:
        slice_data = Slice()
        n_array = slice_data.matrix
        spacing = slice_data.spacing
        image = to_vtk(n_array, spacing)
        self.image = image
    
    def LoadVolume(self) -> None:
        self.LoadImage()
        image = self.image

        if self.mode == "GPU":
            volume_mapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
            volume_mapper.SetInputData(image)
            volume_mapper.AutoAdjustSampleDistancesOff()
            volume_mapper.LockSampleDistanceToInputSpacingOn()
        else:
            volume_mapper = vtk.vtkFixedPointVolumeRayCastMapper()
            volume_mapper.SetInputData(image)
            volume_mapper.SetAutoAdjustSampleDistances(True)
            volume_mapper.SetLockSampleDistanceToInputSpacing(False)
            volume_mapper.SetImageSampleDistance(1.0)
            spacing = image.GetSpacing()
            sampleDistance = (spacing[0] + spacing[1] + spacing[2])/6
            volume_mapper.SetSampleDistance(sampleDistance)
            volume_mapper.SetInteractiveSampleDistance(sampleDistance)

        volume_properties = vtk.vtkVolumeProperty()
        volume_properties.SetInterpolationTypeToLinear()
        volume_properties.ShadeOn()
        volume_properties.SetAmbient(0.15)
        volume_properties.SetDiffuse(0.9)
        volume_properties.SetSpecular(0.3)
        volume_properties.SetSpecularPower(15)

        scalar_color = vtk.vtkColorTransferFunction()
        scalar_color.AddRGBPoint(-3024, 0, 0, 0)
        scalar_color.AddRGBPoint(143.556, 0.615686, 0.356863, 0.184314)
        scalar_color.AddRGBPoint(166.222, 0.882353, 0.603922, 0.290196)
        scalar_color.AddRGBPoint(214.389, 1, 1, 1)
        scalar_color.AddRGBPoint(419.736, 1, 0.937033, 0.954531)
        scalar_color.AddRGBPoint(3071, 0.827451, 0.658824, 1)
        volume_properties.SetColor(scalar_color)

        scalar_opacity = vtk.vtkPiecewiseFunction()
        scalar_opacity.AddPoint(-3024, 0)
        scalar_opacity.AddPoint(143.556, 0)
        scalar_opacity.AddPoint(166.222, 0.686275)
        scalar_opacity.AddPoint(214.389, 0.696078)
        scalar_opacity.AddPoint(419.736, 0.833333)
        scalar_opacity.AddPoint(3071, 0.803922)
        volume_properties.SetScalarOpacity(scalar_opacity)

        gradient_opacity = vtk.vtkPiecewiseFunction()
        gradient_opacity.AddPoint(0, 1)
        gradient_opacity.AddPoint(255, 1)
        volume_properties.SetGradientOpacity(gradient_opacity)
        self.volume_properties = volume_properties

        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_properties)
        self.volume = volume

        self.renderer.AddVolume(volume)
        self.renderer.ResetCamera()

        # Load slice plane
        self.LoadSlicePlane()
        self.slice_plane.UpdateAllSlice()
        self.SetWidgetInteractor(self.slice_plane.plane_z)
        self.SetWidgetInteractor(self.slice_plane.plane_y)
        self.SetWidgetInteractor(self.slice_plane.plane_x)
        self.slice_plane.Disable()

        self.interactor.GetRenderWindow().Render()

    def UpdateSlice3D(self, orientations: List) -> None:
        for orientation in orientations:
            self.slice_plane.ChangeSlice(orientation)

class SlicePlane:
    def __init__(self) -> None:
        self.Create()

    def Create(self) -> None:
        # 3D widget for reslicing image data.
        plane_x = self.plane_x = vtk.vtkImagePlaneWidget()
        plane_x.InteractionOff()
        # Convenience method sets the plane orientation normal to the x, y, or z axes.
        plane_x.SetPlaneOrientationToXAxes()
        # Control the visibility of the actual texture mapped reformatted plane.
        plane_x.TextureVisibilityOn()
        # Set action associated to buttons.
        plane_x.SetLeftButtonAction(0)
        plane_x.SetRightButtonAction(0)
        plane_x.SetMiddleButtonAction(0)
        # Set the properties of the cross-hair cursor.
        plane_x.GetCursorProperty().SetOpacity(0)
        plane_x.GetPlaneProperty().SetColor(0, 1, 0)
        plane_x.GetSelectedPlaneProperty().SetColor(0, 1, 0)

        plane_y = self.plane_y = vtk.vtkImagePlaneWidget()
        # Enable/disable text display of window-level, image coordinates and scalar values in a render window.
        plane_y.DisplayTextOff()
        plane_y.SetPlaneOrientationToYAxes()
        plane_y.TextureVisibilityOn()
        plane_y.SetLeftButtonAction(0)
        plane_y.SetRightButtonAction(0)
        plane_y.SetMiddleButtonAction(0)
        plane_y.GetCursorProperty().SetOpacity(0)
        plane_y.GetPlaneProperty().SetColor(0, 0, 1)
        plane_y.GetSelectedPlaneProperty().SetColor(0, 0, 1)

        plane_z = self.plane_z = vtk.vtkImagePlaneWidget()
        plane_z.InteractionOff()
        plane_z.SetPlaneOrientationToZAxes()
        plane_z.TextureVisibilityOn()
        plane_z.SetLeftButtonAction(0)
        plane_z.SetRightButtonAction(0)
        plane_z.SetMiddleButtonAction(0)
        plane_z.GetCursorProperty().SetOpacity(0)
        plane_z.GetPlaneProperty().SetColor(1, 0, 0)
        plane_z.GetSelectedPlaneProperty().SetColor(1, 0, 0)

    def Enable(self, plane_label=None) -> None:
        if plane_label is not None:
            if plane_label == "AXIAL":
                self.plane_z.On()
            elif plane_label == "CORONAL":
                self.plane_y.On()
            else:
                self.plane_x.On()
        else:
            self.plane_z.On()
            self.plane_y.On()
            self.plane_x.On()

    def Disable(self, plane_label=None) -> None:
        if plane_label is not None:
            if plane_label == "AXIAL":
                self.plane_z.Off()
            elif plane_label == "CORONAL":
                self.plane_y.Off()
            else:
                self.plane_x.Off()
        else:
            self.plane_z.Off()
            self.plane_y.Off()
            self.plane_x.Off()

    def DeletePlanes(self) -> None:
        del self.plane_z
        del self.plane_y
        del self.plane_x

    def UpdateAllSlice(self) -> None:
        slice = Slice()
        slice.UpdateSlice3D(self.plane_z, "AXIAL")
        slice.UpdateSlice3D(self.plane_y, "CORONAL")
        slice.UpdateSlice3D(self.plane_x, "SAGITAL")

    def ChangeSlice(self, orientation: str) -> None:
        slice = Slice()
        if orientation == "AXIAL" and self.plane_z.GetEnabled():
            slice.UpdateSlice3D(self.plane_z, orientation)
        elif orientation == "CORONAL" and self.plane_y.GetEnabled():
            slice.UpdateSlice3D(self.plane_y, orientation)
        elif orientation == "SAGITAL" and self.plane_x.GetEnabled():
            slice.UpdateSlice3D(self.plane_x, orientation)
