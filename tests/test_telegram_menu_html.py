import ast
import unittest
from html.parser import HTMLParser
from pathlib import Path


class MenuParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in {"b"}:
            self.errors.append(f"Unexpected tag: {tag}")
        self.tags.append(tag)


class TelegramMenuTest(unittest.TestCase):
    def test_main_menu_html(self):
        path = Path(__file__).resolve().parents[1] / (
            "app/telegram/handlers.py"
        )
        tree = ast.parse(path.read_text())

        function = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_main_menu_text"
        )

        result = next(
            node for node in function.body
            if isinstance(node, ast.Return)
        )

        menu = ast.literal_eval(result.value)

        self.assertIn("&lt;id&gt;", menu)
        self.assertIn("&lt;status|history|export&gt;", menu)
        self.assertLessEqual(len(menu), 4096)

        parser = MenuParser()
        parser.feed(menu)
        self.assertEqual(parser.errors, [])
        self.assertEqual(menu.count("<b>"), menu.count("</b>"))


if __name__ == "__main__":
    unittest.main()
