from time import time

from textual.app import App, ComposeResult, RenderResult
from textual.containers import Container
from textual.renderables.gradient import LinearGradient
from textual.widgets import Static
from ascii_art import brand_slant
COLORS = [
    "#881177",
    "#aa3355",
    "#cc6666",
    #"#ee9944",
    #"#eedd00",
    #"#99dd55",
    #"#44dd88",
    #"#22ccbb",
    #"#00bbcc",
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


class SplashApp(App):
    """Simple app to show our custom widget."""

    def compose(self) -> ComposeResult:
        yield Splash()


if __name__ == "__main__":
    app = SplashApp()
    app.run()