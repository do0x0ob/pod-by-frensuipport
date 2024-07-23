from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.widgets import Switch, Button, Static, RadioSet, RadioButton, Collapsible, TextArea, Label, ListView, ListItem
from textual.app import ComposeResult

class LeftPanel(VerticalScroll):
    def compose(self) -> ComposeResult:
        self.border_title = ":: Wallet"
        
        yield Static("::_TESTNET_::", id="network", classes="hatch cross_theme")

        with Container(id="wallet-container"):
            wallet_list = ListView(
                ListItem(Label("Ruby| 0x4685")),
                ListItem(Label("sappaire| 0x123")),
                ListItem(Label("sappaire| 0x123")),
                id="wallet-list"
            )
            wallet_list.border_subtitle = ":: Addresses"
            yield wallet_list

        switches = Horizontal(id="switches")
        switches.border_subtitle = " :: Switches"
        with switches:
            with Vertical(classes="switch_container"):
                yield Label("MOD", id="center")
                yield Switch(id="mod-switch", disabled=True)
            with Vertical(classes="switch_container"):
                yield Label("LOCK", id="center")
                yield Switch(id="safe-lock")

        task_sheets = VerticalScroll(id="wallet-content")
        task_sheets.border_subtitle = ":: Submissions"
        with task_sheets:
            with Collapsible(id="task1", title="Greatest Coffee Maker Ever"):
                with RadioSet(id="focus_me"):
                    yield RadioButton("0x...5412542154125421", id="m1")
                    yield RadioButton("0x...5412542154125421", id="m2")
                    yield RadioButton("0x...5412542154125421", id="m3")
            with Collapsible(id="task2", title="Learn Sui Move"):
                with RadioSet(id="focus_me2"):
                    yield RadioButton("0x...5412542154125421", id="m4")
                    yield RadioButton("0x...5412542154125421", id="m5")
                    yield RadioButton("0x...5412542154125421", id="m6")
            with Collapsible(id="task3", title="Home Brew Beer"):
                with RadioSet(id="focus_me3"):
                    yield RadioButton("0x...5412542154125421", id="m7")
                    yield RadioButton("0x...5412542154125421", id="m8")
                    yield RadioButton("0x...5412542154125421", id="m9")
        

class BottomRight(Horizontal):
    def compose(self) -> ComposeResult:
        self.border_title = ":: Annotations"
        
        yield TextArea(id="void")
        
        snippets = Horizontal(id="snippets", classes="hatch cross")
        snippets.border_title = ":: Caution ::"
        with snippets:
            yield Button("Approved", id="approve", variant="primary", disabled=False)
            yield Button("Declined", id="decline", variant="error", disabled=False)