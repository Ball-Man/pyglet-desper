import os.path as pt

import desper
import pyglet

import pytest


def get_filename(*path: str) -> str:
    """Get a path with respect to tests folder.

    Use varargs instead of slashes.
    """
    return pt.join(pt.dirname(__file__), *path)


@pytest.fixture(scope='session')
def window():
    win = pyglet.window.Window()
    yield win
    win.close()


@pytest.fixture
def world():
    return desper.World()


@pytest.fixture
def default_loop():
    desper.default_loop = desper.SimpleLoop()
    return desper.default_loop


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


class Transformable:
    position = None
    rotation = None
    scale_x = None
    scale_y = None

    deleted = 0

    def update(self, position=None, rotation=None, scale_x=None, scale_y=None):
        if position is not None:
            self.position = position

        if rotation is not None:
            self.rotation = rotation

        if scale_x is not None:
            self.scale_x = scale_x

        if scale_y is not None:
            self.scale_y = scale_y

    def delete(self):
        self.deleted += 1
