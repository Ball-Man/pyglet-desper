"""Management of pyglet specific resources.

In particular, a set of specialized :class:`desper.Handle`s are
provided.
"""
import os.path as pt

import desper
import pyglet
from pyglet.media.codecs import MediaDecoder
from pyglet.image.codecs import ImageDecoder
from pyglet.image.atlas import TextureBin


default_texture_bin = pyglet.image.atlas.TextureBin()
"""Default texture atlas for :class:`ImageFileHandle`.

All images loaded with said handle class will by default be added
to an atlas in this bin, which will result in optimized batching
and hance rendering.

Before loading any images, it is possible to modify the bin's
:attr:`TextureBin.texture_width` and :attr:`TextureBin.texture_height`
in order to alter the size of generated atlases (defaults to 2048x2048).

Replacing the bin entirely with a new instance will sort no effect.
Specify a bin manually as parameter for :class:`ImageFileHandle`
in that case.
"""

_image_cache: dict[str, pyglet.image.AbstractImage] = {}
"""Cache for internal use.

Map absolute filenames to pyglet images. Mainly populated by
:class:`ImageFileHandle` to prevent reloading the same image multiple
times.
"""


class MediaFileHandle(desper.Handle[pyglet.media.Source]):
    """Specialized handle for pyglet's :class:`pyglet.media.Source`.

    Given a filename (path string), the :meth:`load` implementation
    tries to load given file as a :class:`pyglet.media.Source`
    object, i.e. an audio or video resource.

    Optionally, the source can be set to be streamed from disk
    through the ``streaming`` parameter (defaults to: not streamed).

    A decoder can be specified. Available
    decoders can be inspected through
    :func:`pyglet.media.codecs.get_codecs`.
    If not specified, the first available codec that supports the given
    file format will be used.
    """

    def __init__(self, filename: str, streaming=False,
                 decoder: MediaDecoder = None):
        self.filename = filename
        self.streaming = streaming
        self.decoder = decoder

    def load(self) -> pyglet.media.Source:
        """Load file with given parameters."""
        return pyglet.media.load(self.filename, streaming=self.streaming,
                                 decoder=self.decoder)


class ImageFileHandle(desper.Handle[pyglet.image.AbstractImage]):
    """Specialized handle for :class:`pyglet.image.AbstractImage`.

    Given a filename (path string), the :meth:`load` implementation
    tries to load given file as a :class:`pyglet.image.AbstractImage`
    object.

    By default images are cached and loaded into atlases
    (:class:`pyglet.image.atlas.TextureAtlas`). This behaviour can be
    altered through ``atlas``, ``border`` and ``texture_bin``
    parameters.

    Note that such atlas related parameters are ignored if the image
    is found in the local cache, as the cached value will be
    directly returned independently from the given parameters.

    A decoder can be specified. Available
    decoders can be inspected through
    :func:`pyglet.image.codecs.get_codecs`.
    If not specified, the first available codec that supports the given
    file format will be used.
    """

    def __init__(self, filename: str,
                 atlas=True, border: int = 1,
                 texture_bin: TextureBin = default_texture_bin,
                 decoder: ImageDecoder = None):
        self.filename = filename
        self.atlas = atlas
        self.border = border
        self.texture_bin = texture_bin
        self.decoder = decoder

    def load(self) -> pyglet.image.AbstractImage:
        """Load file with given parameters."""
        abs_filename = pt.abspath(self.filename)
        if abs_filename in _image_cache:
            return _image_cache[abs_filename]

        image = pyglet.image.load(abs_filename, decoder=self.decoder)

        if self.atlas:
            image = self.texture_bin.add(image)

        _image_cache[abs_filename] = image
        return image
