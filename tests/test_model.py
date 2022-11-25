from context import pyglet_desper as pdesper

import pytest
import pyglet

from helpers import *       # NOQA


@pytest.fixture
def wav_filename():
    return get_filename('files', 'fake_project', 'media', 'yayuh.wav')


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
