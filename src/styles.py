import vtk
from typing import Tuple

import constants as const

class BaseImageInteractorStyle(vtk.vtkInteractorStyleImage):
    def __init__(self, viewer) -> None:
        self.viewer = viewer

        self.left_pressed = False
        self.middle_pressed = False
        self.right_pressed = False

        self.AddObserver("LeftButtonPressEvent", self.OnPressLeftButton)
        self.AddObserver("LeftButtonReleaseEvent", self.OnReleaseLeftButton)

        self.AddObserver("MiddleButtonPressEvent", self.OnMiddleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent", self.OnMiddleButtonReleaseEvent)

        self.AddObserver("RightButtonPressEvent", self.OnPressRightButton)
        self.AddObserver("RightButtonReleaseEvent", self.OnReleaseRightButton)

    def OnPressLeftButton(self, obj, event) -> None:
        self.left_pressed = True

    def OnReleaseLeftButton(self, obj, event) -> None:
        self.left_pressed = False

    def OnMiddleButtonPressEvent(self, obj, event) -> None:
        self.middle_pressed = True

    def OnMiddleButtonReleaseEvent(self, obj, event) -> None:
        self.middle_pressed = False

    def OnPressRightButton(self, obj, event) -> None:
        self.right_pressed = True

    def OnReleaseRightButton(self, obj, event) -> None:
        self.right_pressed = False

class DefaultInteractorStyle(BaseImageInteractorStyle):
    """
    Interactor style responsible for Default functionalities:
        - Zoom moving mouse with right button pressed.
        - Change the slices with the scroll.
    """
    def __init__(self, viewer) -> None:
        BaseImageInteractorStyle.__init__(self, viewer)

        self.viewer = viewer

        self.AddObserver("MouseMoveEvent", self.OnZoomRightMove)
        self.AddObserver("MouseWheelForwardEvent", self.OnScrollForward)
        self.AddObserver("MouseWheelBackwardEvent", self.OnScrollBackward)

        # Zoom using right button
        self.AddObserver("RightButtonPressEvent", self.OnZoomRightClick)
        self.AddObserver("RightButtonReleaseEvent", self.OnZoomRightRelease)

    def OnZoomRightMove(self, obj, event) -> None:
        if self.right_pressed:
            obj.Dolly()
            obj.OnRightButtonDown()
        elif self.middle_pressed:
            obj.Pan()
            obj.OnMiddleButtonDown()

    def OnScrollForward(self, obj, event) -> None:
        self.viewer.OnScrollForward()

    def OnScrollBackward(self, obj, event) -> None:
        self.viewer.OnScrollBackward()

    def OnZoomRightClick(self, obj, event) -> None:
        obj.StartDolly()

    def OnZoomRightRelease(self, obj, event) -> None:
        obj.OnRightButtonUp()
        self.right_pressed = False

# Test
class DefaultInteractorStyle_2(BaseImageInteractorStyle):
    """
    Interactor style responsible for Default functionalities:
        - Zoom moving mouse with right button pressed.
        - Change the slices with the scroll.
    """
    def __init__(self, viewer, orientation) -> None:
        BaseImageInteractorStyle.__init__(self, viewer)

        self.viewer = viewer
        self.orientation = orientation

        self.AddObserver("MouseMoveEvent", self.OnZoomRightMove)
        self.AddObserver("MouseWheelForwardEvent", self.OnScrollForward)
        self.AddObserver("MouseWheelBackwardEvent", self.OnScrollBackward)

        # Zoom using right button
        self.AddObserver("RightButtonPressEvent", self.OnZoomRightClick)
        self.AddObserver("RightButtonReleaseEvent", self.OnZoomRightRelease)

    def OnZoomRightMove(self, obj, event) -> None:
        if self.right_pressed:
            obj.Dolly()
            obj.OnRightButtonDown()
        elif self.middle_pressed:
            obj.Pan()
            obj.OnMiddleButtonDown()

    def OnScrollForward(self, obj, event) -> None:
        self.viewer.OnScrollForward(self.orientation)

    def OnScrollBackward(self, obj, event) -> None:
        self.viewer.OnScrollBackward(self.orientation)

    def OnZoomRightClick(self, obj, event) -> None:
        obj.StartDolly()

    def OnZoomRightRelease(self, obj, event) -> None:
        obj.OnRightButtonUp()
        self.right_pressed = False
# Test

class CrossInteractorStyle(DefaultInteractorStyle):
    """
    The style displays the cross in each slice and allows the user to move the cross in the slices by clicking 
    and dragging the mouse.
    """
    def __init__(self, viewer) -> None:
        DefaultInteractorStyle.__init__(self, viewer)

        self.viewer = viewer
        self.orientation = viewer.orientation
        self.slice_actor = viewer.slice_data.actor
        self.slice_data = viewer.slice_data

        self.picker = vtk.vtkWorldPointPicker()

        self.AddObserver("LeftButtonPressEvent", self.OnCrossMouseClick)
        self.AddObserver("LeftButtonReleaseEvent", self.OnReleaseLeftButton)

        self.AddObserver("MouseMoveEvent", self.OnCrossMove)

    def OnCrossMouseClick(self, obj, event) -> None:
        iren = obj.GetInteractor()
        self.ChangeCrossPosition(iren)

    def OnCrossMove(self, obj, event) -> None:
        # The user moved the mouse with left button pressed.
        if self.left_pressed:
            iren = obj.GetInteractor()
            self.ChangeCrossPosition(iren)

    def ChangeCrossPosition(self, iren: vtk.vtkRenderWindowInteractor) -> None:
        mouse_x, mouse_y = iren.GetEventPosition()
        x, y, z = self.viewer.get_coordinate_cursor(mouse_x, mouse_y, self.picker)
        
        self.viewer.UpdateSlicesPosition([x, y, z])

        # Update the position of the cross in other slices.
        self.viewer.SetCrossFocalPoint([x, y, z])
        self.viewer.UpdateRender()

# Test
class CrossInteractorStyle_2(DefaultInteractorStyle_2):
    """
    The style displays the cross in each slice and allows the user to move the cross in the slices by clicking 
    and dragging the mouse.
    """
    def __init__(self, viewer, orientation) -> None:
        DefaultInteractorStyle_2.__init__(self, viewer, orientation)

        self.viewer = viewer
        self.orientation = orientation

        self.picker = vtk.vtkWorldPointPicker()

        self.AddObserver("LeftButtonPressEvent", self.OnCrossMouseClick)
        self.AddObserver("LeftButtonReleaseEvent", self.OnReleaseLeftButton)

        self.AddObserver("MouseMoveEvent", self.OnCrossMove)

    def OnCrossMouseClick(self, obj, event) -> None:
        iren = obj.GetInteractor()
        self.ChangeCrossPosition(iren)

    def OnCrossMove(self, obj, event) -> None:
        # The user moved the mouse with left button pressed.
        if self.left_pressed:
            iren = obj.GetInteractor()
            self.ChangeCrossPosition(iren)

    def ChangeCrossPosition(self, iren: vtk.vtkRenderWindowInteractor) -> None:
        mouse_x, mouse_y = iren.GetEventPosition()
        x, y, z = self.viewer.get_coordinate_cursor(mouse_x, mouse_y, self.orientation, self.picker)
        
        self.viewer.UpdateSlicesPosition(self.orientation, [x, y, z])

        # Update the position of the cross in other slices.
        self.viewer.SetCrossFocalPoint([x, y, z])
        self.viewer.UpdateRender()

    def OnScrollBar(self) -> None:
        if self.orientation == "AXIAL":
            x, y, z = self.viewer.cross_axial.GetFocalPoint()
        elif self.orientation == "CORONAL":
            x, y, z = self.viewer.cross_coronal.GetFocalPoint()
        elif self.orientation == "SAGITAL":
            x, y, z = self.viewer.cross_sagital.GetFocalPoint()

        # self.viewer.UpdateSlicesPosition(self.orientation, [x, y, z])

        # Update the position of the cross in other slices.
        self.viewer.SetCrossFocalPoint([x, y, z])
        # self.viewer.UpdateRender()
# Test
