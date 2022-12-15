import math
from typing import Optional

import desper
import pyglet
from pyglet.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA

from .sync import *             # NOQA

ON_CAMERA_DRAW_EVENT_NAME = 'on_camera_draw'


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


@desper.event_handler('on_switch_in', 'on_switch_out', 'on_add')
class AdvancedSprite(pyglet.sprite.AdvancedSprite):
    """Specialized advanced sprite for better integration into desper.

    Being an advanced sprite, it is possible to specify its shader
    program at any time through the :attr:`program` attribute (see
    :class:`pyglet.sprite.AdvancedSprite`).

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
                 subpixel=False,
                 program=None):
        super().__init__(img, x, y, z, blend_src, blend_dest, batch, group,
                         subpixel, program)
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


@desper.event_handler(ON_CAMERA_DRAW_EVENT_NAME)
class Camera:
    """Render content of a :class:`pyglet.graphics.Batch`.

    Apply the given projection and viewport before rendering. If
    omitted, projection and viewport will be set as window defaults
    (from pyglet), that is:

    - orthogonal projection that maps to the window pixel size, with
        origin (0, 0) at the bottom-left corner
    - viewport equal to: ``0, 0, window.width, window.height``

    A projection matrix can be easily obtained through
    :meth:`desper.math.Mat4.orthogonal_projection` (2D) or through
    :meth:`desper.math.Mat4.perspective_projection` (3D).

    Viewport can be manually constructed and shall be a tuple in the
    form ``(x, y, width, height)`` (:class:`desper.math.Vec4` is
    supported).

    A :class:`pyglet.window.Window` can be specified and shall be taken
    as target of these transformations. In case of single window
    applications this is unnecessary and the main window will be
    automatically retrieven.
    """

    def __init__(self, batch: pyglet.graphics.Batch,
                 projection: Optional[desper.math.Mat4] = None,
                 viewport: Optional[tuple[int, int, int, int]] = None,
                 window: Optional[pyglet.window.Window] = None):
        self.batch = batch

        self.window: pyglet.window.Window = window
        if window is None:
            assert len(pyglet.app.windows), (
                'Unable to find an open window')
            self.window = next(iter(pyglet.app.windows))

        self.projection: desper.math.Mat4 = projection
        if projection is None:
            self.projection = self.window.projection

        self.viewport: tuple[int, int, int, int] = viewport
        if viewport is None:
            self.viewport = self.window.viewport

        # View transformation matrix
        self.view = desper.math.Mat4()

    def on_camera_draw(self):
        """Event handler: apply projection, view and viewport, render."""
        self.window.projection = self.projection
        self.window.viewport = self.viewport
        self.window.view = self.view

        self.batch.draw()


@desper.event_handler('on_draw')
class CameraProcessor(desper.Processor):
    """Render all cameras (:class:`Camera`).

    Despite being a :class:`desper.Processor` subclass, no action
    is done during :meth:`process`. The possibility to add it as a
    processor in a :class:`World` is pure convenience, but adding it
    as component in an entity (any entity) works just fine.

    All the logic take place in the
    :meth:`on_draw` method, which is a handler for the homonymous pyglet
    connected event.

    Rendering is done by dispatchment of
    :attr:`ON_CAMERA_DRAW_EVENT_NAME` event. :class:`Camera` and
    eventual custom objects handle this event and render accordingly.

    A :class:`pyglet.window.Window` can be specified and shall be taken
    as target of these transformations. In case of single window
    applications this is unnecessary and the main window will be
    automatically retrieven.
    """

    def __init__(self, window: Optional[pyglet.window.Window] = None):
        self.window = window
        if window is None:
            assert len(pyglet.app.windows), (
                'Unable to find an open window')
            self.window = next(iter(pyglet.app.windows))

    def on_draw(self):
        """Event handler: clear window and render all cameras.

        Rendering is done by dispatchment of
        :attr:`ON_CAMERA_DRAW_EVENT_NAME`.
        """
        self.window.clear()
        self.world.dispatch(ON_CAMERA_DRAW_EVENT_NAME)

    def process(self, dt):
        """No implementation needed."""
        pass


@desper.event_handler(desper.ON_POSITION_CHANGE_EVENT_NAME,
                      desper.ON_ROTATION_CHANGE_EVENT_NAME,
                      desper.ON_SCALE_CHANGE_EVENT_NAME)
class CameraTransform2D(desper.Controller):
    """Synchronize :class:`Camera` with :class:`desper.Transform2D`.

    A :class:`Camera`s internal :attr:`Camera.view` matrix is updated
    based on the entity's :class:`desper.Transform2D`.
    Requires to be in the same desper entity of both the camera and the
    transform component.
    """
    transform: desper.Transform2D = desper.ComponentReference(
        desper.Transform2D)
    camera: Camera = desper.ComponentReference(Camera)

    # Cached matrices for faster recalculations
    _translation_matrix = desper.math.Mat4()
    _rotation_matrix = desper.math.Mat4()
    _scale_matrix = desper.math.Mat4()

    def on_add(self, entity, world):
        """Setup transform event handling."""
        super().on_add(entity, world)

        assert self.transform is not None and self.camera is not None, (
            'Both a Transform component and a Camera component '
            'are required to be in the same entity in order for '
            f'{type(self)} to work.')

        transform = self.transform
        transform.add_handler(self)

        self._translation_matrix = desper.math.Mat4.from_translation(
            (*-transform.position, 0.))
        self._rotation_matrix = desper.math.Mat4.from_rotation(
            math.radians(transform.rotation), (0., 0., 1.))
        self._scale_matrix = desper.math.Mat4.from_scale(
            (*transform.scale, 1.))

        self.camera.view = self.get_view_matrix()

    def get_view_matrix(self) -> desper.math.Mat4:
        """Compute view matrix.

        Each query computes the matrix product between rotation,
        translation and scale matrix.
        """
        return (self._scale_matrix @ self._translation_matrix
                @ self._rotation_matrix)

    def on_position_change(self, new_position: desper.math.Vec2):
        """Event handler: update translation matrix and camera."""
        self._translation_matrix = desper.math.Mat4.from_translation(
            (*-new_position, 0.))

        self.camera.view = self.get_view_matrix()

    def on_rotation_change(self, new_rotation: float):
        """Event handler: update rotation matrix and camera."""
        self._rotation_matrix = desper.math.Mat4.from_rotation(
            math.radians(new_rotation), (0., 0., 1.))

        self.camera.view = self.get_view_matrix()

    def on_scale_change(self, new_scale: desper.math.Vec2):
        """Event handler: update scale matrix and camera."""
        self._scale_matrix = desper.math.Mat4.from_scale(
            (*new_scale, 1.))

        self.camera.view = self.get_view_matrix()
