from textual import on
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, TextArea
from textual.app import ComposeResult
from custom_widgets import WalletList, NetworkEnvironmentWidget, FunctionSwitches, WalletContent, PanelController
from movecall import approve_tasksheet

class LeftPanel(VerticalScroll):
    def __init__(self, client, tasksheet_address, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.controller = PanelController(self)
        self.tasksheet_address = tasksheet_address

    def compose(self) -> ComposeResult:
        self.border_title = ":: Wallet"
        
        yield NetworkEnvironmentWidget(id="network", classes="hatch cross_theme")
        with Container(id="wallet-container"):
            yield WalletList(self.client, id="wallet-list")
        yield FunctionSwitches()
        yield WalletContent(self.client, self.tasksheet_address)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.controller.on_button_pressed(event)
    
    def watch_wallet_content_is_loading(self, is_loading: bool) -> None:
        self.controller.watch_is_loading(is_loading)
        
class BottomRight(Horizontal):
    def compose(self) -> ComposeResult:
        self.border_title = ":: Annotations"
        
        yield TextArea(id="annotation_input")
        
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
    
    @on(Button.Pressed, "#approve")
    def handle_approve(self, event: Button.Pressed) -> None:
        annotation = self.query_one("#annotation_input", TextArea)
        
        # 這裡你需要獲取其他必要的參數
        task_id = "0x690ecfcaca9af8c8708282e5242ce0ac1df3c4f13c2c3e95479adb6f28930e11"
        task_sheet_id = "0x95485527d405e1e6158a325bff84da75ff270dbfbc197982471fb5656adffb5f"
        mod_cap_id = "0x263c23fd72b08bda2adec5298c797f35e9f2e9d87043b6efeb773a5b202faa5c"

        res = approve_tasksheet(task_id, task_sheet_id, mod_cap_id, annotation.text)
        if res:
            annotation.clear()
            self.app.action_refresh()
            self.screen.action_splash()