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
