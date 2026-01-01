from django.core.management.base import BaseCommand
from Dashboard.models import Category, Item, Transaction
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generate sample categories, items, and transactions for testing sales chart.'

    def handle(self, *args, **options):
        # Create categories
        categories = []
        for cname in ['Electronics', 'Clothing', 'Food', 'Books', 'Others']:
            cat, _ = Category.objects.get_or_create(name=cname)
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS('Categories created.'))

        # Create items
        items = []
        for i in range(10):
            item, _ = Item.objects.get_or_create(
                sn=f'SN{i+1:04d}',
                name=f'Item {i+1}',
                category=random.choice(categories),
                stock=random.randint(1, 50),
                reorder_level=random.randint(5, 15),
                price=random.uniform(10, 200)
            )
            items.append(item)
        self.stdout.write(self.style.SUCCESS('Items created.'))

        # Create transactions for last 12 months
        now = timezone.now()
        for m in range(12):
            month = (now.month - m - 1) % 12 + 1
            year = now.year if now.month - m > 0 else now.year - 1
            for _ in range(random.randint(5, 15)):
                day = random.randint(1, 28)
                dt = timezone.datetime(year, month, day, tzinfo=timezone.get_current_timezone())
                Transaction.objects.create(
                    item=random.choice(items),
                    amount=random.uniform(20, 500),
                    created_at=dt
                )
        self.stdout.write(self.style.SUCCESS('Sample transactions created for last 12 months.'))

        # Create transactions for last 5 years
        for y in range(now.year-4, now.year+1):
            for _ in range(random.randint(10, 30)):
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                dt = timezone.datetime(y, month, day, tzinfo=timezone.get_current_timezone())
                Transaction.objects.create(
                    item=random.choice(items),
                    amount=random.uniform(20, 500),
                    created_at=dt
                )
        self.stdout.write(self.style.SUCCESS('Sample transactions created for last 5 years.'))
