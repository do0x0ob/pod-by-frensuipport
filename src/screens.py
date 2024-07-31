from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Header, ContentSwitcher, Footer, Button, MarkdownViewer, Static
from textual.app import ComposeResult
from textual.css.query import NoMatches
from ascii_art import welcome
from render import Splash
from panels import LeftPanel, BottomRight
from custom_widgets import WalletContent
from pysui import SuiConfig, AsyncClient
import json


class LoadingScreen(Screen):
    """ Main Screen for MOD"""
    def compose(self) -> ComposeResult:
        yield Static(welcome, classes="ascii_text")

class Mod_Screen(Screen):
    def __init__(self):
        super().__init__()
        self.client = AsyncClient(SuiConfig.default_config())
        self.tasksheet_address = "0xc8e76738b2a255fe5d093a39f1eaa3b3ab869efcd62e4705c8790ceb7a532f02::public_task::Task"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app-grid"):
            yield LeftPanel(self.app.client, self.tasksheet_address, id="left-pane")
            top_right = ContentSwitcher(initial="splash", id="top-right", classes="invisible_border")
            top_right.border_title = ":: Content"
            with top_right:
                yield Splash(id="splash")
            yield BottomRight(id="bottom-right")
        yield Footer()


    def load_markdown_content(self):
        try:
            with open('markdown_contents.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("markdown_contents.json file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error decoding JSON from markdown_contents.json.")
            return {}
        

    async def load_and_switch_content(self, option_id: str) -> None:
        content_switcher = self.query_one("#top-right", ContentSwitcher)
        viewer_id = f"id_{option_id}"
        
        markdown_contents = self.load_markdown_content()
        content = markdown_contents.get(option_id, f"Content not found for ID: {option_id}")
        
        try:
            existing_viewer = content_switcher.get_child_by_id(viewer_id)
            if existing_viewer:
                content_switcher.current = viewer_id
            else:
                markdown_viewer = MarkdownViewer(
                    content,
                    id=viewer_id,
                    show_table_of_contents=False
                )
                await content_switcher.add_content(markdown_viewer, set_current=True)
        except NoMatches:
            markdown_viewer = MarkdownViewer(
                content,
                id=viewer_id,
                show_table_of_contents=False
            )
            await content_switcher.add_content(markdown_viewer, set_current=True)
            self.switch_content(viewer_id)


    def action_splash(self) -> None:
        self.switch_content("splash")
    
    def update_lock_state(self, is_locked: bool) -> None:
        bottom_right = self.query_one("#bottom-right", BottomRight)
        bottom_right.update_buttons_state(is_locked)
    

    def switch_content(self, content_id: str) -> None:
        content_switcher = self.query_one("#top-right", ContentSwitcher)
        content_switcher.current = content_id
        self.update_top_right_style(content_id)


    def on_wallet_content_option_selected(self, event: WalletContent.OptionSelected) -> None:
        option_id = event.option_id.replace("id_", "")
        self.run_worker(self.load_and_switch_content(option_id))
        self.update_top_right_style(event.option_id)


    def update_top_right_style(self, content_id: str) -> None:
        content_switcher = self.query_one("#top-right", ContentSwitcher)
        visible_class = "visible_border" if content_id != "splash" else "invisible_border"
        invisible_class = "invisible_border" if content_id != "splash" else "visible_border"
        content_switcher.remove_class(invisible_class)
        content_switcher.add_class(visible_class)


    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "approve":
            self.notify("Sending approving...", title="Approval", severity="information")
        elif event.button.id == "decline":
            self.notify("Declining task sheet...", title="Decline", severity="error")
    
    def handle_approve(self) -> None:
        bottom_right = self.query_one(BottomRight)
        bottom_right.handle_approve()

    def handle_decline(self) -> None:
        bottom_right = self.query_one(BottomRight)
        bottom_right.handle_decline()