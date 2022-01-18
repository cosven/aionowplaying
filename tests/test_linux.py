import sys
import pytest

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason=f'These tests should be skipped on {sys.platform}')

import asyncio
from dbus_next.aio import MessageBus

from aionowplaying import NowPlayingInterface, LoopStatus, PropertyName


class MyNowPlayingInterface(NowPlayingInterface):
    async def on_fullscreen(self, fullscreen: bool):
        assert isinstance(fullscreen, bool)

    async def on_raise(self):
        print('on_raise')

    async def on_quit(self):
        print('on_quit')

    async def on_loop_status(self, status: LoopStatus):
        assert isinstance(status, LoopStatus)
        assert status == LoopStatus.None_

    async def on_rate(self, rate: float):
        assert isinstance(rate, float)
        assert rate == 1.0

    async def on_shuffle(self, shuffle: bool):
        assert isinstance(shuffle, bool)
        assert not shuffle

    async def on_volume(self, volume: float):
        assert isinstance(volume, float)
        assert volume == 1.0

    async def on_next(self):
        print('on_next')

    async def on_previous(self):
        print('on_previous')

    async def on_play(self):
        print('on_play')

    async def on_play_pause(self):
        print('on_play_pause')

    async def on_stop(self):
        print('on_stop')

    async def on_seek(self, offset: int):
        assert isinstance(offset, int)
        assert offset == 0


@pytest.yield_fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def interface():
    it = MyNowPlayingInterface('TestNowPlayingPlayer')
    assert it is not None
    it.set_property(PropertyName.Identity, 'TestNowPlayingPlayer')
    it.set_property(PropertyName.DesktopEntry, 'test-now-playing')
    it.set_property(PropertyName.CanSetFullscreen, True)
    it.set_property(PropertyName.CanRaise, True)
    it.set_property(PropertyName.CanQuit, True)
    task = asyncio.ensure_future(it.start())
    yield task
    task.cancel()


@pytest.fixture(scope='session')
async def msgbus():
    await asyncio.sleep(2)
    bus = await MessageBus().connect()
    introspection = await bus.introspect('org.mpris.MediaPlayer2.TestNowPlayingPlayer', '/org/mpris/MediaPlayer2')
    yield bus, introspection
    bus.disconnect()


# noinspection PyUnresolvedReferences
class TestNowPlaying:
    async def test_properties(self, interface, msgbus):
        bus, introspection = msgbus
        proxy_object = bus.get_proxy_object('org.mpris.MediaPlayer2.TestNowPlayingPlayer', '/org/mpris/MediaPlayer2',
                                            introspection)
        iface = proxy_object.get_interface('org.mpris.MediaPlayer2')
        assert isinstance(await iface.get_can_quit(), bool)
        assert isinstance(await iface.get_can_raise(), bool)
        assert isinstance(await iface.get_can_set_fullscreen(), bool)
        assert isinstance(await iface.get_fullscreen(), bool)
        assert isinstance(await iface.get_desktop_entry(), str)
        assert isinstance(await iface.get_identity(), str)
        assert isinstance(await iface.get_supported_uri_schemes(), list)
        assert isinstance(await iface.get_supported_mime_types(), list)

    async def test_set_properties(self, interface, msgbus):
        bus, introspection = msgbus
        proxy_object = bus.get_proxy_object('org.mpris.MediaPlayer2.TestNowPlayingPlayer', '/org/mpris/MediaPlayer2',
                                            introspection)
        iface = proxy_object.get_interface('org.mpris.MediaPlayer2')
        await iface.set_fullscreen(True)
        await asyncio.sleep(1)
        assert await iface.get_fullscreen() is True

    async def test_methods(self, interface, msgbus):
        bus, introspection = msgbus
        proxy_object = bus.get_proxy_object('org.mpris.MediaPlayer2.TestNowPlayingPlayer', '/org/mpris/MediaPlayer2',
                                            introspection)
        iface = proxy_object.get_interface('org.mpris.MediaPlayer2')
        await asyncio.sleep(1)
        await iface.call_raise()
        await iface.call_quit()