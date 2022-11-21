import desper
import pyglet
from pyglet.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA


@desper.event_handler('on_switch_in', 'on_switch_out', 'on_add')
class Sprite(pyglet.sprite.Sprite):
    """Specialized sprite for better integration into desper.

    In particular, it listens to some events in order to schedule
    animations correctly. See module :mod:`pyglet.sprite` to know
    more about sprites.

    This assumes that the default event workflow is being followed.
    That is: world dispatching is disabled after creation and
    enabled just when it is used as current world (i.e. with
    :func:`desper.switch`).
    """

    def __init__(self,
                 img, x=0, y=0, z=0,
                 blend_src=GL_SRC_ALPHA,
                 blend_dest=GL_ONE_MINUS_SRC_ALPHA,
                 batch=None,
                 group=None,
                 subpixel=False):
        super().__init__(img, x, y, z, blend_src, blend_dest, batch, group,
                         subpixel)
        # Pause at creation to prevent global clock from scheduling it
        if self._animation is not None:
            self.paused = True

    __init__.__doc__ = pyglet.sprite.Sprite.__init__.__doc__

    def on_add(self, entity, world: desper.World):
        """Start animation."""
        if self._animation is not None:
            self.paused = False

    def on_switch_in(self, world_from: desper.World, world_to: desper.World):
        """Start animation."""
        if self._animation is not None:
            self.paused = False

    def on_switch_out(self, world_from: desper.World, world_to: desper.World):
        """Stop animation."""
        if self._animation is not None:
            self.paused = True
