"""
writing/utils.py

Markdown → HTML renderer that produces markup compatible with the
art-content and cs-content CSS classes in style.css.

The HTML output is placed inside an <article class="art-content"> (or
cs-content) wrapper in the template, so element-level selectors in the
stylesheet (.art-content h2, .art-content pre, etc.) apply automatically.

Special components (art-note, cs-callout) are written as raw HTML blocks
directly in the Markdown source — the markdown library passes them through
unchanged, so the author retains full fidelity.

Usage:
    from writing.utils import render_markdown, calculate_read_time, word_count_from_html

    html = render_markdown(markdown_source)
    wc   = word_count_from_html(html)
    rt   = calculate_read_time(wc)
"""

import re
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _build_md():
    """Build and return a configured Markdown instance."""
    import markdown
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.nl2br import Nl2BrExtension
    from markdown.extensions.attr_list import AttrListExtension
    from markdown.extensions.codehilite import CodeHiliteExtension

    extensions = [
        FencedCodeExtension(),         # ```python ... ``` blocks
        TableExtension(),              # | col | col | tables
        AttrListExtension(),           # {.class #id} attribute syntax
        # CodeHiliteExtension is optional — gives syntax highlighting via Pygments
        # Uncomment once `pygments` is installed:
        # CodeHiliteExtension(css_class='highlight', guess_lang=False),
    ]
    return markdown.Markdown(
        extensions=extensions,
        output_format='html',
    )


def render_markdown(source: str) -> str:
    """
    Convert Markdown source to HTML.

    Raw HTML blocks (e.g. <div class="art-note">) are passed through
    unchanged, which lets authors embed special template components.

    The caller is responsible for marking the result safe in templates:
        {{ article.body_html|safe }}
    """
    try:
        md = _build_md()
        return md.convert(source)
    except ImportError:
        # Graceful fallback before `markdown` is installed
        escaped = source.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre>{escaped}</pre>'


# ---------------------------------------------------------------------------
# Read-time calculation
# ---------------------------------------------------------------------------

class _PlainTextExtractor(HTMLParser):
    """Strip all HTML tags and collect text content."""

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return ' '.join(self._parts)


def word_count_from_html(html: str) -> int:
    """Return approximate word count of text content inside HTML."""
    parser = _PlainTextExtractor()
    parser.feed(html)
    text = parser.get_text()
    return len(re.findall(r'\b\w+\b', text))


def calculate_read_time(word_count: int, wpm: int = 238) -> int:
    """
    Estimate reading time in minutes.

    238 wpm is the research-backed average for adults reading on screens
    (Rayner et al., 2016). Minimum returned value is 1 minute.
    """
    return max(1, round(word_count / wpm))
