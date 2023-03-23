from functools import partial
from typing import Callable, Optional

from ophyd import Device
from ophyd.sim import make_fake_device

from dodal.devices.aperturescatterguard import AperturePositions, ApertureScatterguard
from dodal.devices.backlight import Backlight
from dodal.devices.DCM import DCM
from dodal.devices.detector import DetectorParams
from dodal.devices.eiger import EigerDetector
from dodal.devices.fast_grid_scan import FastGridScan
from dodal.devices.oav.oav_detector import OAV
from dodal.devices.s4_slit_gaps import S4SlitGaps
from dodal.devices.smargon import Smargon
from dodal.devices.synchrotron import Synchrotron
from dodal.devices.undulator import Undulator
from dodal.devices.zebra import Zebra
from dodal.utils import BeamlinePrefix, get_beamline_name

BL = get_beamline_name("s03")

ACTIVE_DEVICES: dict[str, Device] = {}


def device_instantiation(
    device: Callable,
    name: str,
    prefix: str,
    wait: bool,
    fake: bool,
    post_create: Optional[Callable],
) -> Device:
    active_device = ACTIVE_DEVICES.get(name)
    if active_device is None:
        if fake:
            device = make_fake_device(device)
        ACTIVE_DEVICES[name] = device(
            name=name, prefix=f"{BeamlinePrefix(BL).beamline_prefix}{prefix}"
        )
        if wait:
            ACTIVE_DEVICES[name].wait_for_connection()
        if post_create:
            post_create(ACTIVE_DEVICES[name])
        return ACTIVE_DEVICES[name]
    else:
        if post_create:
            post_create(active_device)
            return active_device


def dcm(wait_for_connection: bool = True, fake_with_ophyd_sim: bool = False):
    """Get the i03 DCM device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    return partial(
        device_instantiation,
        device=DCM,
        name="dcm",
        prefix="",
        wait=wait_for_connection,
        fake=fake_with_ophyd_sim,
    )


def aperture_scatterguard(
    wait_for_connection: bool = True,
    fake_with_ophyd_sim: bool = False,
    aperture_positions: AperturePositions | None = None,
):
    """Get the i03 aperture and scatterguard device, instantiate it if it hasn't already
    been. If this is called when already instantiated, it will return the existing
    object. If aperture_positions is specified, it will update them.
    """

    def load_positions(a_s: ApertureScatterguard):
        a_s.load_aperture_positions(aperture_positions)

    return partial(
        device_instantiation,
        device=ApertureScatterguard,
        name="aperture_scatterguard",
        prefix="",
        wait=wait_for_connection,
        fake=fake_with_ophyd_sim,
        post_create=load_positions,
    )


# def aperture_scatterguard(
#    aperture_positions: AperturePositions | None = None,
#    wait_for_connection: bool = True,
#    fake_with_ophyd_sim: bool = False,
# ) -> ApertureScatterguard:
#    """Get the i03 aperture and scatterguard device, instantiate it if it hasn't already
#    been. If this is called when already instantiated, it will return the existing
#    object. If aperture_positions is specified, it will update them.
#    """
#    aperture_scatterguard: ApertureScatterguard = ACTIVE_DEVICES.get(
#        "aperture_scatterguard"
#    )
#    if aperture_scatterguard is None:
#        ACTIVE_DEVICES["aperture_scatterguard"] = ApertureScatterguard(
#            name="ApertureScatterguard",
#            prefix=f"{BeamlinePrefix(BL).beamline_prefix}",
#        )
#        if aperture_positions is not None:
#            ACTIVE_DEVICES["aperture_scatterguard"].load_aperture_positions(
#                aperture_positions
#            )
#        if wait_for_connection:
#            ACTIVE_DEVICES["aperture_scatterguard"].wait_for_connection()
#        return ACTIVE_DEVICES["aperture_scatterguard"]
#    else:
#        if aperture_positions is not None:
#            aperture_scatterguard.load_aperture_positions(aperture_positions)
#        return aperture_scatterguard


def backlight(wait_for_connection: bool = True) -> Backlight:
    """Get the i03 backlight device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    backlight = ACTIVE_DEVICES.get("backlight")
    if backlight is None:
        ACTIVE_DEVICES["backlight"] = Backlight(
            name="Backlight", prefix=f"{BeamlinePrefix(BL).beamline_prefix}-EA-BL-01:"
        )
        if wait_for_connection:
            ACTIVE_DEVICES["backlight"].wait_for_connection()
        return ACTIVE_DEVICES["backlight"]
    else:
        return backlight


# def dcm(wait_for_connection: bool = True) -> DCM:
#     """Get the i03 DCM device, instantiate it if it hasn't already been.
#     If this is called when already instantiated, it will return the existing object.
#     """
#     dcm = ACTIVE_DEVICES.get("dcm")
#     if dcm is None:
#         ACTIVE_DEVICES["dcm"] = DCM(
#             name="dcm", prefix=f"{BeamlinePrefix(BL).beamline_prefix}"
#         )
#         if wait_for_connection:
#             ACTIVE_DEVICES["dcm"].wait_for_connection()
#         return ACTIVE_DEVICES["dcm"]
#     else:
#         return dcm
#


