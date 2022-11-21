from context import pyglet_desper as pdesper


import desper
import pytest

from helpers import *


@pytest.fixture
def loop():
    return pdesper.Loop()


@pytest.fixture
def populated_world_handle():
    handle = desper.WorldHandle()
    handle.transform_functions.append(populate_transformer)
    return handle


class TestLoop:

    def test_switch(self, loop):
        handle = desper.WorldHandle()
        loop.switch(handle)

        assert loop.current_world is handle()
        assert loop.current_world_handle is handle
        assert loop.current_world.dispatch_enabled

    def test_switch_clear(self, loop):
        handle1 = desper.WorldHandle()
        handle2 = desper.WorldHandle()
        loop.switch(handle1)
        world1 = handle1()

        # Test clear current
        loop.switch(handle2, clear_current=True)
        world1_new = handle1()
        assert world1 is not world1_new

        # Test clear next
        loop.switch(handle1, clear_next=True)
        assert loop.current_world is not world1_new

    def test_loop(self, populated_world_handle, loop, window):
        populated_world_handle().create_entity(OnUpdateQuitComponent())
        loop.switch(populated_world_handle)

        try:
            loop.loop()
        except desper.Quit:
            pass

    def test_connect_window_events(self, populated_world_handle, loop, window):
        loop.connect_window_events(window, 'on_key_press')

        handler = OnKeyPressComponent()
        populated_world_handle().create_entity(
            OnUpdateQuitComponent(), handler)

        loop.switch(populated_world_handle)

        event_args = 42, 42
        window.dispatch_event('on_key_press', *event_args)

        loop.start()

        assert handler.args_tuple == event_args

    def test_disconnect_window_events(self, populated_world_handle, loop,
                                      window):
        loop.connect_window_events(window, 'on_key_press')

        handler = OnKeyPressComponent()
        populated_world_handle().create_entity(
            OnUpdateQuitComponent(), handler)

        loop.switch(populated_world_handle)

        event_args = 42, 42

        loop.disconnect_window_events(window, 'on_key_press', 'on_draw')
        window.dispatch_event('on_key_press', *event_args)

        loop.start()

        assert not handler.args_tuple
