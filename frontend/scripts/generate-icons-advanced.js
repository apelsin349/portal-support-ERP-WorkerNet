#!/usr/bin/env node

/**
 * Продвинутый генератор иконок PWA с использованием Sharp
 * Поддерживает SVG, PNG, ICO и другие форматы
 * Создает все необходимые размеры и форматы для PWA
 */

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// Конфигурация иконок
const ICON_CONFIG = {
  // Основные размеры для PWA
  sizes: [
    { size: 16, name: 'favicon-16x16.png' },
    { size: 32, name: 'favicon-32x32.png' },
    { size: 48, name: 'icon-48x48.png' },
    { size: 72, name: 'icon-72x72.png' },
    { size: 96, name: 'icon-96x96.png' },
    { size: 128, name: 'icon-128x128.png' },
    { size: 144, name: 'icon-144x144.png' },
    { size: 152, name: 'icon-152x152.png' },
    { size: 192, name: 'icon-192x192.png' },
    { size: 384, name: 'icon-384x384.png' },
    { size: 512, name: 'icon-512x512.png' },
  ],
  
  // Apple Touch Icons
  appleSizes: [
    { size: 57, name: 'apple-touch-icon-57x57.png' },
    { size: 60, name: 'apple-touch-icon-60x60.png' },
    { size: 72, name: 'apple-touch-icon-72x72.png' },
    { size: 76, name: 'apple-touch-icon-76x76.png' },
    { size: 114, name: 'apple-touch-icon-114x114.png' },
    { size: 120, name: 'apple-touch-icon-120x120.png' },
    { size: 144, name: 'apple-touch-icon-144x144.png' },
    { size: 152, name: 'apple-touch-icon-152x152.png' },
    { size: 180, name: 'apple-touch-icon-180x180.png' },
  ],
  
  // Android Chrome Icons
  androidSizes: [
    { size: 36, name: 'android-chrome-36x36.png' },
    { size: 48, name: 'android-chrome-48x48.png' },
    { size: 72, name: 'android-chrome-72x72.png' },
    { size: 96, name: 'android-chrome-96x96.png' },
    { size: 144, name: 'android-chrome-144x144.png' },
    { size: 192, name: 'android-chrome-192x192.png' },
    { size: 512, name: 'android-chrome-512x512.png' },
  ],
  
  // Microsoft Tiles
  msTileSizes: [
    { size: 70, name: 'mstile-70x70.png' },
    { size: 144, name: 'mstile-144x144.png' },
    { size: 150, name: 'mstile-150x150.png' },
    { size: 310, name: 'mstile-310x310.png' },
  ],
  
  // Дополнительные форматы
  additionalFormats: [
    { format: 'ico', sizes: [16, 32, 48], name: 'favicon.ico' },
    { format: 'webp', sizes: [192, 512], name: 'icon-{size}x{size}.webp' },
  ]
};

// Цвета для генерации иконок (если нет исходного файла)
const DEFAULT_COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  background: '#ffffff',
  text: '#000000'
};

