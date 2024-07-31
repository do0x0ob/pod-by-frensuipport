from time import time
import math
from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.containers import Container
from textual.renderables.gradient import LinearGradient
from textual.widgets import Static
from rich.console import RenderableType
from rich.text import Text
from rich.style import Style
from ascii_art import brand_slant

COLORS = [
    "#881177",
    "#aa3355",
    "#cc6666",
    "#0099cc",
    "#3366bb",
    "#663399",
]
STOPS = [(i / (len(COLORS) - 1), color) for i, color in enumerate(COLORS)]


class Splash(Container):
    """Custom Colorful Amination widget that extends Container."""

    DEFAULT_CSS = """
    Splash {
        align: center middle;
    }
    Static {
        width: auto;
        padding: 2 4;
    }
    """

    def on_mount(self) -> None:
        self.auto_refresh = 1 / 60

    def compose(self) -> ComposeResult:
        yield Static(brand_slant)  

    def render(self) -> RenderResult:
        return LinearGradient(time() * 60, STOPS)  


class TanhLoader(Widget):
    DEFAULT_CSS = """
    TanhLoader {
        height: 2;
        width: 1fr;
    }
    """

    values = reactive([0] * 42) 
    colors = ["#881177", "#aa3355", "#cc6666", "#0099cc", "#3366bb", "#663399"] * 7  # repeat color list for 7 times
    animation_step = reactive(0)
    is_animating = reactive(True)

    def on_mount(self):
        self.set_interval(0.02, self.update_animation)

    def update_animation(self):
        if not self.is_animating:
            return

        self.animation_step += 1
        for i in range(42):
            x = math.sin((self.animation_step + i * 4) * 0.1) * 2
            self.values[i] = (x + 2) * 1.75

    def render(self) -> RenderableType:
        bars = []
        for value, color in zip(self.values, self.colors):
            bar = "▁▂▃▄▅▆▇█"[min(int(value), 7)]
            bars.append(Text(bar, Style(color=color)))
        return Text(" ").join(bars)