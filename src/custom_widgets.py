from textual.widgets import ListView, ListItem, Label

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
            short_address = f"{address[:4]}...{address[-4:]}"
            label_text = f"{alias}|{short_address}"
            if address == active_address:
                label_text += "*"
            self.append(ListItem(Label(label_text)))