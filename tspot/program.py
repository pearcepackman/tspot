from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static, Input

class FlexApp(App):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Static("[b]TSpot[/b]", classes = "title"),
            ),
            Container(
                Input(placeholder="Type to search...", classes="search-input")
            ),
            Container(
                Static("Hello, [i]User[/i]", classes = "hello")
            ),
            id="topbar"
            
        )
        # Main horizontal container
        yield Container(
            # Left section: vertical stack
            Container(
                Static("Left Top", classes="box"),
                Static("Left Bottom", classes="box"),
                id="left-column"
            ),
            # Right section: vertical stack
            Container(
                Static("Right Top", classes="box"),
                Static("Right Bottom", classes="box"),
                id="right-column"
            ),
            id="main-container"
        )

if __name__ == "__main__":
    FlexApp().run()
