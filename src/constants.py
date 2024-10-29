# Mask threshold options

# proj = Project()
# THRESHOLD_RANGE = proj.threshold_modes[_("Bone")]
THRESHOLD_RANGE = [0, 3033]
THRESHOLD_PRESETS_INDEX = ("Bone")
THRESHOLD_HUE_RANGE = (0, 0.6667)
THRESHOLD_INVALUE = 5000
THRESHOLD_OUTVALUE = 0

# Slice orientation
AXIAL = 1
CORONAL = 2
SAGITAL = 3
VOLUME = 4
SURFACE = 5

AXIAL_STR = "AXIAL"
CORONAL_STR = "CORONAL"
SAGITAL_STR = "SAGITAL"

# Camera according to slice's orientation
AXIAL_SLICE_CAM_POSITION = {"AXIAL": (0, 0, 1), "CORONAL": (0, -1, 0), "SAGITAL": (1, 0, 0)}
AXIAL_SLICE_CAM_VIEW_UP = {"AXIAL": (0, 1, 0), "CORONAL": (0, 0, 1), "SAGITAL": (0, 0, 1)}

SAGITAL_SLICE_CAM_POSITION = {"AXIAL": (0, 0, 1), "CORONAL": (0, 1, 0), "SAGITAL": (-1, 0, 0)}
SAGITAL_SLICE_CAM_VIEW_UP = {"AXIAL": (0, -1, 0), "CORONAL": (0, 0, 1), "SAGITAL": (0, 0, 1)}

CORONAL_SLICE_CAM_POSITION = {"AXIAL": (0, 0, 1), "CORONAL": (0, 1, 0), "SAGITAL": (-1, 0, 0)}
CORONAL_SLICE_CAM_VIEW_UP = {"AXIAL": (0, -1, 0), "CORONAL": (0, 0, 1), "SAGITAL": (0, 0, 1)}

SLICE_POSITION = {
    AXIAL: [AXIAL_SLICE_CAM_VIEW_UP, AXIAL_SLICE_CAM_POSITION],
    CORONAL: [CORONAL_SLICE_CAM_VIEW_UP, CORONAL_SLICE_CAM_POSITION],
    SAGITAL: [SAGITAL_SLICE_CAM_VIEW_UP, SAGITAL_SLICE_CAM_POSITION],
}

# Colour representing each orientation
ORIENTATION_COLOUR = {
    "AXIAL": (1, 0, 0),
    "CORONAL": (0, 1, 0),
    "SAGITAL": (0, 0, 1),
}

# VTK text
TEXT_SIZE_SMALL = 11
TEXT_SIZE = 12
TEXT_SIZE_LARGE = 16
TEXT_SIZE_EXTRA_LARGE = 20
TEXT_SIZE_DISTANCE_DURING_NAVIGATION = 32
TEXT_COLOUR = (1, 1, 1)

(X, Y) = (0.03, 0.97)
(XZ, YZ) = (0.05, 0.93)
TEXT_POS_LEFT_UP = (X, Y)
# ------------------------------------------------------------------
TEXT_POS_LEFT_DOWN = (X, 1 - Y)  # SetVerticalJustificationToBottom

TEXT_POS_LEFT_DOWN_ZERO = (X, 1 - YZ)
# ------------------------------------------------------------------
TEXT_POS_RIGHT_UP = (1 - X, Y)  # SetJustificationToRight
# ------------------------------------------------------------------
TEXT_POS_RIGHT_DOWN = (1 - X, 1 - Y)  # SetVerticalJustificationToBottom &
# SetJustificationToRight
# ------------------------------------------------------------------
TEXT_POS_HCENTRE_DOWN = (0.5, 1 - Y)  # SetJustificationToCentered
# ChildrticalJustificationToBottom

TEXT_POS_HCENTRE_DOWN_ZERO = (0.5, 1 - YZ)
# ------------------------------------------------------------------
TEXT_POS_HCENTRE_UP = (0.5, Y)  # SetJustificationToCentered
# ------------------------------------------------------------------
TEXT_POS_VCENTRE_RIGHT = (1 - X, 0.5)  # SetVerticalJustificationToCentered
# SetJustificationToRight
TEXT_POS_VCENTRE_RIGHT_ZERO = (1 - XZ, 0.5)
# ------------------------------------------------------------------
TEXT_POS_VCENTRE_LEFT = (X, 0.5)  # SetVerticalJustificationToCentered
# ------------------------------------------------------------------

SLICE_STATE_CROSS = 3006
