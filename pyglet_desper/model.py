"""Management of pyglet specific resources.

In particular, a set of specialized :class:`desper.Handle`s are
provided.
"""
import os.path as pt
from typing import Union

import desper
import pyglet
from pyglet.image import Animation, AnimationFrame, AbstractImage
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


def clear_image_cache():
    """Clear module level image cache.

    Texture bins/atlases (e.g. :attr:`default_texture_bin`) will not
    get cleared. Based on the user's implementation manual
    intervention might be necessary.
    """
    _image_cache.clear()


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

        if (self.atlas
            and image.width + self.border <= self.texture_bin.texture_width
            and image.height + self.border
                <= self.texture_bin.texture_height):
            image = self.texture_bin.add(image)

        _image_cache[abs_filename] = image
        return image


def parse_spritesheet(sheet: pyglet.image.AbstractImage,
                      metadata: dict) -> Union[AbstractImage, Animation]:
    """Setup image or animation from a source image and a dictionary.

    The dictionary must be in the following format:::

        {
            "frames": [
                {
                    "frame": {"x": ..., "y": ..., "w": ..., "h": ...},
                    "duration": ...
                },
                ...
            ],

            "meta": {
                "origin": {"x": ..., "y": ...}
            }
        }

    Durations are in milliseconds.

    All fields are optional. In particular, here is how the decoder
    reacts to missing values:

    - If ``frames`` list is present and contains more than one frame,
        a :class:`pyglet.image.Animation` is built. Otherwise, a single
        :class:`pyglet.image.AbstractImage` is returned. If the
        ``frames`` list is missing or empty, the same input ``sheet`` is
        returned (eventually its origin will be changed).
    - ``origin`` is used to set the origin (i.e. ``anchor_x``
        and ``anchor_y``) of all animation frames.
        The user is then encouraged to have an animation where all
        frames have the same size (or deal with the consequences).
        if and only if the ``frames`` list is missing or empty, the
        origin is set directly to the input image ``sheet``, which is
        then returned.
    - ``x`` and ``y`` coordinates (for frames, or for origin) are
        assumed to be ``0`` if unspecified.
    - ``w`` and ``h`` coordinates are assumed to be respectively equal
        to :attr:`sheet.width` and :attr:`sheet.height` if unspecified.
    - ``duration`` values are set to one second (``1000`` ms) if
        unspecified.

    Be aware that according to ``pyglet``'s coordinate system, the
    origin of an image is considered to be the bottom-left corner (
    as opposed to common top-left based systems).

    The format is compatible with `Aseprite <https://aseprite.com/>`_'s
    export spritesheet option (in the output tab, json data must be
    enabled and set to ``array`` type, not ``hash``). Keep in mind that
    Aseprite uses a top-left origin in its format. The format is
    enriched with various other properties which are ignored by this
    function.
    """
    # Extract origin
    meta = metadata.get('meta', {})
    origin = meta.get('origin', {})
    origin_x = origin.get('x', 0)
    origin_y = origin.get('y', 0)

    frames: list[dict] = metadata.get('frames', [])

    # Empty list of frames, fallback to the input sheet
    if not frames:
        sheet.anchor_x = origin_x
        sheet.anchor_y = origin_y
        return sheet

    # Otherwise, start building frames
    regions = []
    durations = []
    for frame in frames:
        region = frame.get('frame', {})
        region_x = region.get('x', 0)
        region_y = region.get('y', 0)
        region_w = region.get('w', sheet.width)
        region_h = region.get('h', sheet.height)

        image_region = sheet.get_region(region_x, region_y, region_w,
                                        region_h)
        image_region.anchor_x = origin_x
        image_region.anchor_y = origin_y
        regions.append(image_region)

        durations.append(frame.get('duration', 1000))

    # If single frame, return the region itself
    if len(regions) == 1:
        return regions[0]

    # Finally, assemble frames and return animation
    return Animation([AnimationFrame(region, duration)
                      for region, duration in zip(regions, durations)])
