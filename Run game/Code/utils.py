# utils.py
import textwrap

def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=40))
    return lines
