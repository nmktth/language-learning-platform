# Generated manually for achievements and richer exercise types.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_lesson_content_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='type',
            field=models.CharField(
                choices=[
                    ('multiple_choice', 'Multiple choice'),
                    ('translation', 'Translation'),
                    ('matching_pairs', 'Matching pairs'),
                    ('listening', 'Listening'),
                ],
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=64, unique=True)),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='bronze', max_length=32)),
                ('medal_tier', models.CharField(default='bronze', max_length=32)),
                ('condition_type', models.CharField(choices=[('xp', 'XP reached'), ('streak', 'Streak reached'), ('correct_answers', 'Correct answers count'), ('completed_lessons', 'Completed lessons count')], max_length=32)),
                ('threshold', models.PositiveIntegerField(default=1)),
                ('xp_reward', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('awarded_at', models.DateTimeField(auto_now_add=True)),
                ('progress_snapshot', models.JSONField(blank=True, default=dict)),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='core.achievement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-awarded_at'],
                'unique_together': {('user', 'achievement')},
            },
        ),
    ]
