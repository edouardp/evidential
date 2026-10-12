# /// script
# requires-python = ">=3.11"
# dependencies = ["textual"]
# ///
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import OptionList, Static

FRUITS = {
    "Apple": "A crisp, sweet fruit. Great for pies and snacking.",
    "Banana": "A tropical favourite. Rich in potassium.",
    "Cherry": "Small, tart, and perfect for desserts.",
    "Dragonfruit": "Exotic cactus fruit with mild, sweet flesh.",
    "Elderberry": "Dark berry used in syrups and wines.",
    "Fig": "Soft, honey-sweet fruit. Pairs well with cheese.",
}


class ChooserApp(App):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [("escape,ctrl+c", "quit")]
    CSS = """
    #title {
        padding: 0 0 1 1;
    }
    Horizontal {
        height: auto;
    }
    OptionList {
        width: 1fr;
        height: auto;
    }
    #description {
        width: 1fr;
        height: auto;
        padding: 1 2;
    }
    """

    def __init__(self, items: list[str] | dict[str, str] | None = None, title: str | None = None):
        super().__init__()
        self.title_text = title
        if isinstance(items, dict):
            self.items = items
        elif items:
            self.items = dict.fromkeys(items, "")
        else:
            self.items = FRUITS

    def compose(self) -> ComposeResult:
        if self.title_text:
            yield Static(self.title_text, id="title")
        with Horizontal():
            yield OptionList(*self.items.keys())
            yield Static("", id="description")

    def on_mount(self) -> None:
        self.capture_mouse(self.query_one(OptionList))

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self.query_one("#description", Static).update(self.items[str(event.option.prompt)])

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(str(event.option.prompt))


if __name__ == "__main__":
    import json
    import os
    import sys

    args = sys.argv[1:]
    title = None
    if "--title" in args:
        i = args.index("--title")
        title = args[i + 1]
        args = args[:i] + args[i + 2 :]
    items = None
    if len(args) == 1 and args[0].endswith(".json"):
        with open(args[0]) as f:
            data = json.load(f)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data
    elif args:
        items = args

    result = ChooserApp(items, title=title).run(inline=True)
    if result:
        try:
            os.write(3, result.encode())
        except OSError:
            print(result)
    else:
        sys.exit(1)
