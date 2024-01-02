import getpass
import socket
from functools import partial
from typing import Callable, Dict
from unittest.mock import MagicMock, patch

from pytest import mark, raises

from dodal.devices.zocalo import (
    ZocaloTrigger,
)

SIM_ZOCALO_ENV = "dev_artemis"

EXPECTED_DCID = 100
EXPECTED_RUN_START_MESSAGE = {"event": "start", "ispyb_dcid": EXPECTED_DCID}
EXPECTED_RUN_END_MESSAGE = {
    "event": "end",
    "ispyb_dcid": EXPECTED_DCID,
}


@patch("zocalo.configuration.from_file", autospec=True)
@patch("dodal.devices.zocalo.zocalo_interaction.lookup", autospec=True)
def _test_zocalo(
    func_testing: Callable, expected_params: dict, mock_transport_lookup, mock_from_file
):
    mock_zc = MagicMock()
    mock_from_file.return_value = mock_zc
    mock_transport = MagicMock()
    mock_transport_lookup.return_value = MagicMock()
    mock_transport_lookup.return_value.return_value = mock_transport

    func_testing(mock_transport)

    mock_zc.activate_environment.assert_called_once_with(SIM_ZOCALO_ENV)
    mock_transport.connect.assert_called_once()
    expected_message = {
        "recipes": ["mimas"],
        "parameters": expected_params,
    }

    expected_headers = {
        "zocalo.go.user": getpass.getuser(),
        "zocalo.go.host": socket.gethostname(),
    }
    mock_transport.send.assert_called_once_with(
        "processing_recipe", expected_message, headers=expected_headers
    )
    mock_transport.disconnect.assert_called_once()


def normally(function_to_run, mock_transport):
    function_to_run()


def with_exception(function_to_run, mock_transport):
    mock_transport.send.side_effect = Exception()

    with raises(Exception):
        function_to_run()


zc = ZocaloTrigger(environment=SIM_ZOCALO_ENV)


@mark.parametrize(
    "function_to_test,function_wrapper,expected_message",
    [
        (zc.run_start, normally, EXPECTED_RUN_START_MESSAGE),
        (
            zc.run_start,
            with_exception,
            EXPECTED_RUN_START_MESSAGE,
        ),
        (zc.run_end, normally, EXPECTED_RUN_END_MESSAGE),
        (zc.run_end, with_exception, EXPECTED_RUN_END_MESSAGE),
    ],
)
def test__run_start_and_end(
    function_to_test: Callable, function_wrapper: Callable, expected_message: Dict
):
    """
    Args:
        function_to_test (Callable): The function to test e.g. start/stop zocalo
        function_wrapper (Callable): A wrapper around the function, used to test for expected exceptions
        expected_message (Dict): The expected dictionary sent to zocalo
    """
    function_to_run = partial(function_to_test, EXPECTED_DCID)
    function_to_run = partial(function_wrapper, function_to_run)
    _test_zocalo(function_to_run, expected_message)
