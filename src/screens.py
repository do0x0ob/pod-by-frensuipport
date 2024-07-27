from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Header, ContentSwitcher, Footer, Button, MarkdownViewer, TextArea, Static
from textual.app import ComposeResult
from ascii_art import welcome
from render import Splash
from panels import LeftPanel, BottomRight
from custom_widgets import WalletContent
from pysui import SuiConfig, AsyncClient
import json


class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static(welcome, classes="ascii_text")

class Mod_Screen(Screen):
    
    
    def __init__(self):
        super().__init__()
        self.client = AsyncClient(SuiConfig.default_config())
        self.tasksheet_address = "0xc8e76738b2a255fe5d093a39f1eaa3b3ab869efcd62e4705c8790ceb7a532f02::public_task::Task"

    
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
    

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app-grid"):
            yield LeftPanel(self.app.client, self.tasksheet_address, id="left-pane")
            top_right = ContentSwitcher(initial="splash", id="top-right")
            top_right.border_title = ":: Content"
            with top_right:
                yield Splash(id="splash")
                markdown_contents = self.load_markdown_content() #TODO: 優化為獨立函數，點擊刷新之後可以重複使用，生成最新 markdown view
                for submission_id, content in markdown_contents.items():
                    yield MarkdownViewer(
                        content,
                        id=f"id_{submission_id}",
                        show_table_of_contents=False
                    )
            yield BottomRight(id="bottom-right")
        yield Footer()


    def action_splash(self) -> None:
        self.switch_content("splash")    
    
    def update_lock_state(self, is_locked: bool) -> None:
        bottom_right = self.query_one("#bottom-right", BottomRight)
        bottom_right.update_buttons_state(is_locked)
    
    def switch_content(self, content_id: str) -> None:
        content_switcher = self.query_one("#top-right", ContentSwitcher)
        content_switcher.current = content_id
        if content_id == "splash":
            content_switcher.remove_class("markdown-view")
        else:
            content_switcher.add_class("markdown-view")

    def on_wallet_content_option_selected(self, event: WalletContent.OptionSelected) -> None:
        self.switch_content(event.option_id)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "approve":
            self.notify("Submission approved!", title="Approval", severity="information")
        elif event.button.id == "decline":
            self.notify("Submission declined!", title="Decline", severity="error")
        
        textarea = self.query_one("#void", TextArea)
        textarea.clear()