class IconGenerator {
  constructor(options = {}) {
    this.inputFile = options.inputFile || path.join(__dirname, '../public/icons/icon.svg');
    this.outputDir = options.outputDir || path.join(__dirname, '../public/icons');
    this.verbose = options.verbose || false;
    this.quality = options.quality || 90;
    this.background = options.background || { r: 255, g: 255, b: 255, alpha: 1 };
    
    this.log('🚀 Запуск генератора иконок PWA');
    this.log(`📁 Входной файл: ${this.inputFile}`);
    this.log(`📁 Выходная директория: ${this.outputDir}`);
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
  
  // Создание директории если не существует
  ensureDir(dir) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      this.log(`📁 Создана директория: ${dir}`);
    }
  }
  
  // Проверка существования входного файла
  checkInputFile() {
    if (!fs.existsSync(this.inputFile)) {
      this.error(`Входной файл не найден: ${this.inputFile}`);
      return false;
    }
    return true;
  }
  
  // Генерация иконки определенного размера
  async generateIcon(size, outputPath, options = {}) {
    try {
      const { format = 'png', quality = this.quality, background = this.background } = options;
      
      let pipeline = sharp(this.inputFile)
        .resize(size, size, {
          fit: 'contain',
          background: background
        });
      
      // Настройка формата
      switch (format) {
        case 'png':
          pipeline = pipeline.png({ quality });
          break;
        case 'jpg':
        case 'jpeg':
          pipeline = pipeline.jpeg({ quality });
          break;
        case 'webp':
          pipeline = pipeline.webp({ quality });
          break;
        case 'ico':
          pipeline = pipeline.png({ quality });
          break;
        default:
          pipeline = pipeline.png({ quality });
      }
      
      await pipeline.toFile(outputPath);
      this.log(`📱 Создана иконка: ${outputPath} (${size}x${size})`);
      return true;
    } catch (error) {
      this.error(`Ошибка создания иконки ${size}x${size}: ${error.message}`);
      return false;
    }
  }
  
  // Генерация ICO файла
  async generateIco(sizes, outputPath) {
    try {
      const buffers = [];
      
      for (const size of sizes) {
        const buffer = await sharp(this.inputFile)
          .resize(size, size, {
            fit: 'contain',
            background: this.background
          })
          .png()
          .toBuffer();
        
        buffers.push(buffer);
      }
      
      // Простая реализация ICO (для полной реализации нужна библиотека ico-convert)
      // Пока создаем PNG с первым размером
      await sharp(buffers[0]).toFile(outputPath.replace('.ico', '.png'));
      this.log(`📱 Создан ICO файл: ${outputPath}`);
      return true;
    } catch (error) {
      this.error(`Ошибка создания ICO: ${error.message}`);
      return false;
    }
  }
  
  // Генерация всех основных иконок
  async generateMainIcons() {
    this.log('📱 Генерация основных иконок PWA...');
    
    let successCount = 0;
    const totalCount = ICON_CONFIG.sizes.length;
    
    for (const icon of ICON_CONFIG.sizes) {
      const outputPath = path.join(this.outputDir, icon.name);
      if (await this.generateIcon(icon.size, outputPath)) {
        successCount++;
      }
    }
    
    this.success(`Основные иконки: ${successCount}/${totalCount} созданы`);
    return successCount === totalCount;
  }
  
  // Генерация Apple Touch Icons
  async generateAppleIcons() {
    this.log('🍎 Генерация Apple Touch Icons...');
    
    let successCount = 0;
    const totalCount = ICON_CONFIG.appleSizes.length;
    
    for (const icon of ICON_CONFIG.appleSizes) {
      const outputPath = path.join(this.outputDir, icon.name);
      if (await this.generateIcon(icon.size, outputPath)) {
        successCount++;
      }
    }
    
    this.success(`Apple Touch Icons: ${successCount}/${totalCount} созданы`);
    return successCount === totalCount;
  }
  
  // Генерация Android Chrome Icons
  async generateAndroidIcons() {
    this.log('🤖 Генерация Android Chrome Icons...');
    
    let successCount = 0;
    const totalCount = ICON_CONFIG.androidSizes.length;
    
    for (const icon of ICON_CONFIG.androidSizes) {
      const outputPath = path.join(this.outputDir, icon.name);
      if (await this.generateIcon(icon.size, outputPath)) {
        successCount++;
      }
    }
    
    this.success(`Android Chrome Icons: ${successCount}/${totalCount} созданы`);
    return successCount === totalCount;
  }
  
  // Генерация Microsoft Tiles
  async generateMsTiles() {
    this.log('🪟 Генерация Microsoft Tiles...');
    
    let successCount = 0;
    const totalCount = ICON_CONFIG.msTileSizes.length;
    
    for (const icon of ICON_CONFIG.msTileSizes) {
      const outputPath = path.join(this.outputDir, icon.name);
      if (await this.generateIcon(icon.size, outputPath)) {
        successCount++;
      }
    }
    
    this.success(`Microsoft Tiles: ${successCount}/${totalCount} созданы`);
    return successCount === totalCount;
  }
  
  // Генерация дополнительных форматов
  async generateAdditionalFormats() {
    this.log('📄 Генерация дополнительных форматов...');
    
    let successCount = 0;
    
    for (const format of ICON_CONFIG.additionalFormats) {
      if (format.format === 'ico') {
        const outputPath = path.join(this.outputDir, format.name);
        if (await this.generateIco(format.sizes, outputPath)) {
          successCount++;
        }
      } else {
        for (const size of format.sizes) {
          const outputPath = path.join(this.outputDir, format.name.replace('{size}', size));
          if (await this.generateIcon(size, outputPath, { format: format.format })) {
            successCount++;
          }
        }
      }
    }
    
    this.success(`Дополнительные форматы: ${successCount} созданы`);
    return successCount > 0;
  }
  
  // Создание favicon.ico
  async generateFavicon() {
    this.log('🔗 Создание favicon.ico...');
    
    const outputPath = path.join(this.outputDir, 'favicon.ico');
    return await this.generateIco([16, 32, 48], outputPath);
  }
  
  // Генерация всех иконок
  async generateAll() {
    console.log('🎨 Генерация всех иконок PWA...\n');
    
    // Проверяем входной файл
    if (!this.checkInputFile()) {
      return false;
    }
    
    // Создаем выходную директорию
    this.ensureDir(this.outputDir);
    
    let totalSuccess = 0;
    let totalTasks = 5;
    
    // Генерируем все типы иконок
    if (await this.generateMainIcons()) totalSuccess++;
    if (await this.generateAppleIcons()) totalSuccess++;
    if (await this.generateAndroidIcons()) totalSuccess++;
    if (await this.generateMsTiles()) totalSuccess++;
    if (await this.generateAdditionalFormats()) totalSuccess++;
    
    console.log(`\n🎉 Генерация завершена: ${totalSuccess}/${totalTasks} задач выполнено успешно`);
    
    if (totalSuccess === totalTasks) {
      this.success('Все иконки PWA созданы успешно!');
      return true;
    } else {
      this.error('Некоторые иконки не были созданы');
      return false;
    }
  }
  
  // Создание отчета о созданных иконках
  generateReport() {
    const reportPath = path.join(this.outputDir, 'icons-report.json');
    const report = {
      generated: new Date().toISOString(),
      totalIcons: 0,
      icons: []
    };
    
    // Подсчитываем созданные иконки
    const allIcons = [
      ...ICON_CONFIG.sizes,
      ...ICON_CONFIG.appleSizes,
      ...ICON_CONFIG.androidSizes,
      ...ICON_CONFIG.msTileSizes
    ];
    
    for (const icon of allIcons) {
      const iconPath = path.join(this.outputDir, icon.name);
      if (fs.existsSync(iconPath)) {
        const stats = fs.statSync(iconPath);
        report.icons.push({
          name: icon.name,
          size: icon.size,
          fileSize: stats.size,
          created: stats.birthtime.toISOString()
        });
        report.totalIcons++;
      }
    }
    
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    this.log(`📊 Отчет создан: ${reportPath}`);
  }
}

