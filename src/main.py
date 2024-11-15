import vtk
from vtkmodules.util.numpy_support import vtk_to_numpy
from pubsub import pub as Publisher
from argparse import ArgumentParser

from slice_ import Slice
from viewer_slice import SliceViewer
from viewer_volume import VolumeViewer
from viewer_endoscopy import EndoscopyViewer

def main():
    parser = ArgumentParser("App")
    parser.add_argument(
        "--mode",
        type=str,
        default="CPU",
    )
    args = parser.parse_args()
    mode = args.mode

    path = "D:/workingspace/dicom/220277460 Nguyen Thanh Dat"
    # path = "D:/workingspace/dicom/DICOM_NGUYEN VAN HUONG78T_CT_9210255004/1.2.392.200036.9123.100.11.12.700001708.2024010308030744.44/1.2.392.200036.9123.100.11.15114374081372786170424474122344997"
    # path = "D:/workingspace/viewer/be_project/viewer-core/server3d/src/data/2.25.273770070420816203849299146355226291780/1.2.840.113619.2.428.3.678656.566.1723853370.188.3/data"
    # path = "D:/workingspace/viewer/be_project/viewer-core/server3d/src/data/2.25.273770070420816203849299146355226291780/1.2.840.113619.2.428.3.678656.566.1723853370.188.3/data"
    # path = "D:/workingspace/viewer/be_project/viewer-core/server3d/src/data/1.2.840.113619.2.472.3.2831157761.80.1725840678.120/1.2.840.113619.2.472.3.2831157761.80.1725840678.176.6/data"
    dicomReader = vtk.vtkDICOMImageReader()
    dicomReader.SetDirectoryName(path)
    dicomReader.Update()
    imageData = dicomReader.GetOutput()

    slice = Slice()
    dimensions = imageData.GetDimensions()
    shape = dimensions[::-1]
    matrix = vtk_to_numpy(imageData.GetPointData().GetScalars()).reshape(shape)
    slice.matrix = matrix
    slice.spacing = imageData.GetSpacing()
    slice.center = imageData.GetCenter()
    
    sliceViewer = SliceViewer()
    volumeViewer = VolumeViewer(mode)
    # endoViewer = EndoscopyViewer()
    
    Publisher.sendMessage("Load mpr")
    Publisher.sendMessage("Load volume")
    Publisher.sendMessage("Start app")

if __name__ == "__main__":
    main()
