from context import pyglet_desper as pdesper

import inspect
import os
import os.path as pt
import json

import pytest
import pyglet
from pyglet.graphics import Batch

from helpers import *       # NOQA

pyglet.resource.path = [pt.abspath(os.curdir).replace(os.sep, '/')]
pyglet.resource.reindex()


@pytest.fixture
def wav_filename():
    return get_filename('files', 'fake_project', 'media', 'yayuh.wav')


@pytest.fixture
def png_filename():
    return get_filename('files', 'fake_project', 'image', 'logo.png')


@pytest.fixture
def png_image(png_filename):
    return pyglet.image.load(png_filename)


@pytest.fixture
def animation_sheet_filename():
    return get_filename('files', 'fake_project', 'image',
                        'animation1.png')


@pytest.fixture
def animation_sheet(animation_sheet_filename):
    return pyglet.image.load(animation_sheet_filename)


@pytest.fixture
def animation_meta_filename():
    return get_filename('files', 'fake_project', 'image',
                        'animation1.json')


@pytest.fixture
def animation_meta(animation_meta_filename):
    with open(animation_meta_filename) as fin:
        return json.load(fin)


@pytest.fixture
def gif_filename():
    return get_filename('files', 'fake_project', 'image', 'muybridge.gif')


@pytest.fixture
def font_filename():
    return get_filename('files', 'fake_project', 'font', 'SillySet.ttf')


@pytest.fixture
def texture_bin():
    return pyglet.image.atlas.TextureBin()


@pytest.fixture
def clear_cache():
    yield
    pdesper.clear_image_cache()


def test_clear_image_cache(png_filename):
    pdesper.model._image_cache[png_filename] = None

    pdesper.clear_image_cache()

    assert png_filename not in pdesper.model._image_cache


class TestMediaFileHandle:

    def test_init(self, wav_filename):
        handle = pdesper.MediaFileHandle(wav_filename, True, None)
        assert handle.filename is wav_filename
        assert handle.streaming
        assert handle.decoder is None

    def test_load(self, wav_filename):
        handle = pdesper.MediaFileHandle(wav_filename)
        source = handle.load()

        assert isinstance(source, pyglet.media.Source)


class TestImageFileHandle:

    def test_init(self, png_filename, texture_bin):
        handle = pdesper.ImageFileHandle(png_filename, False, 10, texture_bin,
                                         None)

        assert handle.filename is png_filename
        assert not handle.atlas
        assert handle.border == 10
        assert handle.texture_bin is texture_bin
        assert handle.decoder is None

    def test_load(self, png_filename, texture_bin, clear_cache):
        handle = pdesper.ImageFileHandle(png_filename, texture_bin=texture_bin)
        image = handle.load()

        assert isinstance(image, pyglet.image.AbstractImage)
        assert pt.abspath(png_filename) in pdesper.model._image_cache
        assert texture_bin.atlases

        # Test caching
        handle2 = pdesper.ImageFileHandle(
            png_filename, texture_bin=texture_bin)
        assert handle2() is image

    def test_load_no_atlas(self, png_filename, texture_bin, clear_cache):
        handle = pdesper.ImageFileHandle(png_filename, atlas=False,
                                         texture_bin=texture_bin)
        handle.load()

        assert not texture_bin.atlases


class TestParseSpritesheet():

    def test_defaults(self, png_image):
        result = pdesper.parse_spritesheet(png_image, {})

        assert result is png_image

    def test_single_frame(self, png_image):
        frame_region = {'x': 10, 'y': 10, 'w': 30, 'h': 30}
        meta = {'frames': [{'frame': frame_region}]}

        result = pdesper.parse_spritesheet(png_image, meta)

        assert isinstance(
            result,
            (pyglet.image.TextureRegion, pyglet.image.ImageDataRegion))

        assert result.width == frame_region['w']
        assert result.height == frame_region['h']

    def test_full(self, animation_sheet, animation_meta):
        # Try building an animation from an actual aseprite export
        animation = pdesper.parse_spritesheet(animation_sheet, animation_meta)

        assert isinstance(animation, pyglet.image.Animation)
        assert len(animation.frames) == len(animation_meta['frames'])

        origin_y = animation_meta['meta']['origin']['y']
        origin_x = animation_meta['meta']['origin']['x']

        for frame_meta, frame in zip(animation_meta['frames'],
                                     animation.frames):
            frame_region_meta = frame_meta['frame']
            assert frame_region_meta['w'] == frame.image.width
            assert frame_region_meta['h'] == frame.image.height
            assert frame_region_meta['x'] == frame.image.x
            assert frame_region_meta['y'] == frame.image.y

            assert frame_meta['duration'] == frame.duration

            # Ensure origin
            assert frame.image.anchor_x == origin_x
            assert frame.image.anchor_x == origin_y


