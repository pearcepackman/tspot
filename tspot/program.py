from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static

QUESTION = "What is your favorite programming language?"

class FlexApp(App):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Container(
            Static(QUESTION, classes="question"),
            id="main-container"
        )

if __name__ == "__main__":
    FlexApp().run()
