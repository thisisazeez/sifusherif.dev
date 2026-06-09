from django.core.management.base import BaseCommand, CommandError
from writing.models import Series


class Command(BaseCommand):
    help = 'Import articles from Medium into the portfolio database.'

    def add_arguments(self, parser):
        parser.add_argument(
            'source', choices=['medium'],
            help='Platform to import from.',
        )
        parser.add_argument(
            '--username', default='sifusherif',
            help='Platform username (default: sifusherif).',
        )
        parser.add_argument(
            '--series', dest='series_slug', default=None,
            help='Slug of the Series to assign imported articles to.',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Fetch and display what would be imported without writing to the database.',
        )
        parser.add_argument(
            '--overwrite', action='store_true',
            help='Re-import and overwrite articles that were previously imported.',
        )

    def handle(self, *args, **options):
        series = None
        if options['series_slug']:
            try:
                series = Series.objects.get(slug=options['series_slug'])
            except Series.DoesNotExist:
                raise CommandError(
                    f"Series with slug '{options['series_slug']}' does not exist. "
                    f"Create it in the admin first."
                )

        if options['source'] == 'medium':
            from writing.importers.medium import MediumImporter
            importer = MediumImporter(username=options['username'])
        else:
            raise CommandError(f"Unknown source: {options['source']}")

        self.stdout.write(
            f"Fetching articles from Medium (@{options['username']})…"
        )

        try:
            imported, skipped = importer.import_all(
                series=series,
                dry_run=options['dry_run'],
                overwrite=options['overwrite'],
            )
        except RuntimeError as exc:
            raise CommandError(str(exc))

        prefix = '[DRY RUN] ' if options['dry_run'] else ''

        if options['dry_run']:
            self.stdout.write('\nArticles that would be imported:')
            for a in imported:
                self.stdout.write(f'  • {a.title} ({a.published_at})')
        else:
            for a in imported:
                self.stdout.write(f'  ✓ {a.title}')

        self.stdout.write(self.style.SUCCESS(
            f'\n{prefix}Imported: {len(imported)}  |  Skipped (already exist): {len(skipped)}'
        ))

        if skipped and not options['overwrite']:
            self.stdout.write(
                self.style.WARNING(
                    'Use --overwrite to re-import skipped articles.'
                )
            )
