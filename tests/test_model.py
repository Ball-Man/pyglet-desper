from context import pyglet_desper as pdesper

import os
import os.path as pt

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
