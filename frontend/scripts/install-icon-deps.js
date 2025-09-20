#!/usr/bin/env node

/**
 * Скрипт установки зависимостей для генерации иконок
 * Устанавливает Sharp и другие необходимые библиотеки
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Зависимости для генерации иконок
const ICON_DEPENDENCIES = [
  'sharp@^0.32.6',
  'jimp@^0.22.10',
  'svg2png@^4.1.1'
];

// Опциональные зависимости для расширенной функциональности
const OPTIONAL_DEPENDENCIES = [
  'puppeteer@^21.5.2',
  'ico-convert@^1.0.0'
];

class IconDependenciesInstaller {
  constructor(options = {}) {
    this.verbose = options.verbose || false;
    this.installOptional = options.installOptional || false;
    this.packageManager = this.detectPackageManager();
  }
  
  log(message) {
    if (this.verbose) {
      console.log(message);
    }
  }
  
  error(message) {
    console.error(`❌ ${message}`);
  }
  
  success(message) {
    console.log(`✅ ${message}`);
  }
  
  // Определение менеджера пакетов
  detectPackageManager() {
    if (fs.existsSync('package-lock.json')) {
      return 'npm';
    } else if (fs.existsSync('yarn.lock')) {
      return 'yarn';
    } else if (fs.existsSync('pnpm-lock.yaml')) {
      return 'pnpm';
    } else {
      return 'npm'; // по умолчанию
    }
  }
  
  // Проверка существования зависимости
  isDependencyInstalled(dependency) {
    const packageName = dependency.split('@')[0];
    const packageJsonPath = path.join(process.cwd(), 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
      return false;
    }
    
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const allDeps = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies
    };
    
    return packageName in allDeps;
  }
  
  // Установка зависимости
  installDependency(dependency) {
    try {
      const packageName = dependency.split('@')[0];
      
      if (this.isDependencyInstalled(packageName)) {
        this.log(`📦 ${packageName} уже установлен`);
        return true;
      }
      
      this.log(`📦 Устанавливаем ${dependency}...`);
      
      let command;
      switch (this.packageManager) {
        case 'yarn':
          command = `yarn add ${dependency} --dev`;
          break;
        case 'pnpm':
          command = `pnpm add ${dependency} --save-dev`;
          break;
        default:
          command = `npm install ${dependency} --save-dev`;
      }
      
      execSync(command, { 
        stdio: this.verbose ? 'inherit' : 'pipe',
        cwd: process.cwd()
      });
      
      this.success(`${packageName} установлен успешно`);
      return true;
    } catch (error) {
      this.error(`Ошибка установки ${dependency}: ${error.message}`);
      return false;
    }
  }
  
  // Установка всех основных зависимостей
  async installMainDependencies() {
    console.log('📦 Установка основных зависимостей для генерации иконок...\n');
    
    let successCount = 0;
    const totalCount = ICON_DEPENDENCIES.length;
    
    for (const dependency of ICON_DEPENDENCIES) {
      if (this.installDependency(dependency)) {
        successCount++;
      }
    }
    
    console.log(`\n📊 Основные зависимости: ${successCount}/${totalCount} установлены`);
    return successCount === totalCount;
  }
  
  // Установка опциональных зависимостей
  async installOptionalDependencies() {
    if (!this.installOptional) {
      this.log('⏭️  Пропускаем установку опциональных зависимостей');
      return true;
    }
    
    console.log('\n📦 Установка опциональных зависимостей...\n');
    
    let successCount = 0;
    const totalCount = OPTIONAL_DEPENDENCIES.length;
    
    for (const dependency of OPTIONAL_DEPENDENCIES) {
      if (this.installDependency(dependency)) {
        successCount++;
      }
    }
    
    console.log(`\n📊 Опциональные зависимости: ${successCount}/${totalCount} установлены`);
    return successCount === totalCount;
  }
  
  // Проверка системных зависимостей для Sharp
  checkSystemDependencies() {
    console.log('\n🔍 Проверка системных зависимостей...');
    
    const platform = process.platform;
    const arch = process.arch;
    
    console.log(`💻 Платформа: ${platform} ${arch}`);
    
    // Sharp требует определенные системные библиотеки
    if (platform === 'linux') {
      console.log('🐧 Linux: Sharp должен работать из коробки');
    } else if (platform === 'darwin') {
      console.log('🍎 macOS: Sharp должен работать из коробки');
    } else if (platform === 'win32') {
      console.log('🪟 Windows: Sharp должен работать из коробки');
    }
    
    return true;
  }
  
  // Тестирование установленных зависимостей
  async testDependencies() {
    console.log('\n🧪 Тестирование установленных зависимостей...\n');
    
    const tests = [
      {
        name: 'Sharp',
        test: () => {
          const sharp = require('sharp');
          return sharp.versions;
        }
      },
      {
        name: 'Jimp',
        test: () => {
          const Jimp = require('jimp');
          return Jimp.version;
        }
      }
    ];
    
    let successCount = 0;
    
    for (const test of tests) {
      try {
        const result = test.test();
        this.success(`${test.name} работает: ${JSON.stringify(result)}`);
        successCount++;
      } catch (error) {
        this.error(`${test.name} не работает: ${error.message}`);
      }
    }
    
    console.log(`\n📊 Тесты: ${successCount}/${tests.length} прошли успешно`);
    return successCount === tests.length;
  }
  
  // Создание отчета об установке
  createInstallationReport() {
    const reportPath = path.join(process.cwd(), 'icon-deps-report.json');
    const report = {
      installed: new Date().toISOString(),
      packageManager: this.packageManager,
      platform: process.platform,
      arch: process.arch,
      dependencies: {
        main: ICON_DEPENDENCIES,
        optional: OPTIONAL_DEPENDENCIES
      },
      installedDeps: []
    };
    
    // Проверяем установленные зависимости
    for (const dep of [...ICON_DEPENDENCIES, ...OPTIONAL_DEPENDENCIES]) {
      const packageName = dep.split('@')[0];
      if (this.isDependencyInstalled(packageName)) {
        report.installedDeps.push(packageName);
      }
    }
    
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    this.log(`📊 Отчет создан: ${reportPath}`);
  }
  
  // Основная функция установки
  async install() {
    console.log('🚀 Установка зависимостей для генерации иконок PWA...\n');
    
    // Проверяем системные зависимости
    this.checkSystemDependencies();
    
    // Устанавливаем основные зависимости
    const mainSuccess = await this.installMainDependencies();
    
    // Устанавливаем опциональные зависимости
    const optionalSuccess = await this.installOptionalDependencies();
    
    // Тестируем установленные зависимости
    const testSuccess = await this.testDependencies();
    
    // Создаем отчет
    this.createInstallationReport();
    
    // Итоговый результат
    if (mainSuccess && testSuccess) {
      this.success('\n🎉 Все зависимости установлены успешно!');
      console.log('\n📋 Следующие шаги:');
      console.log('1. Запустите: npm run generate-icons');
      console.log('2. Или для расширенной генерации: npm run generate-icons-advanced');
      console.log('3. Проверьте созданные иконки в public/icons/');
      return true;
    } else {
      this.error('\n❌ Установка завершена с ошибками');
      console.log('\n🔧 Рекомендации:');
      console.log('1. Проверьте подключение к интернету');
      console.log('2. Убедитесь, что у вас установлен Node.js 18+');
      console.log('3. Попробуйте очистить кэш: npm cache clean --force');
      return false;
    }
  }
}

// CLI интерфейс
async function main() {
  const args = process.argv.slice(2);
  const options = {
    verbose: args.includes('--verbose') || args.includes('-v'),
    installOptional: args.includes('--optional') || args.includes('-o')
  };
  
  // Парсинг аргументов
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--help':
      case '-h':
        console.log(`
📦 Установщик зависимостей для генерации иконок PWA

Использование:
  node install-icon-deps.js [опции]

Опции:
  -v, --verbose        Подробный вывод
  -o, --optional       Установить опциональные зависимости
  -h, --help           Показать эту справку

Примеры:
  node install-icon-deps.js
  node install-icon-deps.js --verbose --optional
        `);
        process.exit(0);
        break;
    }
  }
  
  try {
    const installer = new IconDependenciesInstaller(options);
    const success = await installer.install();
    process.exit(success ? 0 : 1);
  } catch (error) {
    console.error(`❌ Критическая ошибка: ${error.message}`);
    process.exit(1);
  }
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
  main();
}

module.exports = IconDependenciesInstaller;
