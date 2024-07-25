from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label, Static, Button, Switch
from textual.containers import Vertical, Horizontal
from pysui import SuiConfig, AsyncClient
from pysui.sui.sui_constants import (
    DEVNET_SUI_URL,
    LOCALNET_SUI_URL,
    TESTNET_SUI_URL,
    MAINNET_SUI_URL,
    DEVNET_ENVIRONMENT_KEY,
    LOCALNET_ENVIRONMENT_KEY,
    TESTNET_ENVIRONMENT_KEY
)

NETWORK_ENV_MAP = {
    DEVNET_SUI_URL: DEVNET_ENVIRONMENT_KEY,
    LOCALNET_SUI_URL: LOCALNET_ENVIRONMENT_KEY,
    TESTNET_SUI_URL: TESTNET_ENVIRONMENT_KEY,
    MAINNET_SUI_URL: "mainnet"
}


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
