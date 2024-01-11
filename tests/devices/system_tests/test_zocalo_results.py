import bluesky.plan_stubs as bps
import pytest
import pytest_asyncio
from bluesky.run_engine import RunEngine

from dodal.devices.zocalo import XrcResult, ZocaloResults, ZocaloTrigger

TEST_RESULT_LARGE: XrcResult = {
    "centre_of_mass": [1, 2, 3],
    "max_voxel": [1, 2, 3],
    "max_count": 105062,
    "n_voxels": 35,
    "total_count": 2387574,
    "bounding_box": [[2, 2, 2], [8, 8, 7]],
}


@pytest_asyncio.fixture
async def zocalo_device():
    zd = ZocaloResults("zocalo")
    await zd.connect()
    return zd


@pytest.mark.s03
@pytest.mark.asyncio
async def test_read_results_from_fake_zocalo(zocalo_device: ZocaloResults):
    zc = ZocaloTrigger("dev_artemis")
    zc.run_start(0)
    zc.run_end(0)
    zocalo_device.timeout_s = 5

    def plan():
        yield from bps.open_run()
        yield from bps.trigger_and_read([zocalo_device])
        yield from bps.close_run()

    RE = RunEngine()
    RE(plan())

    results = await zocalo_device.read()
    assert results["zocalo-results"]["value"][0] == TEST_RESULT_LARGE
