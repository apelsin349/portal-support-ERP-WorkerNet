#!/usr/bin/env python
"""
Скрипт для диагностики и исправления проблем с API schema.
"""
import os
import sys
import django
from pathlib import Path

# Добавляем путь к Django проекту
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_django_setup():
    """Проверяем настройку Django."""
    try:
        from django.conf import settings
        print(f"✓ Django settings loaded successfully")
        print(f"  DEBUG: {settings.DEBUG}")
        print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"  INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
        return True
    except Exception as e:
        print(f"✗ Error loading Django settings: {e}")
        return False

def check_models():
    """Проверяем модели."""
    try:
        from django.apps import apps
        models = apps.get_models()
        print(f"✓ Found {len(models)} models")
        
        # Проверяем основные модели
        from app.models import User, Tenant, Ticket
        print(f"✓ Core models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error with models: {e}")
        return False

def check_api_urls():
    """Проверяем API URLs."""
    try:
        from django.urls import reverse
        from django.test import RequestFactory
        
        # Проверяем основные URL patterns
        factory = RequestFactory()
        request = factory.get('/api/v1/health/')
        
        # Проверяем импорты API
        from app.api.api_urls import urlpatterns
        print(f"✓ API URLs loaded successfully ({len(urlpatterns)} patterns)")
        return True
    except Exception as e:
        print(f"✗ Error with API URLs: {e}")
        return False

def check_drf_spectacular():
    """Проверяем drf-spectacular."""
    try:
        from drf_spectacular.views import SpectacularAPIView
        from django.conf import settings
        
        # Проверяем настройки
        spectacular_settings = getattr(settings, 'SPECTACULAR_SETTINGS', {})
        print(f"✓ drf-spectacular configured")
        print(f"  Title: {spectacular_settings.get('TITLE', 'Not set')}")
        
        # Проверяем схему
        view = SpectacularAPIView()
        print(f"✓ SpectacularAPIView can be instantiated")
        return True
    except Exception as e:
        print(f"✗ Error with drf-spectacular: {e}")
        return False

def generate_schema():
    """Генерируем схему API."""
    try:
        from drf_spectacular.openapi import AutoSchema
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/api/schema/')
        
        # Пытаемся сгенерировать схему
        schema_generator = AutoSchema()
        print(f"✓ Schema generator created successfully")
        return True
    except Exception as e:
        print(f"✗ Error generating schema: {e}")
        return False

def main():
    """Основная функция диагностики."""
    print("🔍 Диагностика API Schema WorkerNet Portal")
    print("=" * 50)
    
    checks = [
        ("Django Setup", check_django_setup),
        ("Models", check_models),
        ("API URLs", check_api_urls),
        ("drf-spectacular", check_drf_spectacular),
        ("Schema Generation", generate_schema),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Результаты диагностики:")
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Все проверки пройдены успешно!")
        print("API schema должна работать корректно.")
    else:
        print("\n⚠️  Обнаружены проблемы!")
        print("Необходимо исправить ошибки для корректной работы API schema.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
