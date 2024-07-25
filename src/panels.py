from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, TextArea
from textual.app import ComposeResult
from custom_widgets import WalletList, NetworkEnvironmentWidget, FunctionSwitches, WalletContent, PanelController

class LeftPanel(VerticalScroll):
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.controller = PanelController(self)

    def compose(self) -> ComposeResult:
        self.border_title = ":: Wallet"
        
        yield NetworkEnvironmentWidget(id="network", classes="hatch cross_theme")
        with Container(id="wallet-container"):
            yield WalletList(self.client, id="wallet-list")
        yield FunctionSwitches()
        yield WalletContent()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.controller.on_button_pressed(event)
    
    def watch_wallet_content_is_loading(self, is_loading: bool) -> None:
        self.controller.watch_is_loading(is_loading)
        
class BottomRight(Horizontal):
    def compose(self) -> ComposeResult:
        self.border_title = ":: Annotations"
        
        yield TextArea(id="void")
        
        snippets = Horizontal(id="snippets", classes="hatch cross")
        snippets.border_title = ":: Caution ::"
        with snippets:
            yield Button("Approved", id="approve", variant="primary", disabled=False)
            yield Button("Declined", id="decline", variant="error", disabled=False)
    
    def update_buttons_state(self, is_locked: bool) -> None:
        approve_button = self.query_one("#approve", Button)
        decline_button = self.query_one("#decline", Button)
        approve_button.disabled = is_locked
        decline_button.disabled = is_locked