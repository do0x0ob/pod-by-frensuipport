import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Center
from textual.widgets import Header, Footer, Static, LoadingIndicator, Button
from textual.screen import Screen

class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        with Center():
            yield LoadingIndicator()
            yield Static("Loading...", id="loading-text")

class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Static("Main Application Content")
            yield Button("Test Button", id="test-button")
        yield Footer()

    def on_button_pressed(self) -> None:
        self.app.notify("Button pressed!")

class LoadingTestApp(App):
    """A Textual app to demonstrate loading screen."""

    CSS = """
    LoadingScreen {
        align: center middle;
    }

    #loading-text {
        margin-top: 1;
    }

    Container {
        align: center middle;
    }
    """

    SCREENS = {
        "loading": LoadingScreen,
        "main": MainScreen
    }

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def on_mount(self) -> None:
        self.push_screen("loading")
        self.set_timer(3, self.load_main_screen)

    def load_main_screen(self) -> None:
        self.push_screen("main")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

if __name__ == "__main__":
    app = LoadingTestApp()
    app.run()