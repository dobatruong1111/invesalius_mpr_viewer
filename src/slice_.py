import numpy as np
from numpy import ndarray
import vtk

import utils
import converters
from project import Project

class SliceBuffer:
    """
    This class is used as buffer that mantains the vtkImageData and numpy array
    from actual slices from each orientation.
    """
    def __init__(self) -> None:
        self.index = -1
        self.image = None
        self.mask = None
        self.vtk_image = None
        self.vtk_mask = None

    def discard_vtk_mask(self) -> None:
        self.vtk_mask = None

    def discard_vtk_image(self) -> None:
        self.vtk_image = None

    def discard_mask(self) -> None:
        self.mask = None

    def discard_image(self) -> None:
        self.image = None

    def discard_buffer(self) -> None:
        self.index = -1
        self.image = None
        self.mask = None
        self.vtk_image = None
        self.vtk_mask = None

class Slice(metaclass=utils.Singleton):
    def __init__(self) -> None:
        self.matrix = None
        self.spacing = (1.0, 1.0, 1.0)
        self.center = [0, 0, 0]
        self.opacity = 0.8

        self.buffer_slices = {
            "AXIAL": SliceBuffer(),
            "CORONAL": SliceBuffer(),
            "SAGITAL": SliceBuffer()
        }

    def do_ww_wl(self, image: vtk.vtkImageData) -> vtk.vtkImageData:
        project = Project()
        colorer = vtk.vtkImageMapToWindowLevelColors()
        colorer.SetInputData(image)
        colorer.SetWindow(project.window_width)
        colorer.SetLevel(project.window_level)
        colorer.SetOutputFormatToRGB()
        colorer.Update()
        return colorer.GetOutput()

    def get_image_slice(self, orientation: str, slice_number: int, number_slices=1) -> ndarray:
        dz, dy, dx = self.matrix.shape
        if self.buffer_slices[orientation].index == slice_number and self.buffer_slices[orientation].image is not None:
            n_image = self.buffer_slices[orientation].image
        else:
            if orientation == "AXIAL":
                tmp_array = np.array(self.matrix[slice_number : slice_number + number_slices])
                n_image = tmp_array.reshape(dy, dx)
            elif orientation == "CORONAL":
                tmp_array = np.array(self.matrix[:, slice_number : slice_number + number_slices, :])
                n_image = tmp_array.reshape(dz, dx)
            elif orientation == "SAGITAL":
                tmp_array = np.array(self.matrix[:, :, slice_number : slice_number + number_slices])
                n_image = tmp_array.reshape(dz, dy)
            self.buffer_slices[orientation].image = n_image
        return n_image

    def GetNumberOfSlices(self, orientation: str) -> int:
        shape = self.matrix.shape
        if orientation == "AXIAL":
            return shape[0]
        elif orientation == "CORONAL":
            return shape[1]
        elif orientation == "SAGITAL":
            return shape[2]
        
    def GetMaxSliceNumber(self, orientation: str) -> int:
        shape = self.matrix.shape
        if orientation == "AXIAL":
            return shape[0] - 1
        elif orientation == "CORONAL":
            return shape[1] - 1
        elif orientation == "SAGITAL":
            return shape[2] - 1

    def GetSlices(self, orientation: str, slice_number: int, number_slices: int) -> vtk.vtkImageData:
        if self.buffer_slices[orientation].index == slice_number:
            if self.buffer_slices[orientation].vtk_image:
                image = self.buffer_slices[orientation].vtk_image
            else:
                n_image = self.get_image_slice(orientation, slice_number, number_slices)
                image = converters.to_vtk(n_image, self.spacing, slice_number, orientation)
                ww_wl_image = self.do_ww_wl(image)
                image = ww_wl_image
            self.buffer_slices[orientation].vtk_image = image
        else:
            n_image = self.get_image_slice(orientation, slice_number, number_slices)
            image = converters.to_vtk(n_image, self.spacing, slice_number, orientation)
            ww_wl_image = self.do_ww_wl(image)
            image = ww_wl_image
            self.buffer_slices[orientation].vtk_image = image
            self.buffer_slices[orientation].index = slice_number
        return image
