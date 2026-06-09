"""Base importer — shared logic for all platform importers."""
import re
from datetime import date
from writing.models import Article, Series
from writing.utils import render_markdown, word_count_from_html, calculate_read_time


class BaseImporter:
    source_name: str = ''

    def fetch_articles(self) -> list[dict]:
        """
        Must return a list of dicts with keys:
            title       str
            standfirst  str   (first paragraph / brief)
            body_md     str   (Markdown content)
            published_at date
            source_url  str
        """
        raise NotImplementedError

    def import_all(
        self,
        series: Series | None = None,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> tuple[list[Article], list[str]]:
        """
        Import all articles from the platform.
        Returns (imported_articles, skipped_urls).
        """
        imported = []
        skipped  = []

        for data in self.fetch_articles():
            url = data.get('source_url', '')
            existing = Article.objects.filter(source_url=url).first() if url else None

            if existing and not overwrite:
                skipped.append(url)
                continue

            body_html = render_markdown(data.get('body_md', ''))
            wc = word_count_from_html(body_html)
            rt = calculate_read_time(wc)

            defaults = {
                'title':         data['title'],
                'standfirst':    data.get('standfirst', '')[:500],
                'body_md':       data.get('body_md', ''),
                'body_html':     body_html,
                'word_count':    wc,
                'read_time':     rt,
                'published_at':  data.get('published_at', date.today()),
                'series':        series,
                'imported_from': self.source_name,
                'is_published':  True,
            }

            if existing and overwrite:
                for k, v in defaults.items():
                    setattr(existing, k, v)
                if not dry_run:
                    existing.save()
                imported.append(existing)
            elif not existing:
                slug = self._unique_slug(data['title'])
                if not dry_run:
                    article = Article.objects.create(slug=slug, source_url=url, **defaults)
                else:
                    article = Article(slug=slug, source_url=url, **defaults)
                imported.append(article)

        return imported, skipped

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        return re.sub(r'[\s_-]+', '-', text)[:100]

    def _unique_slug(self, title: str) -> str:
        base = self._slugify(title)
        slug = base
        n = 1
        while Article.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug
