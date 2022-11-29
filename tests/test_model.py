from context import pyglet_desper as pdesper

import os
import os.path as pt
import typing
import json

import pytest
import pyglet

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
