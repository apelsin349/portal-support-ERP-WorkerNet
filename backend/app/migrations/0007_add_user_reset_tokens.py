from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_fix_foreign_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_token',
            field=models.CharField(max_length=32, null=True, blank=True, verbose_name='Токен сброса'),
        ),
        migrations.AddField(
            model_name='user',
            name='reset_token_expires',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Истечение токена'),
        ),
        # Add index for reset token lookups
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS idx_users_reset_token ON users(reset_token) WHERE reset_token IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_users_reset_token;"
        ),
    ]
