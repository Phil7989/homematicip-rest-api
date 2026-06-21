"""Tests for the FakeHcuServer – verifies that the fake hCU server behaves
like a real local HomematicIP Control Unit."""

import pytest

from homematicip.device import HomeControlUnit, PlugableSwitch
from homematicip.home import Home
from homematicip_demo.fake_hcu_server import FakeHcuServer
from homematicip_demo.helper import no_ssl_verification


# ---------------------------------------------------------------------------
# Server identity
# ---------------------------------------------------------------------------


def test_hcu_server_sgtin(fake_hcu):
    assert fake_hcu.aio_server.sgtin == FakeHcuServer.HCU_SGTIN


def test_hcu_getHost_returns_own_url(fake_hcu_home, fake_hcu):
    """The /getHost endpoint must point back at the hCU itself, not a cloud URL."""
    assert fake_hcu_home._connection_context.rest_url == fake_hcu.url


# ---------------------------------------------------------------------------
# Device recognition
# ---------------------------------------------------------------------------


def test_hcu_device_is_home_control_unit(fake_hcu_home: Home):
    with no_ssl_verification():
        d = fake_hcu_home.search_device_by_id(FakeHcuServer.HCU_SGTIN)
        assert isinstance(d, HomeControlUnit)
        assert d.dutyCycleLevel == 5.0
        assert d.accessPointPriority == 0
        assert d.signalBrightness == 1.0


def test_hcu_switch_device_is_present(fake_hcu_home: Home):
    with no_ssl_verification():
        d = fake_hcu_home.search_device_by_id("3014F711A0000SWITCH00001")
        assert isinstance(d, PlugableSwitch)
        assert d.label == "HCU-Switch"


# ---------------------------------------------------------------------------
# Home state
# ---------------------------------------------------------------------------


def test_hcu_home_is_connected(fake_hcu_home: Home):
    assert fake_hcu_home.connected is True


def test_hcu_home_id(fake_hcu_home: Home):
    assert fake_hcu_home.id == FakeHcuServer.HCU_HOME_ID


def test_hcu_home_timezone(fake_hcu_home: Home):
    assert fake_hcu_home.timeZoneId == "Europe/Berlin"


def test_hcu_home_duty_cycle(fake_hcu_home: Home):
    assert fake_hcu_home.dutyCycle == 5.0


# ---------------------------------------------------------------------------
# Switch control
# ---------------------------------------------------------------------------


def test_hcu_switch_state_on(fake_hcu_home: Home):
    with no_ssl_verification():
        switch = fake_hcu_home.search_device_by_id("3014F711A0000SWITCH00001")
        assert switch.on is False
        switch.set_switch_state(True)
        fake_hcu_home.get_current_state()
        switch = fake_hcu_home.search_device_by_id("3014F711A0000SWITCH00001")
        assert switch.on is True


def test_hcu_switch_label(fake_hcu_home: Home):
    with no_ssl_verification():
        switch = fake_hcu_home.search_device_by_id("3014F711A0000SWITCH00001")
        switch.set_label("Living Room Plug")
        fake_hcu_home.get_current_state()
        switch = fake_hcu_home.search_device_by_id("3014F711A0000SWITCH00001")
        assert switch.label == "Living Room Plug"


# ---------------------------------------------------------------------------
# Home commands
# ---------------------------------------------------------------------------


def test_hcu_set_location(fake_hcu_home: Home):
    with no_ssl_verification():
        fake_hcu_home.set_location("Munich", 48.137154, 11.576124)
        fake_hcu_home.get_current_state()
        assert fake_hcu_home.location.city == "Munich"
        assert fake_hcu_home.location.latitude == 48.137154
        assert fake_hcu_home.location.longitude == 11.576124


def test_hcu_set_timezone(fake_hcu_home: Home):
    with no_ssl_verification():
        fake_hcu_home.set_timezone("Europe/London")
        fake_hcu_home.get_current_state()
        assert fake_hcu_home.timeZoneId == "Europe/London"


def test_hcu_set_pin_and_clear(fake_hcu_home: Home):
    with no_ssl_verification():
        fake_hcu_home.set_pin("1234")
        assert fake_hcu_home._fake_cloud.aio_server.pin == "1234"
        fake_hcu_home.set_pin("", "1234")
        assert fake_hcu_home._fake_cloud.aio_server.pin is None


# ---------------------------------------------------------------------------
# Auth flow
# ---------------------------------------------------------------------------


def test_hcu_server_reset_clears_state(fake_hcu):
    """reset() must restore the initial device state."""
    fake_hcu.aio_server.data["devices"]["3014F711A0000SWITCH00001"]["label"] = "Changed"
    fake_hcu.aio_server.reset()
    label = fake_hcu.aio_server.data["devices"]["3014F711A0000SWITCH00001"]["label"]
    assert label == "HCU-Switch"
