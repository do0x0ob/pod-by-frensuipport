from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Container
from textual.widgets import Button, Label, ContentSwitcher, LoadingIndicator, Collapsible, RadioButton
from textual.reactive import reactive

class WalletApp(App):
    is_loading = reactive(True)

    def compose(self) -> ComposeResult:
        yield Button("Refresh Wallet", id="refresh-button", variant="primary")
        with Container(id="wallet-container"):
            with ContentSwitcher(initial="loading"):
                with LoadingIndicator(id="loading"):
                    yield Label("Loading wallet content...")
                
                yield VerticalScroll(id="wallet-content")

    def on_mount(self) -> None:
        self.query_one("#wallet-content").border_subtitle = ":: Submissions"
        self.load_wallet_content()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-button":
            self.load_wallet_content()

    def load_wallet_content(self) -> None:
        self.is_loading = True
        self.query_one(ContentSwitcher).current = "loading"
        
        # 使用 set_timer 来模拟异步加载
        self.set_timer(2, self._finish_loading)

    def _finish_loading(self) -> None:
        wallet_content = self.query_one("#wallet-content")
        wallet_content.remove_children()
        
        wallet_content.mount(Label(":: Submissions", classes="subtitle"))
        wallet_content.mount(Collapsible(RadioButton("0x...5412542154125421", id="m1"), title="Greatest Coffee Maker Ever"))
        wallet_content.mount(Collapsible(RadioButton("0x...5412542154125421", id="m2"), title="Learn Sui Move"))
        wallet_content.mount(Collapsible(RadioButton("0x...5412542154125421", id="m3"), title="Home Brew Beer"))
        
        self.is_loading = False
        self.query_one(ContentSwitcher).current = "wallet-content"

    def watch_is_loading(self, is_loading: bool) -> None:
        refresh_button = self.query_one("#refresh-button", Button)
        refresh_button.disabled = is_loading

if __name__ == "__main__":
    app = WalletApp()
    app.run()