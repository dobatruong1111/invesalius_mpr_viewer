import vtk

import constants as const

class TextZero:
    def __init__(self) -> None:
        property = vtk.vtkTextProperty()
        property.SetFontSize(const.TEXT_SIZE_LARGE)
        property.SetFontFamilyToArial()
        property.BoldOn()
        property.ItalicOff()
        property.SetJustificationToLeft()
        property.SetVerticalJustificationToTop()
        property.SetColor(const.TEXT_COLOUR)
        self.property = property

        actor = vtk.vtkTextActor()
        actor.GetTextProperty().ShallowCopy(property)
        actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        actor.PickableOff()
        self.actor = actor

        self.layer = 99
        self.children = []
        self.text = ""
        self.position = (0, 0)
        self.bottom_pos = False
        self.right_pos = False

    def SetColour(self, colour: tuple) -> None:
        self.property.SetColor(colour)

    def SetSize(self, size: int) -> None:
        self.property.SetFontSize(size)
        self.actor.GetTextProperty().ShallowCopy(self.property)

    def SetValue(self, value: any) -> None:
        if isinstance(value, int) or isinstance(value, float):
            value = str(value)
        self.actor.SetInput(value)
        self.text = value

    def SetPosition(self, position: tuple) -> None:
        self.actor.GetPositionCoordinate().SetValue(position[0], position[1])
        self.position = position
