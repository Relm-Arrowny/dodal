from enum import Enum

from ophyd import Component, Device, EpicsMotor, EpicsSignalRO

UNDULATOR_DISCREPANCY_THRESHOLD_MM = 2e-3  # The acceptable difference, in mm, between the undulator gap and the DCM energy,
# when the latter is converted to mm using lookup tables


class UndulatorGapAccess(Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class Undulator(Device):
    gap_motor: EpicsMotor = Component(EpicsMotor, "BLGAPMTR")
    current_gap: EpicsSignalRO = Component(EpicsSignalRO, "CURRGAPD")
    gap_access: EpicsSignalRO = Component(EpicsSignalRO, "IDBLENA")
    gap_discrepancy_tolerance_mm: float = UNDULATOR_DISCREPANCY_THRESHOLD_MM

    def __init__(self, lookup_table_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_table_path = lookup_table_path
