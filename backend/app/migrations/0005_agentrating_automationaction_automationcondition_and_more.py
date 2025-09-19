from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_merge_0003_conflicts"),
    ]

    operations = [
        # Knowledge base tables
        migrations.RunSQL(
            sql=(
                """
                CREATE TABLE IF NOT EXISTS knowledge_categories (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    parent_id BIGINT,
                    tenant_id BIGINT NOT NULL,
                    "order" INTEGER NOT NULL DEFAULT 0,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (name, tenant_id)
                );

                CREATE TABLE IF NOT EXISTS knowledge_articles (
                    id BIGSERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    slug VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    excerpt TEXT NOT NULL DEFAULT '',
                    category_id BIGINT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'draft',
                    author_id BIGINT NOT NULL,
                    tenant_id BIGINT NOT NULL,
                    meta_title VARCHAR(255) NOT NULL DEFAULT '',
                    meta_description TEXT NOT NULL DEFAULT '',
                    keywords VARCHAR(500) NOT NULL DEFAULT '',
                    view_count INTEGER NOT NULL DEFAULT 0,
                    helpful_count INTEGER NOT NULL DEFAULT 0,
                    not_helpful_count INTEGER NOT NULL DEFAULT 0,
                    published_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    custom_fields JSONB NOT NULL DEFAULT '{}',
                    UNIQUE (slug, tenant_id)
                );

                CREATE TABLE IF NOT EXISTS knowledge_article_attachments (
                    id BIGSERIAL PRIMARY KEY,
                    article_id BIGINT NOT NULL,
                    file VARCHAR(100) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    file_size BIGINT NOT NULL,
                    mime_type VARCHAR(100) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS knowledge_article_ratings (
                    id BIGSERIAL PRIMARY KEY,
                    article_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (article_id, user_id)
                );

                CREATE TABLE IF NOT EXISTS knowledge_article_views (
                    id BIGSERIAL PRIMARY KEY,
                    article_id BIGINT NOT NULL,
                    user_id BIGINT,
                    ip_address INET NOT NULL,
                    user_agent TEXT NOT NULL DEFAULT '',
                    viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS knowledge_searches (
                    id BIGSERIAL PRIMARY KEY,
                    query VARCHAR(255) NOT NULL,
                    user_id BIGINT,
                    tenant_id BIGINT NOT NULL,
                    results_count INTEGER NOT NULL DEFAULT 0,
                    searched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                -- M2M knowledge_articles.tags
                CREATE TABLE IF NOT EXISTS app_knowledgearticle_tags (
                    id BIGSERIAL PRIMARY KEY,
                    knowledgearticle_id BIGINT NOT NULL,
                    tag_id BIGINT NOT NULL,
                    UNIQUE (knowledgearticle_id, tag_id)
                );

                -- Automation tables
                CREATE TABLE IF NOT EXISTS automation_rules (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    rule_type VARCHAR(20) NOT NULL,
                    trigger_type VARCHAR(20) NOT NULL,
                    conditions JSONB NOT NULL DEFAULT '{}',
                    actions JSONB NOT NULL DEFAULT '{}',
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    priority INTEGER NOT NULL DEFAULT 0,
                    tenant_id BIGINT NOT NULL,
                    created_by_id BIGINT NOT NULL,
                    execution_count INTEGER NOT NULL DEFAULT 0,
                    last_executed_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS automation_executions (
                    id BIGSERIAL PRIMARY KEY,
                    rule_id BIGINT NOT NULL,
                    ticket_id BIGINT,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    result JSONB NOT NULL DEFAULT '{}',
                    error_message TEXT NOT NULL DEFAULT '',
                    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    completed_at TIMESTAMPTZ
                );

                CREATE TABLE IF NOT EXISTS automation_conditions (
                    id BIGSERIAL PRIMARY KEY,
                    rule_id BIGINT NOT NULL,
                    condition_type VARCHAR(20) NOT NULL,
                    field_name VARCHAR(100) NOT NULL DEFAULT '',
                    operator VARCHAR(20) NOT NULL DEFAULT '',
                    value TEXT NOT NULL DEFAULT '',
                    logical_operator VARCHAR(10) NOT NULL DEFAULT 'AND',
                    "order" INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS automation_actions (
                    id BIGSERIAL PRIMARY KEY,
                    rule_id BIGINT NOT NULL,
                    action_type VARCHAR(20) NOT NULL,
                    parameters JSONB NOT NULL DEFAULT '{}',
                    "order" INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS automation_templates (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    template_data JSONB NOT NULL DEFAULT '{}',
                    category VARCHAR(100) NOT NULL DEFAULT '',
                    is_public BOOLEAN NOT NULL DEFAULT TRUE,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_by_id BIGINT NOT NULL,
                    usage_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS automation_schedules (
                    id BIGSERIAL PRIMARY KEY,
                    rule_id BIGINT NOT NULL UNIQUE,
                    frequency VARCHAR(20) NOT NULL,
                    cron_expression VARCHAR(100) NOT NULL DEFAULT '',
                    start_time TIME NOT NULL,
                    end_time TIME,
                    weekdays JSONB NOT NULL DEFAULT '[]',
                    month_days JSONB NOT NULL DEFAULT '[]',
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            ),
            reverse_sql=(
                """
                DROP TABLE IF EXISTS automation_schedules;
                DROP TABLE IF EXISTS automation_templates;
                DROP TABLE IF EXISTS automation_actions;
                DROP TABLE IF EXISTS automation_conditions;
                DROP TABLE IF EXISTS automation_executions;
                DROP TABLE IF EXISTS automation_rules;
                DROP TABLE IF EXISTS app_knowledgearticle_tags;
                DROP TABLE IF EXISTS knowledge_searches;
                DROP TABLE IF EXISTS knowledge_article_views;
                DROP TABLE IF EXISTS knowledge_article_ratings;
                DROP TABLE IF EXISTS knowledge_article_attachments;
                DROP TABLE IF EXISTS knowledge_articles;
                DROP TABLE IF EXISTS knowledge_categories;
                """
            ),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Knowledge models
                migrations.CreateModel(
                    name="KnowledgeCategory",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=100, verbose_name="Name")),
                        ("description", models.TextField(blank=True, verbose_name="Description")),
                        ("order", models.PositiveIntegerField(default=0, verbose_name="Order")),
                        ("is_active", models.BooleanField(default=True, verbose_name="Is Active")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                        ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="app.knowledgecategory", verbose_name="Parent Category")),
                        ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="knowledge_categories", to="app.tenant", verbose_name="Tenant")),
                    ],
                    options={
                        "verbose_name": "Knowledge Category",
                        "verbose_name_plural": "Knowledge Categories",
                        "db_table": "knowledge_categories",
                        "ordering": ["order", "name"],
                        "unique_together": {("name", "tenant")},
                    },
                ),
                migrations.CreateModel(
                    name="KnowledgeArticle",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("title", models.CharField(max_length=255, verbose_name="Title")),
                        ("slug", models.SlugField(verbose_name="Slug")),
                        ("content", models.TextField(verbose_name="Content")),
                        ("excerpt", models.TextField(blank=True, verbose_name="Excerpt")),
                        ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=20, verbose_name="Status")),
                        ("meta_title", models.CharField(blank=True, max_length=255, verbose_name="Meta Title")),
                        ("meta_description", models.TextField(blank=True, verbose_name="Meta Description")),
                        ("keywords", models.CharField(blank=True, max_length=500, verbose_name="Keywords")),
                        ("view_count", models.PositiveIntegerField(default=0, verbose_name="View Count")),
                        ("helpful_count", models.PositiveIntegerField(default=0, verbose_name="Helpful Count")),
                        ("not_helpful_count", models.PositiveIntegerField(default=0, verbose_name="Not Helpful Count")),
                        ("published_at", models.DateTimeField(blank=True, null=True, verbose_name="Published At")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                        ("custom_fields", models.JSONField(default=dict, verbose_name="Custom Fields")),
                        ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="knowledge_articles", to="app.user", verbose_name="Author")),
                        ("category", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="articles", to="app.knowledgecategory", verbose_name="Category")),
                        ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="knowledge_articles", to="app.tenant", verbose_name="Tenant")),
                        ("tags", models.ManyToManyField(blank=True, related_name="knowledge_articles", to="app.tag", verbose_name="Tags")),
                    ],
                    options={
                        "verbose_name": "Knowledge Article",
                        "verbose_name_plural": "Knowledge Articles",
                        "db_table": "knowledge_articles",
                        "ordering": ["-published_at", "-created_at"],
                        "unique_together": {("slug", "tenant")},
                    },
                ),
                migrations.CreateModel(
                    name="KnowledgeArticleAttachment",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("file", models.FileField(upload_to="knowledge/attachments/", verbose_name="File")),
                        ("filename", models.CharField(max_length=255, verbose_name="Filename")),
                        ("file_size", models.BigIntegerField(verbose_name="File Size")),
                        ("mime_type", models.CharField(max_length=100, verbose_name="MIME Type")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                        ("article", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attachments", to="app.knowledgearticle", verbose_name="Article")),
                    ],
                    options={
                        "verbose_name": "Knowledge Article Attachment",
                        "verbose_name_plural": "Knowledge Article Attachments",
                        "db_table": "knowledge_article_attachments",
                    },
                ),
                migrations.CreateModel(
                    name="KnowledgeArticleRating",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("rating", models.PositiveIntegerField(choices=[(1, "Very Poor"), (2, "Poor"), (3, "Fair"), (4, "Good"), (5, "Excellent")], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="Rating")),
                        ("comment", models.TextField(blank=True, verbose_name="Comment")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                        ("article", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ratings", to="app.knowledgearticle", verbose_name="Article")),
                        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="knowledge_ratings", to="app.user", verbose_name="User")),
                    ],
                    options={
                        "verbose_name": "Knowledge Article Rating",
                        "verbose_name_plural": "Knowledge Article Ratings",
                        "db_table": "knowledge_article_ratings",
                        "unique_together": {("article", "user")},
                    },
                ),
                migrations.CreateModel(
                    name="KnowledgeArticleView",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("ip_address", models.GenericIPAddressField(verbose_name="IP Address")),
                        ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                        ("viewed_at", models.DateTimeField(auto_now_add=True, verbose_name="Viewed At")),
                        ("article", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="views", to="app.knowledgearticle", verbose_name="Article")),
                        ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="knowledge_views", to="app.user", verbose_name="User")),
                    ],
                    options={
                        "verbose_name": "Knowledge Article View",
                        "verbose_name_plural": "Knowledge Article Views",
                        "db_table": "knowledge_article_views",
                        "ordering": ["-viewed_at"],
                    },
                ),
                migrations.CreateModel(
                    name="KnowledgeSearch",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("query", models.CharField(max_length=255, verbose_name="Query")),
                        ("results_count", models.PositiveIntegerField(default=0, verbose_name="Results Count")),
                        ("searched_at", models.DateTimeField(auto_now_add=True, verbose_name="Searched At")),
                        ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="knowledge_searches", to="app.tenant", verbose_name="Tenant")),
                        ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="knowledge_searches", to="app.user", verbose_name="User")),
                    ],
                    options={
                        "verbose_name": "Knowledge Search",
                        "verbose_name_plural": "Knowledge Searches",
                        "db_table": "knowledge_searches",
                        "ordering": ["-searched_at"],
                    },
                ),
                # Automation models
                migrations.CreateModel(
                    name="AutomationRule",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=200, verbose_name="Название")),
                        ("description", models.TextField(blank=True, verbose_name="Описание")),
                        ("rule_type", models.CharField(max_length=20, verbose_name="Тип правила")),
                        ("trigger_type", models.CharField(max_length=20, verbose_name="Тип триггера")),
                        ("conditions", models.JSONField(default=dict, verbose_name="Условия")),
                        ("actions", models.JSONField(default=dict, verbose_name="Действия")),
                        ("is_active", models.BooleanField(default=True, verbose_name="Активно")),
                        ("priority", models.PositiveIntegerField(default=0, verbose_name="Приоритет")),
                        ("execution_count", models.PositiveIntegerField(default=0, verbose_name="Количество выполнений")),
                        ("last_executed_at", models.DateTimeField(blank=True, null=True, verbose_name="Последнее выполнение")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                        ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="created_automation_rules", to="app.user", verbose_name="Создатель")),
                        ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="automation_rules", to="app.tenant", verbose_name="Арендатор")),
                    ],
                    options={
                        "verbose_name": "Правило автоматизации",
                        "verbose_name_plural": "Правила автоматизации",
                        "db_table": "automation_rules",
                        "ordering": ["priority", "-created_at"],
                    },
                ),
                migrations.CreateModel(
                    name="AutomationExecution",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("status", models.CharField(choices=[("pending", "Ожидает"), ("running", "Выполняется"), ("completed", "Завершено"), ("failed", "Ошибка"), ("skipped", "Пропущено")], default="pending", max_length=20, verbose_name="Статус")),
                        ("result", models.JSONField(default=dict, verbose_name="Результат")),
                        ("error_message", models.TextField(blank=True, verbose_name="Сообщение об ошибке")),
                        ("started_at", models.DateTimeField(auto_now_add=True, verbose_name="Начато")),
                        ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Завершено")),
                        ("rule", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="executions", to="app.automationrule", verbose_name="Правило")),
                        ("ticket", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="automation_executions", to="app.ticket", verbose_name="Тикет")),
                    ],
                    options={
                        "verbose_name": "Выполнение правила",
                        "verbose_name_plural": "Выполнения правил",
                        "db_table": "automation_executions",
                        "ordering": ["-started_at"],
                    },
                ),
                migrations.CreateModel(
                    name="AutomationCondition",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("condition_type", models.CharField(max_length=20, verbose_name="Тип условия")),
                        ("field_name", models.CharField(blank=True, max_length=100, verbose_name="Название поля")),
                        ("operator", models.CharField(blank=True, max_length=20, verbose_name="Оператор")),
                        ("value", models.TextField(blank=True, verbose_name="Значение")),
                        ("logical_operator", models.CharField(choices=[("AND", "И"), ("OR", "ИЛИ")], default="AND", max_length=10, verbose_name="Логический оператор")),
                        ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                        ("rule", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rule_conditions", to="app.automationrule", verbose_name="Правило")),
                    ],
                    options={
                        "verbose_name": "Условие правила",
                        "verbose_name_plural": "Условия правил",
                        "db_table": "automation_conditions",
                        "ordering": ["order"],
                    },
                ),
                migrations.CreateModel(
                    name="AutomationAction",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("action_type", models.CharField(max_length=20, verbose_name="Тип действия")),
                        ("parameters", models.JSONField(default=dict, verbose_name="Параметры")),
                        ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                        ("rule", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rule_actions", to="app.automationrule", verbose_name="Правило")),
                    ],
                    options={
                        "verbose_name": "Действие правила",
                        "verbose_name_plural": "Действия правил",
                        "db_table": "automation_actions",
                        "ordering": ["order"],
                    },
                ),
                migrations.CreateModel(
                    name="AutomationTemplate",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("name", models.CharField(max_length=200, verbose_name="Название")),
                        ("description", models.TextField(blank=True, verbose_name="Описание")),
                        ("template_data", models.JSONField(default=dict, verbose_name="Данные шаблона")),
                        ("category", models.CharField(blank=True, max_length=100, verbose_name="Категория")),
                        ("is_public", models.BooleanField(default=True, verbose_name="Публичный")),
                        ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                        ("usage_count", models.PositiveIntegerField(default=0, verbose_name="Количество использований")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                        ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="automation_templates", to="app.user", verbose_name="Создатель")),
                    ],
                    options={
                        "verbose_name": "Шаблон правила",
                        "verbose_name_plural": "Шаблоны правил",
                        "db_table": "automation_templates",
                        "ordering": ["-usage_count", "name"],
                    },
                ),
                migrations.CreateModel(
                    name="AutomationSchedule",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("frequency", models.CharField(max_length=20, verbose_name="Частота")),
                        ("cron_expression", models.CharField(blank=True, max_length=100, verbose_name="Cron выражение")),
                        ("start_time", models.TimeField(verbose_name="Время начала")),
                        ("end_time", models.TimeField(blank=True, null=True, verbose_name="Время окончания")),
                        ("weekdays", models.JSONField(blank=True, default=list, verbose_name="Дни недели")),
                        ("month_days", models.JSONField(blank=True, default=list, verbose_name="Дни месяца")),
                        ("is_active", models.BooleanField(default=True, verbose_name="Активно")),
                        ("timezone", models.CharField(default="UTC", max_length=50, verbose_name="Часовой пояс")),
                        ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                        ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                        ("rule", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="schedule", to="app.automationrule", verbose_name="Правило")),
                    ],
                    options={
                        "verbose_name": "Расписание правила",
                        "verbose_name_plural": "Расписания правил",
                        "db_table": "automation_schedules",
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
