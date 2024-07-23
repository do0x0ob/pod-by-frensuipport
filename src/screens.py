from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Header, RadioSet, ContentSwitcher, Footer, Button, MarkdownViewer, TextArea, LoadingIndicator, Static
from textual.app import ComposeResult
from ascii_art import welcome
from render import Splash
from panels import LeftPanel, BottomRight
from files import MARKDOWN_CONTENT

class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        # yield LoadingIndicator()
        yield Static(welcome, classes="ascii_text")
        #yield Static(submarine, classes="ascii_text")

class Mod_Screen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app-grid"):
            yield LeftPanel(self.app.client, id="left-pane")
            top_right = ContentSwitcher(initial="splash", id="top-right")
            top_right.border_title = ":: Content"
            with top_right:
                yield Splash(id="splash")
                for i in range(1, 4):
                    yield MarkdownViewer(
                        MARKDOWN_CONTENT[f"content{i}"],
                        id=f"m{i}",
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
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.switch_content(event.pressed.id)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "approve":
            self.notify("Submission approved!", title="Approval", severity="information")
        elif event.button.id == "decline":
            self.notify("Submission declined!", title="Decline", severity="error")
        
        textarea = self.query_one("#void", TextArea)
        textarea.clear()