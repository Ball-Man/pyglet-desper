from context import pyglet_desper as pdesper

import pyglet
import pytest

from helpers import *           # NOQA


@pytest.fixture
def image():
    return pyglet.image.SolidColorImagePattern(
        (255, 0, 0, 255)).create_image(100, 100)


@pytest.fixture
def animation(image):
    return pyglet.image.Animation([
        pyglet.image.AnimationFrame(image, 1),
    ])


@pytest.fixture
def world():
    return desper.World()


class TestSprite:

    def test_on_add(self, window, animation):
        sprite = pdesper.Sprite(animation)
        sprite.on_add(None, None)
        assert not sprite.paused

    def test_on_switch_in(self, window, animation):
        sprite = pdesper.Sprite(animation)
        sprite.on_switch_in(None, None)
        assert not sprite.paused

    def test_on_switch_out(self, window, animation):
        sprite = pdesper.Sprite(animation)
        sprite.on_switch_out(None, None)
        assert sprite.paused


class TestAdvancedSprite:

    def test_on_add(self, window, animation):
        sprite = pdesper.AdvancedSprite(animation)
        sprite.on_add(None, None)
        assert not sprite.paused

    def test_on_switch_in(self, window, animation):
        sprite = pdesper.AdvancedSprite(animation)
        sprite.on_switch_in(None, None)
        assert not sprite.paused

    def test_on_switch_out(self, window, animation):
        sprite = pdesper.AdvancedSprite(animation)
        sprite.on_switch_out(None, None)
        assert sprite.paused


class TestCamera:

    def test_init_default(self, window):
        batch = pyglet.graphics.Batch()
        camera = pdesper.Camera(batch)

        assert camera.batch is batch
        assert camera.window is window
        assert camera.viewport == (0, 0, window.width, window.height)

    def test_init(self, window):
        different_window = pyglet.window.Window()
        batch = pyglet.graphics.Batch()
        camera = pdesper.Camera(batch, desper.math.Mat4(),
                                desper.math.Vec4(), different_window)

        assert camera.batch is batch
        assert camera.window is different_window
        assert camera.viewport == desper.math.Vec4()

        different_window.close()


class TestCameraProcessor:

    def test_init_default(self, window):
        print(pyglet.app.windows)
        processor = pdesper.CameraProcessor()

        assert processor.window is window

    def test_inis(self, window):
        different_window = pyglet.window.Window()

        processor = pdesper.CameraProcessor(different_window)

        assert processor.window is different_window


class TestCameraTransform2D:

    def test_on_add(self, world):
        batch = pyglet.graphics.Batch()
        camera = pdesper.Camera(batch)
        transform = desper.Transform2D()
        camera_transform = pdesper.CameraTransform2D()

        world.create_entity(transform, camera, camera_transform)

        assert transform.is_handler(camera_transform)

    def test_get_view_matrix(self):
        camera_transform = pdesper.CameraTransform2D()
        assert isinstance(camera_transform.get_view_matrix(), desper.math.Mat4)
