from textual.app import App
from textual.binding import Binding
from textual.widgets import Switch, RadioSet
from textual.reactive import reactive
from textual import events
from pysui import SuiConfig, AsyncClient
from screens import LoadingScreen, Mod_Screen
from api import get_submissions

class Pod_By_FrenSuipport(App):
    CSS_PATH = "pod.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="l", action="toggle_lock", description="Lock the Screen"),
        Binding(key="s", action="splash", description="Splash!"),
        Binding(key="f5", action="refresh", description="Refresh wallet content"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        )
    ]

    SCREENS = {
        "loading": LoadingScreen,
        "main": Mod_Screen
    }

    is_locked = reactive(False)

    def __init__(self):
        super().__init__()
        self.client = None

    def on_mount(self) -> None:
        self.push_screen("loading")
        self.set_timer(2.5, self.load_main_screen)

    async def on_load(self) -> None:
        await self.init_client()
        await get_submissions()

    async def init_client(self) -> None:
        cfg = SuiConfig.default_config()
        self.client = AsyncClient(cfg)

    def load_main_screen(self) -> None:
        self.push_screen("main")

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        if isinstance(event.screen, Mod_Screen):
            self.query_one(RadioSet).focus()

    def action_toggle_lock(self) -> None:
        safe_lock = self.query_one("#safe-lock", Switch)
        safe_lock.toggle()
        self.is_locked = safe_lock.value

    def watch_is_locked(self, is_locked: bool) -> None:
        if isinstance(self.screen, Mod_Screen):
            self.screen.update_lock_state(is_locked)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "safe-lock":
            self.is_locked = event.value

    def action_splash(self) -> None:
        if isinstance(self.screen, Mod_Screen):
            self.screen.action_splash()
    
    def action_refresh(self) -> None:
        if isinstance(self.screen, Mod_Screen):
            wallet_content = self.screen.query_one("WalletContent")
            if wallet_content:
                wallet_content.load_wallet_content()

if __name__ == "__main__":
    app = Pod_By_FrenSuipport()
    app.run()