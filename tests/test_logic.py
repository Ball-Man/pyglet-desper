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


class TestGraphicSync2D:

    def test_init(self):
        sync = pdesper.GraphicSync2D(Transformable)

        assert sync.component_type is Transformable
        assert isinstance(sync, desper.EventHandler)

    def test_on_add(self, world):
        sync = pdesper.GraphicSync2D(Transformable)
        transform = desper.Transform2D()
        entity = world.create_entity(transform)

        sync.on_add(entity, world)

        assert transform.is_handler(sync)

    def test_on_remove(self, world):
        sync = pdesper.GraphicSync2D(Transformable)
        transform = desper.Transform2D()
        transformable = Transformable()
        entity = world.create_entity(transform, transformable, sync)

        sync.on_remove(entity, world)

        assert transformable.deleted == 1

    def test_on_position_change(self, world):
        sync = pdesper.GraphicSync2D(Transformable)
        transformable = Transformable()
        world.create_entity(desper.Transform2D(), transformable, sync)

        new_pos = desper.math.Vec2(1, 2)
        sync.on_position_change(new_pos)

        assert transformable.position is new_pos

    def test_on_rotation_change(self, world):
        sync = pdesper.GraphicSync2D(Transformable)
        transformable = Transformable()
        world.create_entity(desper.Transform2D(), transformable, sync)

        new_rot = 10
        sync.on_rotation_change(new_rot)

        assert transformable.rotation is new_rot

    def test_on_scale_change(self, world):
        sync = pdesper.GraphicSync2D(Transformable)
        transformable = Transformable()
        world.create_entity(desper.Transform2D(), transformable, sync)

        new_scale = desper.math.Vec2(1, 2)
        sync.on_scale_change(new_scale)

        assert (transformable.scale_x, transformable.scale_y) == new_scale


class TestSpriteSync:

    def test_init(self):
        sprite_sync = pdesper.SpriteSync()

        assert sprite_sync.component_type is pyglet.sprite.Sprite

    def test_on_add(self, image, world):
        sprite_sync = pdesper.SpriteSync()
        transform = desper.Transform2D((1, 2), 3, (4, 5))
        sprite = pyglet.sprite.Sprite(image)
        entity = world.create_entity(transform, sprite)

        sprite_sync.on_add(entity, world)

        assert (sprite.x, sprite.y) == transform.position
        assert sprite.rotation == transform.rotation
        assert (sprite.scale_x, sprite.scale_y) == transform.scale

    def test_on_position_change(self, image, world):
        sprite_sync = pdesper.SpriteSync()
        transform = desper.Transform2D()
        sprite = pyglet.sprite.Sprite(image)
        world.create_entity(transform, sprite, sprite_sync)

        new_pos = desper.math.Vec2(1, 1)
        sprite_sync.on_position_change(new_pos)

        assert sprite.position == (*new_pos, 0)


def test_arc_sync_component():
    sync_component = pdesper.arc_sync_component()

    assert isinstance(sync_component, pdesper.PositionRotationSync2D)
    assert sync_component.component_type is pyglet.shapes.Arc


# Group all unit tests for sync component functions
@pytest.mark.parametrize('component_function,reference_class,return_type', [
    # Shapes
    (pdesper.arc_sync_component, pyglet.shapes.Arc,
     pdesper.PositionRotationSync2D),
    (pdesper.circle_sync_component, pyglet.shapes.Circle,
     pdesper.PositionSync2D),
    (pdesper.ellipse_sync_component, pyglet.shapes.Ellipse,
     pdesper.PositionRotationSync2D),
    (pdesper.sector_sync_component, pyglet.shapes.Sector,
     pdesper.PositionRotationSync2D),
    (pdesper.line_sync_component, pyglet.shapes.Line,
     pdesper.PositionSync2D),
    (pdesper.rectangle_sync_component, pyglet.shapes.Rectangle,
     pdesper.PositionRotationSync2D),
    (pdesper.borderedrectangle_sync_component, pyglet.shapes.BorderedRectangle,
     pdesper.PositionRotationSync2D),
    (pdesper.triangle_sync_component, pyglet.shapes.Triangle,
     pdesper.PositionSync2D),
    (pdesper.star_sync_component, pyglet.shapes.Star,
     pdesper.PositionRotationSync2D),
    (pdesper.polygon_sync_component, pyglet.shapes.Polygon,
     pdesper.PositionRotationSync2D),

    # Text
    (pdesper.documentlabel_sync_component, pyglet.text.DocumentLabel,
     pdesper.PositionRotationSync2D),
    (pdesper.htmllabel_sync_component, pyglet.text.HTMLLabel,
     pdesper.PositionRotationSync2D),
    (pdesper.label_sync_component, pyglet.text.Label,
     pdesper.PositionRotationSync2D),
])
def test_sync_component_function(component_function, reference_class,
                                 return_type):
    sync_component = component_function()

    assert isinstance(sync_component, return_type)
    assert sync_component.component_type is reference_class
