import csv
from django.core.management.base import BaseCommand
from collection.models import Consumer, Account

class Command(BaseCommand):
    help = 'Ingest consumer and account data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to ingest.')

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                consumer, created = Consumer.objects.get_or_create(
                    ssn=row['ssn'],
                    defaults={
                        'name': row['consumer name'],
                        'address': row['consumer address'],
                    }
                )

                account, created = Account.objects.get_or_create(
                    client_reference=row['client reference no'],
                    defaults={
                        'balance': row['balance'],
                        'status': row['status'],
                    }
                )
                account.consumers.add(consumer)

        self.stdout.write(self.style.SUCCESS('Successfully ingested data from "%s"' % options['csv_file']))
