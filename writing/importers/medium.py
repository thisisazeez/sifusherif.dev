"""
Medium importer — fetches articles from Medium's public RSS feed.

Pre-configured for @sifusherif. Usage:

    from writing.importers.medium import MediumImporter
    importer = MediumImporter()
    imported, skipped = importer.import_all(series=my_series)

Or via management command:
    python manage.py import_articles medium --series django-actually
"""
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from .base import BaseImporter

# Medium's content namespace
_CONTENT_NS = 'http://purl.org/rss/1.0/modules/content/'

# Default username — change here or pass to __init__
DEFAULT_USERNAME = 'sifusherif'


class MediumImporter(BaseImporter):
    source_name = 'medium'

    def __init__(self, username: str = DEFAULT_USERNAME):
        self.username = username
        self.feed_url = f'https://medium.com/feed/@{username}'

    def fetch_articles(self) -> list[dict]:
        """
        Parse the Medium RSS feed and return normalised article dicts.
        Medium's RSS includes full HTML content in <content:encoded>.
        We convert that HTML back to clean Markdown for storage.
        """
        try:
            req = urllib.request.Request(
                self.feed_url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            response = urllib.request.urlopen(req, timeout=15)
        except Exception as exc:
            raise RuntimeError(
                f'Could not fetch Medium feed for @{self.username}: {exc}\n'
                'Check your internet connection.'
            ) from exc

        tree = ET.parse(response)
        root = tree.getroot()

        articles = []
        for item in root.iter('item'):
            title     = item.findtext('title', '').strip()
            link      = item.findtext('link', '').strip()
            pub_date  = item.findtext('pubDate', '').strip()
            html_body = item.findtext(f'{{{_CONTENT_NS}}}encoded', '')

            if not title or not html_body:
                continue

            standfirst = self._extract_standfirst(html_body)
            body_md    = self._html_to_md(html_body)
            pub        = self._parse_date(pub_date)

            articles.append({
                'title':        title,
                'standfirst':   standfirst,
                'body_md':      body_md,
                'published_at': pub,
                'source_url':   link,
            })

        return articles

    # ── Private helpers ────────────────────────────────────────────────────────

    def _extract_standfirst(self, html: str) -> str:
        """
        Pull the first <p> tag as the standfirst / excerpt.
        Strips all inner tags and returns plain text.
        """
        match = re.search(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        if not match:
            return ''
        text = re.sub(r'<[^>]+>', '', match.group(1))
        return text.strip()[:400]

    def _html_to_md(self, html: str) -> str:
        """
        Convert Medium's HTML body to clean Markdown.

        We handle the common elements Medium produces:
          <h1>, <h2>, <h3> → # / ## / ###
          <p>              → paragraph (blank line separated)
          <strong>, <em>   → **bold**, *italic*
          <a href>         → [text](url)
          <ul>/<li>        → - item
          <ol>/<li>        → 1. item
          <blockquote>     → > quote
          <pre><code>      → ``` code block ```
          <code>           → `inline code`
          <hr>             → ---
          <img>            → ![alt](src)
          <figure>         → stripped (Medium wraps images in figures)

        Everything else has its tags stripped, text preserved.
        """
        h = html

        # Pre/code blocks first (protect their contents from other transforms)
        def preserve_pre(m):
            lang_match = re.search(r'class="[^"]*language-(\w+)', m.group(0))
            lang = lang_match.group(1) if lang_match else ''
            code = re.sub(r'<[^>]+>', '', m.group(1))
            code = self._unescape(code)
            return f'\n```{lang}\n{code}\n```\n'

        h = re.sub(r'<pre[^>]*>(.*?)</pre>', preserve_pre, h, flags=re.DOTALL)

        # Inline code
        h = re.sub(r'<code[^>]*>(.*?)</code>',
                   lambda m: f'`{re.sub(r"<[^>]+>", "", m.group(1))}`', h)

        # Images
        h = re.sub(r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"[^>]*/?>',
                   lambda m: f'![{m.group(2)}]({m.group(1)})', h)
        h = re.sub(r'<img[^>]+src="([^"]+)"[^>]*/?>',
                   lambda m: f'![]({m.group(1)})', h)

        # Headings
        h = re.sub(r'<h1[^>]*>(.*?)</h1>', lambda m: f'\n# {self._strip(m.group(1))}\n', h)
        h = re.sub(r'<h2[^>]*>(.*?)</h2>', lambda m: f'\n## {self._strip(m.group(1))}\n', h)
        h = re.sub(r'<h3[^>]*>(.*?)</h3>', lambda m: f'\n### {self._strip(m.group(1))}\n', h)
        h = re.sub(r'<h4[^>]*>(.*?)</h4>', lambda m: f'\n#### {self._strip(m.group(1))}\n', h)

        # Blockquotes
        h = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>',
                   lambda m: f'\n> {self._strip(m.group(1))}\n', h, flags=re.DOTALL)

        # Bold / italic
        h = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', h)
        h = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', h)
        h = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', h)
        h = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', h)

        # Links
        h = re.sub(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                   lambda m: f'[{self._strip(m.group(2))}]({m.group(1)})', h)

        # Lists
        h = re.sub(r'<li[^>]*>(.*?)</li>',
                   lambda m: f'- {self._strip(m.group(1))}\n', h, flags=re.DOTALL)
        h = re.sub(r'<[uo]l[^>]*>', '\n', h)
        h = re.sub(r'</[uo]l>', '\n', h)

        # Paragraphs
        h = re.sub(r'<p[^>]*>(.*?)</p>',
                   lambda m: f'\n{self._strip(m.group(1))}\n', h, flags=re.DOTALL)

        # HR
        h = re.sub(r'<hr[^>]*/?>',  '\n---\n', h)

        # Strip remaining tags (figures, divs, spans, etc.)
        h = re.sub(r'<[^>]+>', '', h)

        # Decode HTML entities
        h = self._unescape(h)

        # Collapse excessive blank lines
        h = re.sub(r'\n{3,}', '\n\n', h)

        return h.strip()

    def _strip(self, html: str) -> str:
        """Remove HTML tags from a string."""
        return re.sub(r'<[^>]+>', '', html).strip()

    def _unescape(self, text: str) -> str:
        """Decode common HTML entities."""
        entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>',
            '&quot;': '"', '&#39;': "'", '&nbsp;': ' ',
            '&mdash;': '—', '&ndash;': '–', '&hellip;': '…',
        }
        for ent, char in entities.items():
            text = text.replace(ent, char)
        return text

    def _parse_date(self, rfc_date: str):
        """Parse RFC 2822 date string to a date object."""
        from datetime import date as date_type
        if not rfc_date:
            return date_type.today()
        try:
            # e.g. "Mon, 02 Jun 2026 12:00:00 GMT"
            return datetime.strptime(rfc_date[:16].strip(), '%a, %d %b %Y').date()
        except ValueError:
            return date_type.today()
