from textual.app import App, ComposeResult
from textual.containers import Container, Center
from textual.binding import Binding
from textual.widgets import Header, RadioSet, ContentSwitcher, Switch, Footer, Button, MarkdownViewer, TextArea, LoadingIndicator, Static
from textual.screen import Screen
from textual import events
from render import Splash
from panels import LeftPanel, BottomRight
from files import MARKDOWN_CONTENT
from pysui import SuiConfig, AsyncClient

"""
class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        with Container(id="loading-container"):
            yield Splash(id="loading-splash")
"""

class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        with Center():
            yield LoadingIndicator()
            yield Static("Loading...", id="loading-text")

class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app-grid"):
            yield LeftPanel(self.app.client, id="left-pane")
            top_right = ContentSwitcher(initial="splash", id="top-right")
            top_right.border_title = ":: Content"
            with top_right:
                yield Splash(id="splash")
                for i in range(1, 4):
                    yield MarkdownViewer(
                        MARKDOWN_CONTENT[f"content{i}"],
                        id=f"m{i}",  # 修改这里，使用 "m1", "m2", "m3" 作为 ID
                        show_table_of_contents=False
                    )
            yield BottomRight(id="bottom-right")
        yield Footer()

class Pod_By_FrenSuipport(App):
    CSS_PATH = "pod.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="l", action="toggle_lock", description="Lock the Screen"),
        Binding(key="s", action="splash", description="Splash!"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        )
    ]

    SCREENS = {
        "loading": LoadingScreen,
        "main": MainScreen
    }

    def __init__(self):
        super().__init__()
        self.client = None

    def on_mount(self) -> None:
        self.push_screen("loading")
        self.set_timer(2.5, self.load_main_screen)

    async def on_load(self) -> None:
        await self.init_client()

    async def init_client(self) -> None:
        cfg = SuiConfig.default_config()
        self.client = AsyncClient(cfg)

    def load_main_screen(self) -> None:
        self.push_screen("main")

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        if isinstance(event.screen, MainScreen):
            self.query_one(RadioSet).focus()

    def action_toggle_lock(self) -> None:
        safe_lock = self.query_one("#safe-lock", Switch)
        safe_lock.toggle()
        self.update_lock_state(safe_lock.value)

    def update_lock_state(self, is_locked: bool) -> None:
        approve_button = self.query_one("#approve", Button)
        decline_button = self.query_one("#decline", Button)
        approve_button.disabled = is_locked
        decline_button.disabled = is_locked

    def action_splash(self) -> None:
        self.switch_content("splash")

    def switch_content(self, content_id: str) -> None:
        content_switcher = self.query_one("#top-right", ContentSwitcher)
        content_switcher.current = content_id
        if content_id == "splash":
            content_switcher.remove_class("markdown-view")
        else:
            content_switcher.add_class("markdown-view")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.switch_content(event.pressed.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "approve":
            self.notify("Submission approved!", title="Approval", severity="information")
        elif event.button.id == "decline":
            self.notify("Submission declined!", title="Decline", severity="error")
        
        textarea = self.query_one("#void", TextArea)
        textarea.clear()

if __name__ == "__main__":
    app = Pod_By_FrenSuipport()
    app.run()