from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_ticket_models"),
    ]

    operations = [
        # ChatMessage
        migrations.RunSQL(
            sql=(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id BIGSERIAL PRIMARY KEY,
                    room_name VARCHAR(200) NOT NULL,
                    sender_id BIGINT NOT NULL,
                    content TEXT NOT NULL,
                    message_type VARCHAR(20) NOT NULL DEFAULT 'text',
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS chat_messages_room_name_timestamp_idx
                    ON chat_messages (room_name, timestamp);
                """
            ),
            reverse_sql=(
                """
                DROP INDEX IF EXISTS chat_messages_room_name_timestamp_idx;
                DROP TABLE IF EXISTS chat_messages;
                """
            ),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="ChatMessage",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("room_name", models.CharField(max_length=200, verbose_name="Комната")),
                        ("content", models.TextField(verbose_name="Содержимое")),
                        ("message_type", models.CharField(default="text", max_length=20, verbose_name="Тип сообщения")),
                        ("timestamp", models.DateTimeField(auto_now_add=True, verbose_name="Время")),
                        ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chat_messages", to="app.user", verbose_name="Отправитель")),
                    ],
                    options={
                        "verbose_name": "Сообщение чата",
                        "verbose_name_plural": "Сообщения чата",
                        "db_table": "chat_messages",
                    },
                ),
            ],
            database_operations=[],
        ),

        # Notification
        migrations.RunSQL(
            sql=(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    type VARCHAR(20) NOT NULL DEFAULT 'system',
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL DEFAULT '',
                    payload JSONB NOT NULL DEFAULT '{}',
                    is_read BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS notifications_is_read_idx ON notifications (is_read);
                CREATE INDEX IF NOT EXISTS notifications_created_at_idx ON notifications (created_at);
                """
            ),
            reverse_sql=(
                """
                DROP INDEX IF EXISTS notifications_is_read_idx;
                DROP INDEX IF EXISTS notifications_created_at_idx;
                DROP TABLE IF EXISTS notifications;
                """
            ),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Notification",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("type", models.CharField(choices=[("ticket", "Тикет"), ("system", "Система"), ("chat", "Чат")], default="system", max_length=20, verbose_name="Тип")),
                        ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                        ("message", models.TextField(blank=True, verbose_name="Сообщение")),
                        ("payload", models.JSONField(default=dict, verbose_name="Данные")),
                        ("is_read", models.BooleanField(db_index=True, default=False, verbose_name="Прочитано")),
                        ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Создано")),
                        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="app.user", verbose_name="Пользователь")),
                    ],
                    options={
                        "verbose_name": "Уведомление",
                        "verbose_name_plural": "Уведомления",
                        "db_table": "notifications",
                        "ordering": ["-created_at"],
                    },
                ),
            ],
            database_operations=[],
        ),

        # A/B testing tables
        migrations.RunSQL(
            sql=(
                """
                CREATE TABLE IF NOT EXISTS feature_flags (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    rollout_percentage INTEGER NOT NULL DEFAULT 0,
                    start_date TIMESTAMPTZ,
                    end_date TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS ab_tests (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status VARCHAR(20) NOT NULL DEFAULT 'draft',
                    traffic_allocation INTEGER NOT NULL DEFAULT 50,
                    start_date TIMESTAMPTZ NOT NULL,
                    end_date TIMESTAMPTZ NOT NULL,
                    created_by_id BIGINT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS ab_test_variants (
                    id BIGSERIAL PRIMARY KEY,
                    ab_test_id BIGINT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    weight INTEGER NOT NULL DEFAULT 50,
                    config JSONB NOT NULL DEFAULT '{}',
                    participants_count INTEGER NOT NULL DEFAULT 0,
                    conversions_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS ab_test_participants (
                    id BIGSERIAL PRIMARY KEY,
                    ab_test_id BIGINT NOT NULL,
                    variant_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    is_converted BOOLEAN NOT NULL DEFAULT FALSE,
                    converted_at TIMESTAMPTZ,
                    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (ab_test_id, user_id)
                );

                CREATE TABLE IF NOT EXISTS ab_test_events (
                    id BIGSERIAL PRIMARY KEY,
                    participant_id BIGINT NOT NULL,
                    event_type VARCHAR(20) NOT NULL,
                    event_name VARCHAR(100) NOT NULL,
                    properties JSONB NOT NULL DEFAULT '{}',
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    ip_address INET,
                    user_agent TEXT NOT NULL DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS ab_test_metrics (
                    id BIGSERIAL PRIMARY KEY,
                    ab_test_id BIGINT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    metric_type VARCHAR(30) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    target_value DOUBLE PRECISION,
                    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (ab_test_id, name)
                );

                -- M2M feature_flags.target_tenants
                CREATE TABLE IF NOT EXISTS app_featureflag_target_tenants (
                    id BIGSERIAL PRIMARY KEY,
                    featureflag_id BIGINT NOT NULL,
                    tenant_id BIGINT NOT NULL,
                    UNIQUE (featureflag_id, tenant_id)
                );

                -- M2M ab_tests.target_tenants
                CREATE TABLE IF NOT EXISTS app_abtest_target_tenants (
                    id BIGSERIAL PRIMARY KEY,
                    abtest_id BIGINT NOT NULL,
                    tenant_id BIGINT NOT NULL,
                    UNIQUE (abtest_id, tenant_id)
                );
                """
            ),
            reverse_sql=(
                """
                DROP TABLE IF EXISTS app_abtest_target_tenants;
                DROP TABLE IF EXISTS app_featureflag_target_tenants;
                DROP TABLE IF EXISTS ab_test_metrics;
                DROP TABLE IF EXISTS ab_test_events;
                DROP TABLE IF EXISTS ab_test_participants;
                DROP TABLE IF EXISTS ab_test_variants;
                DROP TABLE IF EXISTS ab_tests;
                DROP TABLE IF EXISTS feature_flags;
                """
            ),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="FeatureFlag",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=100, unique=True, verbose_name="Название")),
                        ("description", models.TextField(blank=True, verbose_name="Описание")),
                        ("is_enabled", models.BooleanField(default=False, verbose_name="Включен")),
                        ("rollout_percentage", models.PositiveIntegerField(default=0, verbose_name="Процент пользователей")),
                        ("start_date", models.DateTimeField(blank=True, null=True, verbose_name="Дата начала")),
                        ("end_date", models.DateTimeField(blank=True, null=True, verbose_name="Дата окончания")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                        ("target_tenants", models.ManyToManyField(blank=True, related_name="feature_flags", to="app.tenant", verbose_name="Целевые арендаторы")),
                    ],
                    options={
                        "verbose_name": "Feature Flag",
                        "verbose_name_plural": "Feature Flags",
                        "db_table": "feature_flags",
                    },
                ),
                migrations.CreateModel(
                    name="ABTest",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=200, verbose_name="Название")),
                        ("description", models.TextField(blank=True, verbose_name="Описание")),
                        ("status", models.CharField(choices=[("draft", "Черновик"), ("active", "Активен"), ("paused", "Приостановлен"), ("completed", "Завершен"), ("cancelled", "Отменен")], default="draft", max_length=20, verbose_name="Статус")),
                        ("traffic_allocation", models.PositiveIntegerField(default=50, verbose_name="Распределение трафика (%)")),
                        ("start_date", models.DateTimeField(verbose_name="Дата начала")),
                        ("end_date", models.DateTimeField(verbose_name="Дата окончания")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                        ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="created_ab_tests", to="app.user", verbose_name="Создатель")),
                        ("target_tenants", models.ManyToManyField(blank=True, related_name="ab_tests", to="app.tenant", verbose_name="Целевые арендаторы")),
                    ],
                    options={
                        "verbose_name": "A/B Тест",
                        "verbose_name_plural": "A/B Тесты",
                        "db_table": "ab_tests",
                        "ordering": ["-created_at"],
                    },
                ),
                migrations.CreateModel(
                    name="ABTestVariant",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=100, verbose_name="Название")),
                        ("description", models.TextField(blank=True, verbose_name="Описание")),
                        ("weight", models.PositiveIntegerField(default=50, verbose_name="Вес (%)")),
                        ("config", models.JSONField(default=dict, verbose_name="Конфигурация")),
                        ("participants_count", models.PositiveIntegerField(default=0, verbose_name="Участников")),
                        ("conversions_count", models.PositiveIntegerField(default=0, verbose_name="Конверсий")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                        ("ab_test", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="app.abtest", verbose_name="A/B Тест")),
                    ],
                    options={
                        "verbose_name": "Вариант A/B Теста",
                        "verbose_name_plural": "Варианты A/B Тестов",
                        "db_table": "ab_test_variants",
                        "unique_together": {("ab_test", "name")},
                    },
                ),
                migrations.CreateModel(
                    name="ABTestParticipant",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("is_converted", models.BooleanField(default=False, verbose_name="Конвертирован")),
                        ("converted_at", models.DateTimeField(blank=True, null=True, verbose_name="Время конверсии")),
                        ("assigned_at", models.DateTimeField(auto_now_add=True, verbose_name="Назначен")),
                        ("ab_test", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="participants", to="app.abtest", verbose_name="A/B Тест")),
                        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ab_test_participations", to="app.user", verbose_name="Пользователь")),
                        ("variant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="participants", to="app.abtestvariant", verbose_name="Вариант")),
                    ],
                    options={
                        "verbose_name": "Участник A/B Теста",
                        "verbose_name_plural": "Участники A/B Тестов",
                        "db_table": "ab_test_participants",
                        "unique_together": {("ab_test", "user")},
                    },
                ),
                migrations.CreateModel(
                    name="ABTestEvent",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("event_type", models.CharField(max_length=20, verbose_name="Тип события")),
                        ("event_name", models.CharField(max_length=100, verbose_name="Название события")),
                        ("properties", models.JSONField(default=dict, verbose_name="Свойства")),
                        ("timestamp", models.DateTimeField(auto_now_add=True, verbose_name="Время")),
                        ("ip_address", models.GenericIPAddressField(blank=True, null=True, verbose_name="IP адрес")),
                        ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                        ("participant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="app.abtestparticipant", verbose_name="Участник")),
                    ],
                    options={
                        "verbose_name": "Событие A/B Теста",
                        "verbose_name_plural": "События A/B Тестов",
                        "db_table": "ab_test_events",
                        "ordering": ["-timestamp"],
                    },
                ),
                migrations.CreateModel(
                    name="ABTestMetric",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=100, verbose_name="Название")),
                        ("metric_type", models.CharField(max_length=30, verbose_name="Тип метрики")),
                        ("description", models.TextField(blank=True, verbose_name="Описание")),
                        ("target_value", models.FloatField(blank=True, null=True, verbose_name="Целевое значение")),
                        ("is_primary", models.BooleanField(default=False, verbose_name="Основная метрика")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                        ("ab_test", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="metrics", to="app.abtest", verbose_name="A/B Тест")),
                    ],
                    options={
                        "verbose_name": "Метрика A/B Теста",
                        "verbose_name_plural": "Метрики A/B Тестов",
                        "db_table": "ab_test_metrics",
                        "unique_together": {("ab_test", "name")},
                    },
                ),
            ],
            database_operations=[],
        ),
    ]


