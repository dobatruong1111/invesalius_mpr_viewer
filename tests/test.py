import vtk

def main():
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(0.0, 0.0, 0.0)
    sphereSource.SetRadius(5.0)
    sphereSource.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1, 0, 0)

    renderer.AddActor(actor)

    cursor = vtk.vtkCursor3D()
    cursor.AllOff()
    cursor.AxesOn()
    cursor.SetModelBounds(-10, 10, -10, 10, -10, 10)
    cursor.Update()

    colorArray = vtk.vtkUnsignedCharArray()
    colorArray.SetNumberOfComponents(3)
    colorArray.SetNumberOfTuples(3)
    colorArray.SetTuple(0, [0, 0, 255])
    colorArray.SetTuple(1, [0, 255, 0])
    colorArray.SetTuple(2, [255, 0, 0])
    cursor.GetOutput().GetCellData().SetScalars(colorArray)

    cursorMapper = vtk.vtkPolyDataMapper()
    cursorMapper.SetInputConnection(cursor.GetOutputPort())
    cursorActor = vtk.vtkActor()
    cursorActor.SetMapper(cursorMapper)

    renderer.AddActor(cursorActor)
    renderer.ResetCamera()

    renderWindow.Render()
    renderWindowInteractor.Start()

if __name__ == "__main__":
    main()
