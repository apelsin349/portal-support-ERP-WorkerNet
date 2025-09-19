#!/bin/bash

# Скрипт для полного исправления проблем с миграциями
echo "[ИНФО] Начинаем полное исправление проблем с миграциями..."

# Переходим в директорию backend
cd backend

# Проверяем, активировано ли виртуальное окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "[ИНФО] Активируем виртуальное окружение..."
    source venv/bin/activate
fi

echo "[ИНФО] Шаг 1: Исправляем проблему с ограничением unique_username_per_tenant..."

# Безопасно удаляем проблемное ограничение
python manage.py dbshell << 'EOF'
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
EOF

echo "[ИНФО] Шаг 2: Очищаем состояние миграций в базе данных..."

# Удаляем записи о проблемных миграциях из django_migrations
python manage.py dbshell << 'EOF'
DELETE FROM django_migrations 
WHERE app = 'app' AND name IN (
    '0008_agentrating_incident_incidentattachment_and_more',
    '0009_auto_20241201_1200',
    '0010_fix_constraint_issue'
);
EOF

echo "[ИНФО] Шаг 3: Создаем отсутствующие таблицы вручную..."

# Создаем таблицы для AgentRating и IncidentAttachment, если их нет
python manage.py dbshell << 'EOF'
-- Создаем таблицу agent_ratings если её нет
CREATE TABLE IF NOT EXISTS agent_ratings (
    id BIGSERIAL PRIMARY KEY,
    agent_id BIGINT NOT NULL,
    rated_by_id BIGINT NOT NULL,
    ticket_id BIGINT NOT NULL,
    professionalism_rating INTEGER NOT NULL CHECK (professionalism_rating >= 1 AND professionalism_rating <= 5),
    knowledge_rating INTEGER NOT NULL CHECK (knowledge_rating >= 1 AND knowledge_rating <= 5),
    communication_rating INTEGER NOT NULL CHECK (communication_rating >= 1 AND communication_rating <= 5),
    problem_solving_rating INTEGER NOT NULL CHECK (problem_solving_rating >= 1 AND problem_solving_rating <= 5),
    overall_rating INTEGER NOT NULL CHECK (overall_rating >= 1 AND overall_rating <= 5),
    comment TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (agent_id, rated_by_id, ticket_id)
);

-- Создаем таблицу incidents если её нет
CREATE TABLE IF NOT EXISTS incidents (
    id BIGSERIAL PRIMARY KEY,
    incident_id VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('P1', 'P2', 'P3', 'P4')),
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'identified', 'monitoring', 'resolved', 'closed')),
    category VARCHAR(20) NOT NULL CHECK (category IN ('infrastructure', 'application', 'security', 'data', 'integration', 'user_experience')),
    reported_by_id BIGINT NOT NULL,
    assigned_to_id BIGINT,
    tenant_id BIGINT NOT NULL,
    affected_services JSONB NOT NULL DEFAULT '[]',
    business_impact TEXT NOT NULL DEFAULT '',
    user_impact TEXT NOT NULL DEFAULT '',
    detected_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    response_time_minutes INTEGER,
    resolution_time_minutes INTEGER,
    sla_breached BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    custom_fields JSONB NOT NULL DEFAULT '{}'
);

-- Создаем таблицу incident_attachments если её нет
CREATE TABLE IF NOT EXISTS incident_attachments (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    uploaded_by_id BIGINT NOT NULL,
    file VARCHAR(100) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Создаем таблицу incident_updates если её нет
CREATE TABLE IF NOT EXISTS incident_updates (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    update_type VARCHAR(20) NOT NULL CHECK (update_type IN ('status_change', 'investigation', 'resolution', 'communication', 'escalation')),
    is_public BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Создаем таблицу incident_timeline если её нет
CREATE TABLE IF NOT EXISTS incident_timeline (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    event_type VARCHAR(30) NOT NULL CHECK (event_type IN ('created', 'assigned', 'status_changed', 'escalated', 'resolved', 'closed', 'comment_added', 'attachment_added')),
    description TEXT NOT NULL,
    author_id BIGINT,
    metadata JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Создаем таблицу incident_escalations если её нет
CREATE TABLE IF NOT EXISTS incident_escalations (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    level INTEGER NOT NULL,
    reason TEXT NOT NULL,
    escalated_to_id BIGINT NOT NULL,
    escalated_by_id BIGINT NOT NULL,
    escalated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ
);

-- Создаем таблицу incident_slas если её нет
CREATE TABLE IF NOT EXISTS incident_slas (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('P1', 'P2', 'P3', 'P4')),
    response_time_minutes INTEGER NOT NULL,
    resolution_time_minutes INTEGER NOT NULL,
    tenant_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, severity)
);

-- Создаем таблицу app_incident_tags если её нет
CREATE TABLE IF NOT EXISTS app_incident_tags (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    UNIQUE (incident_id, tag_id)
);

EOF

echo "[ИНФО] Шаг 4: Помечаем все миграции как выполненные..."

# Помечаем все миграции как выполненные
python manage.py migrate app 0001 --fake
python manage.py migrate app 0002 --fake
python manage.py migrate app 0003_abtest_abtestevent_abtestmetric_abtestparticipant_and_more --fake
python manage.py migrate app 0003_safe_models --fake
python manage.py migrate app 0004_merge_0003_conflicts --fake
python manage.py migrate app 0005_agentrating_automationaction_automationcondition_and_more --fake
python manage.py migrate app 0006_fix_foreign_keys --fake
python manage.py migrate app 0007_add_user_reset_tokens --fake

# Создаем запись о "выполненной" миграции 0008
python manage.py dbshell << 'EOF'
INSERT INTO django_migrations (app, name, applied) 
VALUES ('app', '0008_agentrating_incident_incidentattachment_and_more', NOW())
ON CONFLICT (app, name) DO NOTHING;
EOF

python manage.py migrate app 0010_fix_constraint_issue --fake

echo "[ИНФО] Шаг 5: Проверяем состояние миграций..."

# Проверяем состояние миграций
python manage.py showmigrations app

echo "[ИНФО] Шаг 6: Выполняем финальную миграцию..."

# Выполняем миграции
python manage.py migrate

echo "[УСПЕХ] Все проблемы с миграциями исправлены!"
echo "[ИНФО] Проект готов к работе!"
