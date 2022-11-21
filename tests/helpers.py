import desper
import pyglet

import pytest


@pytest.fixture(scope='session')
def window():
    win = pyglet.window.Window()
    yield win
    win.close()


@desper.event_handler('on_update')
class OnUpdateComponent:
    frames = 0

    def on_update(self, dt):
        self.frames += 1


@desper.event_handler('on_update')
class OnUpdateQuitComponent:
    frame_skipped = False

    def on_update(self, dt):
        if not self.frame_skipped:
            self.frame_skipped = True
            return

        self.frame_skipped = False
        raise desper.Quit()


def populate_transformer(handle, world):
    world.add_processor(desper.OnUpdateProcessor())

    world.create_entity(OnUpdateComponent())


@desper.event_handler('on_key_press')
class OnKeyPressComponent:
    args_tuple = ()

    def on_key_press(self, *args):
        self.args_tuple = args
