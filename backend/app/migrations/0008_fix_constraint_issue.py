from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_add_user_reset_tokens"),
    ]

    operations = [
        # Удаляем ограничение только если оно существует
        migrations.RunSQL(
            sql="""
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'unique_username_per_tenant' 
                        AND table_name = 'users'
                    ) THEN
                        ALTER TABLE users DROP CONSTRAINT unique_username_per_tenant;
                    END IF;
                END $$;
            """,
            reverse_sql="-- No reverse operation needed"
        ),
    ]