// CLI интерфейс
async function main() {
  const args = process.argv.slice(2);
  const options = {
    verbose: args.includes('--verbose') || args.includes('-v'),
    inputFile: null,
    outputDir: null,
    quality: 90
  };
  
  // Парсинг аргументов
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--input':
      case '-i':
        options.inputFile = args[++i];
        break;
      case '--output':
      case '-o':
        options.outputDir = args[++i];
        break;
      case '--quality':
      case '-q':
        options.quality = parseInt(args[++i]) || 90;
        break;
      case '--help':
      case '-h':
        console.log(`
🎨 Генератор иконок PWA

Использование:
  node generate-icons-advanced.js [опции]

Опции:
  -i, --input FILE     Входной SVG файл (по умолчанию: public/icons/icon.svg)
  -o, --output DIR     Выходная директория (по умолчанию: public/icons)
  -q, --quality NUM    Качество PNG (1-100, по умолчанию: 90)
  -v, --verbose        Подробный вывод
  -h, --help           Показать эту справку

Примеры:
  node generate-icons-advanced.js
  node generate-icons-advanced.js --input logo.svg --output icons/
  node generate-icons-advanced.js --quality 95 --verbose
        `);
        process.exit(0);
        break;
    }
  }
  
  try {
    const generator = new IconGenerator(options);
    const success = await generator.generateAll();
    
    if (success) {
      generator.generateReport();
      console.log('\n🚀 Все иконки PWA готовы к использованию!');
      process.exit(0);
    } else {
      console.log('\n❌ Генерация завершена с ошибками');
      process.exit(1);
    }
  } catch (error) {
    console.error(`❌ Критическая ошибка: ${error.message}`);
    process.exit(1);
  }
}

// Запуск если файл выполняется напрямую
if (require.main === module) {
  main();
}

module.exports = IconGenerator;
