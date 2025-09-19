from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_agentrating_automationaction_automationcondition_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- Add missing foreign key constraints for Knowledge base
                ALTER TABLE knowledge_categories 
                ADD CONSTRAINT fk_knowledge_categories_parent 
                FOREIGN KEY (parent_id) REFERENCES knowledge_categories(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_categories 
                ADD CONSTRAINT fk_knowledge_categories_tenant 
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_articles 
                ADD CONSTRAINT fk_knowledge_articles_category 
                FOREIGN KEY (category_id) REFERENCES knowledge_categories(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_articles 
                ADD CONSTRAINT fk_knowledge_articles_author 
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_articles 
                ADD CONSTRAINT fk_knowledge_articles_tenant 
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_article_attachments 
                ADD CONSTRAINT fk_knowledge_article_attachments_article 
                FOREIGN KEY (article_id) REFERENCES knowledge_articles(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_article_ratings 
                ADD CONSTRAINT fk_knowledge_article_ratings_article 
                FOREIGN KEY (article_id) REFERENCES knowledge_articles(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_article_ratings 
                ADD CONSTRAINT fk_knowledge_article_ratings_user 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_article_views 
                ADD CONSTRAINT fk_knowledge_article_views_article 
                FOREIGN KEY (article_id) REFERENCES knowledge_articles(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_article_views 
                ADD CONSTRAINT fk_knowledge_article_views_user 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

                ALTER TABLE knowledge_searches 
                ADD CONSTRAINT fk_knowledge_searches_tenant 
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;

                ALTER TABLE knowledge_searches 
                ADD CONSTRAINT fk_knowledge_searches_user 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

                ALTER TABLE app_knowledgearticle_tags 
                ADD CONSTRAINT fk_knowledgearticle_tags_article 
                FOREIGN KEY (knowledgearticle_id) REFERENCES knowledge_articles(id) ON DELETE CASCADE;

                ALTER TABLE app_knowledgearticle_tags 
                ADD CONSTRAINT fk_knowledgearticle_tags_tag 
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE;

                -- Add missing foreign key constraints for Automation
                ALTER TABLE automation_rules 
                ADD CONSTRAINT fk_automation_rules_tenant 
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;

                ALTER TABLE automation_rules 
                ADD CONSTRAINT fk_automation_rules_created_by 
                FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE CASCADE;

                ALTER TABLE automation_executions 
                ADD CONSTRAINT fk_automation_executions_rule 
                FOREIGN KEY (rule_id) REFERENCES automation_rules(id) ON DELETE CASCADE;

                ALTER TABLE automation_executions 
                ADD CONSTRAINT fk_automation_executions_ticket 
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE;

                ALTER TABLE automation_conditions 
                ADD CONSTRAINT fk_automation_conditions_rule 
                FOREIGN KEY (rule_id) REFERENCES automation_rules(id) ON DELETE CASCADE;

                ALTER TABLE automation_actions 
                ADD CONSTRAINT fk_automation_actions_rule 
                FOREIGN KEY (rule_id) REFERENCES automation_rules(id) ON DELETE CASCADE;

                ALTER TABLE automation_templates 
                ADD CONSTRAINT fk_automation_templates_created_by 
                FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE CASCADE;

                ALTER TABLE automation_schedules 
                ADD CONSTRAINT fk_automation_schedules_rule 
                FOREIGN KEY (rule_id) REFERENCES automation_rules(id) ON DELETE CASCADE;

                -- Add indexes for better performance
                CREATE INDEX IF NOT EXISTS idx_knowledge_categories_tenant ON knowledge_categories(tenant_id);
                CREATE INDEX IF NOT EXISTS idx_knowledge_categories_parent ON knowledge_categories(parent_id);
                CREATE INDEX IF NOT EXISTS idx_knowledge_articles_category ON knowledge_articles(category_id);
                CREATE INDEX IF NOT EXISTS idx_knowledge_articles_author ON knowledge_articles(author_id);
                CREATE INDEX IF NOT EXISTS idx_knowledge_articles_tenant ON knowledge_articles(tenant_id);
                CREATE INDEX IF NOT EXISTS idx_knowledge_articles_status ON knowledge_articles(status);
                CREATE INDEX IF NOT EXISTS idx_knowledge_articles_published ON knowledge_articles(published_at);
                CREATE INDEX IF NOT EXISTS idx_automation_rules_tenant ON automation_rules(tenant_id);
                CREATE INDEX IF NOT EXISTS idx_automation_rules_active ON automation_rules(is_active);
                CREATE INDEX IF NOT EXISTS idx_automation_executions_rule ON automation_executions(rule_id);
                CREATE INDEX IF NOT EXISTS idx_automation_executions_ticket ON automation_executions(ticket_id);
            """,
            reverse_sql="""
                -- Remove indexes
                DROP INDEX IF EXISTS idx_automation_executions_ticket;
                DROP INDEX IF EXISTS idx_automation_executions_rule;
                DROP INDEX IF EXISTS idx_automation_rules_active;
                DROP INDEX IF EXISTS idx_automation_rules_tenant;
                DROP INDEX IF EXISTS idx_knowledge_articles_published;
                DROP INDEX IF EXISTS idx_knowledge_articles_status;
                DROP INDEX IF EXISTS idx_knowledge_articles_tenant;
                DROP INDEX IF EXISTS idx_knowledge_articles_author;
                DROP INDEX IF EXISTS idx_knowledge_articles_category;
                DROP INDEX IF EXISTS idx_knowledge_categories_parent;
                DROP INDEX IF EXISTS idx_knowledge_categories_tenant;

                -- Remove foreign key constraints
                ALTER TABLE automation_schedules DROP CONSTRAINT IF EXISTS fk_automation_schedules_rule;
                ALTER TABLE automation_templates DROP CONSTRAINT IF EXISTS fk_automation_templates_created_by;
                ALTER TABLE automation_actions DROP CONSTRAINT IF EXISTS fk_automation_actions_rule;
                ALTER TABLE automation_conditions DROP CONSTRAINT IF EXISTS fk_automation_conditions_rule;
                ALTER TABLE automation_executions DROP CONSTRAINT IF EXISTS fk_automation_executions_ticket;
                ALTER TABLE automation_executions DROP CONSTRAINT IF EXISTS fk_automation_executions_rule;
                ALTER TABLE automation_rules DROP CONSTRAINT IF EXISTS fk_automation_rules_created_by;
                ALTER TABLE automation_rules DROP CONSTRAINT IF EXISTS fk_automation_rules_tenant;
                ALTER TABLE app_knowledgearticle_tags DROP CONSTRAINT IF EXISTS fk_knowledgearticle_tags_tag;
                ALTER TABLE app_knowledgearticle_tags DROP CONSTRAINT IF EXISTS fk_knowledgearticle_tags_article;
                ALTER TABLE knowledge_searches DROP CONSTRAINT IF EXISTS fk_knowledge_searches_user;
                ALTER TABLE knowledge_searches DROP CONSTRAINT IF EXISTS fk_knowledge_searches_tenant;
                ALTER TABLE knowledge_article_views DROP CONSTRAINT IF EXISTS fk_knowledge_article_views_user;
                ALTER TABLE knowledge_article_views DROP CONSTRAINT IF EXISTS fk_knowledge_article_views_article;
                ALTER TABLE knowledge_article_ratings DROP CONSTRAINT IF EXISTS fk_knowledge_article_ratings_user;
                ALTER TABLE knowledge_article_ratings DROP CONSTRAINT IF EXISTS fk_knowledge_article_ratings_article;
                ALTER TABLE knowledge_article_attachments DROP CONSTRAINT IF EXISTS fk_knowledge_article_attachments_article;
                ALTER TABLE knowledge_articles DROP CONSTRAINT IF EXISTS fk_knowledge_articles_tenant;
                ALTER TABLE knowledge_articles DROP CONSTRAINT IF EXISTS fk_knowledge_articles_author;
                ALTER TABLE knowledge_articles DROP CONSTRAINT IF EXISTS fk_knowledge_articles_category;
                ALTER TABLE knowledge_categories DROP CONSTRAINT IF EXISTS fk_knowledge_categories_tenant;
                ALTER TABLE knowledge_categories DROP CONSTRAINT IF EXISTS fk_knowledge_categories_parent;
            """
        ),
    ]