def eiger(
    params: DetectorParams | None = None,
    wait_for_connection: bool = True,
) -> EigerDetector:
    """Get the i03 Eiger device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    If called with params, will update those params to the Eiger object.
    """
    eiger: EigerDetector = ACTIVE_DEVICES.get("eiger")
    if eiger is None:
        if params is not None:
            ACTIVE_DEVICES["eiger"] = EigerDetector.with_params(
                params,
                name="EigerDetector",
                prefix=f"{BeamlinePrefix(BL).beamline_prefix}-EA-EIGER-01:",
            )
        else:
            ACTIVE_DEVICES["eiger"] = EigerDetector(
                name="EigerDetector",
                prefix=f"{BeamlinePrefix(BL).beamline_prefix}-EA-EIGER-01:",
            )
        if wait_for_connection:
            # Eiger cannot currently be waited on, see #166
            # ACTIVE_DEVICES["eiger"].wait_for_connection()
            pass
        return ACTIVE_DEVICES["eiger"]
    else:
        if params is not None:
            eiger.set_detector_parameters(params)
        return eiger


def fast_grid_scan(wait_for_connection: bool = True) -> FastGridScan:
    """Get the i03 fast_grid_scan device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    fast_grid_scan = ACTIVE_DEVICES.get("fast_grid_scan")
    if fast_grid_scan is None:
        ACTIVE_DEVICES["fast_grid_scan"] = FastGridScan(
            name="fast_grid_scan",
            prefix=f"{BeamlinePrefix(BL).beamline_prefix}-MO-SGON-01:FGS:",
        )
        if wait_for_connection:
            ACTIVE_DEVICES["fast_grid_scan"].wait_for_connection()
        return ACTIVE_DEVICES["fast_grid_scan"]
    else:
        return fast_grid_scan


def oav(wait_for_connection: bool = True) -> OAV:
    """Get the i03 OAV device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    oav = ACTIVE_DEVICES.get("oav")
    if oav is None:
        ACTIVE_DEVICES["oav"] = OAV(
            name="OAV", prefix=f"{BeamlinePrefix(BL).beamline_prefix}"
        )
        if wait_for_connection:
            ACTIVE_DEVICES["oav"].wait_for_connection()
        return ACTIVE_DEVICES["oav"]
    else:
        return oav


def smargon(wait_for_connection: bool = True) -> Smargon:
    """Get the i03 Smargon device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    smargon = ACTIVE_DEVICES.get("smargon")
    if smargon is None:
        ACTIVE_DEVICES["smargon"] = Smargon(
            name="smargon", prefix=f"{BeamlinePrefix(BL).beamline_prefix}"
        )
        if wait_for_connection:
            ACTIVE_DEVICES["smargon"].wait_for_connection()
        return ACTIVE_DEVICES["smargon"]
    else:
        return smargon


def s4_slit_gaps(wait_for_connection: bool = True) -> S4SlitGaps:
    """Get the i03 s4_slit_gaps device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    s4_slit_gaps = ACTIVE_DEVICES.get("s4_slit_gaps")
    if s4_slit_gaps is None:
        ACTIVE_DEVICES["s4_slit_gaps"] = S4SlitGaps(
            name="s4_slit_gaps",
            prefix=f"{BeamlinePrefix(BL).beamline_prefix}-AL-SLITS-04:",
        )
        if wait_for_connection:
            ACTIVE_DEVICES["s4_slit_gaps"].wait_for_connection()
        return ACTIVE_DEVICES["s4_slit_gaps"]
    else:
        return s4_slit_gaps


def synchrotron(wait_for_connection: bool = True) -> Synchrotron:
    """Get the i03 synchrotron device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    synchrotron = ACTIVE_DEVICES.get("synchrotron")
    if synchrotron is None:
        ACTIVE_DEVICES["synchrotron"] = Synchrotron(name="synchrotron")
        if wait_for_connection:
            ACTIVE_DEVICES["synchrotron"].wait_for_connection()
        return ACTIVE_DEVICES["synchrotron"]
    else:
        return synchrotron


def undulator(wait_for_connection: bool = True) -> Undulator:
    """Get the i03 undulator device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    undulator = ACTIVE_DEVICES.get("undulator")
    if undulator is None:
        ACTIVE_DEVICES["undulator"] = Undulator(
            name="undulator",
            prefix=f"SR{BeamlinePrefix(BL).beamline_prefix[2:]}-MO-SERVC-01:",
        )
        if wait_for_connection:
            ACTIVE_DEVICES["undulator"].wait_for_connection()
        return ACTIVE_DEVICES["undulator"]
    else:
        return undulator


def zebra(wait_for_connection: bool = True) -> Zebra:
    """Get the i03 zebra device, instantiate it if it hasn't already been.
    If this is called when already instantiated, it will return the existing object.
    """
    zebra = ACTIVE_DEVICES.get("zebra")
    if zebra is None:
        ACTIVE_DEVICES["zebra"] = Zebra(
            name="zebra", prefix=f"{BeamlinePrefix(BL).beamline_prefix}-EA-ZEBRA-01:"
        )
        if wait_for_connection:
            ACTIVE_DEVICES["zebra"].wait_for_connection()
        return ACTIVE_DEVICES["zebra"]
    else:
        return zebra
