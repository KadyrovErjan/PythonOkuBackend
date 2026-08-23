from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pythonoku', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='video_urls',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='userprogress',
            name='video_parts_progress',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
