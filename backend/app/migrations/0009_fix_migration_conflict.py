from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_add_user_reset_tokens"),
    ]

    operations = [
        # Эта миграция исправляет конфликт с 0008_agentrating_incident_incidentattachment_and_more
        # Безопасно удаляем ограничение только если оно существует
        migrations.RunSQL(
            sql="""
                DO $$ 
                BEGIN
                    -- Проверяем существование ограничения и удаляем его
                    IF EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'unique_username_per_tenant' 
                        AND table_name = 'users'
                        AND table_schema = 'public'
                    ) THEN
                        ALTER TABLE users DROP CONSTRAINT unique_username_per_tenant;
                        RAISE NOTICE 'Constraint unique_username_per_tenant dropped successfully';
                    ELSE
                        RAISE NOTICE 'Constraint unique_username_per_tenant does not exist, skipping';
                    END IF;
                END $$;
            """,
            reverse_sql="""
                -- Обратная операция - создаем ограничение если его нет
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'unique_username_per_tenant' 
                        AND table_name = 'users'
                        AND table_schema = 'public'
                    ) THEN
                        ALTER TABLE users ADD CONSTRAINT unique_username_per_tenant 
                        UNIQUE (username, tenant_id);
                        RAISE NOTICE 'Constraint unique_username_per_tenant created successfully';
                    END IF;
                END $$;
            """
        ),
    ]
