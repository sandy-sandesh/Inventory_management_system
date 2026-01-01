# Generated migration to remove unique=True from Item.sku field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0003_item_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='sku',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
