from textual.app import App, ComposeResult
from textual.containers import Container
from textual.binding import Binding
from textual.widgets import Header, RadioSet, ContentSwitcher, Switch, Footer, Button, MarkdownViewer, TextArea
from render import Splash
from panels import LeftPanel, BottomRight
from files import MARKDOWN_CONTENT

class Pod_By_FrenSuipport(App):
    CSS_PATH = "pod.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="l", action="toggle_lock", description="Lock the Screen"),
        Binding(key="s", action="splash", description="Splash!"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        )
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="app-grid"):
            yield LeftPanel(id="left-pane")
            top_right = ContentSwitcher(initial="splash", id="top-right")
            top_right.border_title = ":: Content"
            with top_right:
                yield Splash(id="splash")
                for i in range(1, 4):
                    yield MarkdownViewer(
                        MARKDOWN_CONTENT[f"content{i}"],
                        id=f"content{i}", 
                        show_table_of_contents=False
                    )
            yield BottomRight(id="bottom-right")
        yield Footer()

    # TODO: update needed
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        selected_option = event.pressed.id
        content_id = f"content{selected_option[-1]}"
        self.switch_content(content_id)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Event handler for the switch status change."""
        self.update_lock_state(event.value)

    def action_toggle_lock(self) -> None:
        """Action to toggle the lock state when 'l' is pressed."""
        safe_lock = self.query_one("#safe-lock", Switch)
        safe_lock.toggle()
        self.update_lock_state(safe_lock.value)

    def update_lock_state(self, is_locked: bool) -> None:
        """Updates the disabled state of the approve and decline buttons."""
        approve_button = self.query_one("#approve", Button)
        decline_button = self.query_one("#decline", Button)
        approve_button.disabled = is_locked
        decline_button.disabled = is_locked

    def action_splash(self) -> None:
        """Action to switch back to splash screen when 's' is pressed."""
        self.switch_content("splash")

    def switch_content(self, content_id: str) -> None:
        """Switch the content and update classes accordingly."""
        content_switcher = self.query_one("#top-right", ContentSwitcher)
        content_switcher.current = content_id
        if content_id == "splash":
            content_switcher.remove_class("markdown-view")
        else:
            content_switcher.add_class("markdown-view")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "approve":
            self.notify("Submission approved!", title="Approval", severity="information")
        elif event.button.id == "decline":
            self.notify("Submission declined!", title="Decline", severity="error")
        
        # Clear the textarea
        textarea = self.query_one("#void", TextArea)
        textarea.clear()
    
# Entry Point
if __name__ == "__main__":
    app = Pod_By_FrenSuipport()
    app.run()