def test_load_spritesheet(animation_meta_filename):
    animation = pdesper.load_spritesheet(animation_meta_filename)

    assert isinstance(animation, pyglet.image.Animation)


class TestRichImageFileHandle:

    def test_load_spritesheet(self, animation_meta_filename):
        handle = pdesper.RichImageFileHandle(animation_meta_filename)

        animation = handle.load()

        assert isinstance(animation, pyglet.image.Animation)

    def test_load_animation(self, gif_filename):
        handle = pdesper.RichImageFileHandle(gif_filename)

        animation = handle.load()

        assert isinstance(animation, pyglet.image.Animation)

    def test_load_image(self, png_filename):
        handle = pdesper.RichImageFileHandle(png_filename)

        image = handle.load()

        assert isinstance(image, pyglet.image.AbstractImage)


class TestFontFileHandle:

    def test_init(self, font_filename):
        handle = pdesper.FontFileHandle(font_filename)

        handle.load()

        assert pyglet.font.have_font('SillySet')


def test_default_processors_transformer():
    handle = desper.WorldHandle()
    world = handle()

    pdesper.default_processors_transformer(handle, world)

    assert world.get_processor(pdesper.CameraProcessor) is not None


def test_retrieve_batch(world, default_loop):
    batch = pdesper.retrieve_batch(world)
    assert world.get(Batch)[0][1] is batch

    # Test query with existing batch
    batch = pdesper.retrieve_batch(world)
    assert len(world.get(Batch)) == 1
    assert world.get(Batch)[0][1] is batch

    # Test on default loop
    handle = desper.WorldHandle()
    default_loop.switch(handle)

    batch = pdesper.retrieve_batch()

    assert handle().get(Batch)[0][1] is batch


class TestWantsGroupBatch:

    @pytest.mark.parametrize('order,factory', [
        (1, pyglet.graphics.Group)
    ])
    def test_init(self, order, factory):
        wants = pdesper.WantsGroupBatch(order, factory)

        assert wants.order is order
        assert wants.group_factory is factory

    @pytest.mark.parametrize('order,factory', [
        (1, pyglet.graphics.Group)
    ])
    def test_build_group(self, order, factory):
        wants = pdesper.WantsGroupBatch(order, factory)

        group = wants.build_group()
        assert group.order == order
        # Don't test for type, as the factory might be a simple function


def test_init_graphics_transformer(png_image):
    handle = desper.WorldHandle()
    world = handle()

    # Population
    sprite = pdesper.Sprite(png_image)
    sprite2 = pyglet.sprite.Sprite(png_image)
    # Shapes currently unsupported by the transformer
    # shape = pyglet.shapes.Circle(0, 0, 10)
    wants1 = pdesper.WantsGroupBatch(1)

    text = pyglet.text.Label()
    wants2 = pdesper.WantsGroupBatch()

    excluded_sprite = pdesper.Sprite(png_image)

    world.create_entity(sprite, sprite2, wants1)
    world.create_entity(text, wants2)
    world.create_entity(excluded_sprite)

    pdesper.init_graphics_transformer(handle, world)

    assert sprite.batch is sprite2.batch is text.batch
    assert sprite.batch is not excluded_sprite.batch
    assert sprite.group.order == sprite2.group.order == wants1.order
    assert text.group.order == wants2.order
    assert excluded_sprite.group is None

    assert not world.get(pdesper.WantsGroupBatch)


def test_world_from_file_handle():
    handle = pdesper.world_from_file_handle('...')

    assert isinstance(handle, desper.WorldFromFileHandle)

    for transform_function in desper.WorldFromFileHandle(
            '...').transform_functions:
        if not inspect.isfunction(transform_function):
            assert type(transform_function) in map(type,
                                                   handle.transform_functions)
        else:
            assert transform_function in handle.transform_functions

    assert pdesper.default_processors_transformer in handle.transform_functions
    assert pdesper.init_graphics_transformer in handle.transform_functions


def test_resource_populator():
    resource_map = desper.ResourceMap()
    pdesper.resource_populator(
        resource_map, get_filename('files', 'fake_project'))

    assert type(
        resource_map.get('font/SillySet.ttf')) is pdesper.FontFileHandle
    assert isinstance(resource_map['image/animation1.png'],
                      pyglet.image.AbstractImage)
    assert isinstance(resource_map['image/animation1.json'],
                      pyglet.image.Animation)
    assert isinstance(resource_map['image/muybridge.gif'],
                      pyglet.image.Animation)
    assert isinstance(resource_map['media/yayuh.wav'],
                      pyglet.media.StaticSource)
    assert isinstance(resource_map['media/streaming/yayuh.wav'],
                      pyglet.media.StreamingSource)
