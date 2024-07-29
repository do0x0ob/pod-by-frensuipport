import asyncio
from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label, Static, Button, Switch, ContentSwitcher, OptionList
from textual.widgets.option_list import Option
from textual.containers import Vertical, Horizontal, Container, VerticalScroll
from textual.reactive import reactive
from textual.message import Message
from render import TanhLoader
from pysui import SuiConfig, AsyncClient
from pysui.sui.sui_types.address import SuiAddress
from constants import NETWORK_ENV_MAP
from api import get_submissions

class NetworkEnvironmentWidget(Static):
    def on_mount(self) -> None:
        self.update_network_info()

    def update_network_info(self) -> None:
        cfg = SuiConfig.default_config()
        client = AsyncClient(cfg)
        cur_url = client.config.rpc_url
        current_env = NETWORK_ENV_MAP.get(cur_url, "UNKNOWN").upper()
        self.update(f"::{current_env}::")


class WalletList(ListView):
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.border_subtitle = ":: Addresses"

    def on_mount(self):
        self.load_wallets()

    def load_wallets(self):
        addresses = self.client.config.addresses
        aliases = self.client.config.aliases
        active_address = self.client.config.active_address

        for address, alias in zip(addresses, aliases):
            short_address = f"{address[:2]}..{address[-4:]}"
            label_text = f"{alias}|{short_address}"
            if address == active_address:
                label_text += "*"
            self.append(ListItem(Label(label_text)))


class FunctionSwitches(Horizontal):
    def __init__(self, **kwargs):
        super().__init__(id="switches", **kwargs)
        self.border_subtitle = " :: Functions"

    def compose(self) -> ComposeResult:
        with Vertical(classes="switch_container"):
            yield Label("REFETCH", id="center")
            yield Button("F5", id="refetch")
        with Vertical(classes="switch_container"):
            yield Label("LOCK", id="center")
            yield Switch(id="safe-lock")


class WalletContent(Container):
    is_loading = reactive(True)

    def __init__(self, client: AsyncClient, tasksheet_address: SuiAddress):
        super().__init__()
        self.client = client
        self.tasksheet_address = tasksheet_address

    class OptionSelected(Message):
        def __init__(self, option_id: str):
            self.option_id = option_id
            super().__init__()
    
    def compose(self) -> ComposeResult:
        submissions = ContentSwitcher(initial="loading", id="submissions")
        submissions.border_subtitle = ":: Submissions"
        with submissions:
            yield Container(TanhLoader(id="loading-animation"), id="loading")
            yield VerticalScroll(id="wallet-content")

    def on_mount(self) -> None:
        self.load_wallet_content()

    def load_wallet_content(self) -> None:
        self.is_loading = True
        self.query_one(ContentSwitcher).current = "loading"
        self.query_one(TanhLoader).is_animating = True
        asyncio.create_task(self._finish_loading())

    async def _finish_loading(self) -> None:
        wallet_content = self.query_one("#wallet-content")
        wallet_content.remove_children()
        try:
            submissions = await get_submissions()
            for task_name, task_data in submissions.items():
                task_container = Vertical(
                    Container(
                        Static(task_name, classes="taskname"),
                        classes="task_container"
                    ),
                    Vertical(
                        *[OptionList(
                            Option(f"{address[:4]}...{address[-22:]}", id=f"id_{address}"),
                            classes="task_option"
                        ) for address in task_data['tasksheets'].keys()],
                        classes="options_container"
                    ),
                    classes="main_task_group"
                )
                wallet_content.mount(task_container)
        
        except Exception as e:
            print(f"Error in _finish_loading: {str(e)}")

        self.is_loading = False
        self.query_one(TanhLoader).is_animating = False
        self.query_one(ContentSwitcher).current = "wallet-content"
    
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.post_message(self.OptionSelected(event.option.id))



class PanelController:
    def __init__(self, panel):
        self.panel = panel

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refetch":
            self.reload_wallet_content()

    def reload_wallet_content(self) -> None:
        wallet_content = self.panel.query_one(WalletContent)
        wallet_content.load_wallet_content()

    def watch_is_loading(self, is_loading: bool) -> None:
        refetch_button = self.panel.query_one("#refetch", Button)
        refetch_button.disabled = is_loading

