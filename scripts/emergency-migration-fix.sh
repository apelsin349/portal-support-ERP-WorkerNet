#!/bin/bash

# Экстренное исправление проблемы с миграциями
echo "[ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ] Начинаем исправление проблемы с миграциями..."

cd backend

# Активируем виртуальное окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "[ИНФО] Активируем виртуальное окружение..."
    source venv/bin/activate
fi

echo "[ИНФО] Шаг 1: Исправляем ограничение unique_username_per_tenant..."
python manage.py dbshell << 'EOF'
DO $$ 
BEGIN
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

echo "[ИНФО] Шаг 2: Удаляем проблемные записи миграций..."
python manage.py dbshell << 'EOF'
DELETE FROM django_migrations 
WHERE app = 'app' AND (name LIKE '%0008%' OR name LIKE '%0009%');
EOF

echo "[ИНФО] Шаг 3: Создаем отсутствующие таблицы..."
python manage.py dbshell << 'EOF'
-- Создаем таблицу agent_ratings
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

-- Создаем таблицу incidents
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

-- Создаем таблицу incident_attachments
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

-- Создаем таблицу incident_updates
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

-- Создаем таблицу incident_timeline
CREATE TABLE IF NOT EXISTS incident_timeline (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    event_type VARCHAR(30) NOT NULL CHECK (event_type IN ('created', 'assigned', 'status_changed', 'escalated', 'resolved', 'closed', 'comment_added', 'attachment_added')),
    description TEXT NOT NULL,
    author_id BIGINT,
    metadata JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Создаем таблицу incident_escalations
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

-- Создаем таблицу incident_slas
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

-- Создаем таблицу app_incident_tags
CREATE TABLE IF NOT EXISTS app_incident_tags (
    id BIGSERIAL PRIMARY KEY,
    incident_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    UNIQUE (incident_id, tag_id)
);
EOF

echo "[ИНФО] Шаг 4: Очищаем все проблемные записи миграций..."
python manage.py dbshell << 'EOF'
-- Удаляем все записи миграций приложения app, кроме базовой
DELETE FROM django_migrations 
WHERE app = 'app' AND name != '0001_initial';
EOF

echo "[ИНФО] Шаг 5: Сбрасываем состояние миграций..."
python manage.py migrate app 0001 --fake

echo "[ИНФО] Шаг 6: Создаем новые миграции..."
python manage.py makemigrations app

echo "[ИНФО] Шаг 7: Выполняем финальные миграции..."
python manage.py migrate

echo "[УСПЕХ] Экстренное исправление завершено!"
echo "[ИНФО] Проверяем состояние миграций..."
python manage.py showmigrations app

echo "[ИНФО] Проект готов к работе!"
