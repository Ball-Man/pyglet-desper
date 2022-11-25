"""Management of pyglet specific resources.

In particular, a set of specialized :class:`desper.Handle`s are
provided.
"""
import desper
import pyglet
from pyglet.media.codecs import MediaDecoder


class MediaFileHandle(desper.Handle[pyglet.media.Source]):
    """Specialized handle for pyglet's :class:`pyglet.media.Source`.

    Given a filename (path string), the :meth:`load` implementation
    tries to load given file as a :class:`pyglet.media.Source`
    object, i.e. an audio or video resource.

    Optionally, the source can be set to be streamed from disk
    through the ``streaming`` parameter (defaults to: not streamed).

    A decoder can be specified for actual audio decoding. Available
    decoders can be inspected through
    :func:`pyglet.media.codecs.get_codecs`.
    If not specified, the first available codec that supports the given
    file extension will be used.
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
