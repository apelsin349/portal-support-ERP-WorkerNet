const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Попытка импорта Sharp
let sharp;
try {
  sharp = require('sharp');
  console.log('✅ Sharp найден - используется качественная конвертация');
} catch (error) {
  console.log('⚠️  Sharp не найден - используется базовая генерация');
  console.log('💡 Для лучшего качества установите: npm install sharp');
}

// Функция для проверки, нужно ли генерировать иконки
function needsIconGeneration() {
  const iconDir = path.join(__dirname, '../public/icons');
  const hashFile = path.join(iconDir, '.icons_hash');
  const sourceIcon = path.join(__dirname, '../public/icons/icon.svg');
  
  // Если директория иконок не существует, нужно генерировать
  if (!fs.existsSync(iconDir)) {
    return true;
  }
  
  // Если хеш-файл не существует, нужно генерировать
  if (!fs.existsSync(hashFile)) {
    return true;
  }
  
  // Если исходная иконка не существует, используем базовую генерацию
  if (!fs.existsSync(sourceIcon)) {
    return true;
  }
  
  try {
    // Читаем сохраненный хеш
    const savedHash = fs.readFileSync(hashFile, 'utf8').trim();
    
    // Вычисляем текущий хеш исходной иконки
    const sourceIconData = fs.readFileSync(sourceIcon);
    const currentHash = crypto.createHash('sha256').update(sourceIconData).digest('hex');
    
    // Если хеши не совпадают, нужно генерировать
    return savedHash !== currentHash;
  } catch (error) {
    // Если произошла ошибка, генерируем иконки
    return true;
  }
}

// Функция для сохранения хеша
function saveIconHash() {
  const iconDir = path.join(__dirname, '../public/icons');
  const hashFile = path.join(iconDir, '.icons_hash');
  const sourceIcon = path.join(__dirname, '../public/icons/icon.svg');
  
  try {
    if (fs.existsSync(sourceIcon)) {
      const sourceIconData = fs.readFileSync(sourceIcon);
      const hash = crypto.createHash('sha256').update(sourceIconData).digest('hex');
      fs.writeFileSync(hashFile, hash);
    }
  } catch (error) {
    // Игнорируем ошибки сохранения хеша
  }
}

// Создаем простые PNG иконки разных размеров
const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
const iconDir = path.join(__dirname, '../public/icons');

// Создаем директорию для иконок
if (!fs.existsSync(iconDir)) {
  fs.mkdirSync(iconDir, { recursive: true });
}

// Создаем простые иконки в виде base64 PNG
const createIcon = (size) => {
  // Это упрощенная версия - в реальном проекте лучше использовать библиотеки для генерации иконок
  const canvas = `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#1976d2;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#42a5f5;stop-opacity:1" />
        </linearGradient>
      </defs>
      
      <!-- Фон -->
      <rect width="${size}" height="${size}" rx="${size * 0.125}" fill="url(#gradient)"/>
      
      <!-- Иконка поддержки -->
      <g transform="translate(${size * 0.25}, ${size * 0.25})">
        <!-- Голова -->
        <circle cx="${size * 0.25}" cy="${size * 0.1875}" r="${size * 0.0625}" fill="white" opacity="0.9"/>
        
        <!-- Тело -->
        <rect x="${size * 0.1875}" y="${size * 0.25}" width="${size * 0.125}" height="${size * 0.15625}" rx="${size * 0.015625}" fill="white" opacity="0.9"/>
        
        <!-- Руки -->
        <rect x="${size * 0.15625}" y="${size * 0.2734375}" width="${size * 0.03125}" height="${size * 0.078125}" rx="${size * 0.015625}" fill="white" opacity="0.9"/>
        <rect x="${size * 0.34375}" y="${size * 0.2734375}" width="${size * 0.03125}" height="${size * 0.078125}" rx="${size * 0.015625}" fill="white" opacity="0.9"/>
        
        <!-- Ноги -->
        <rect x="${size * 0.2109375}" y="${size * 0.40625}" width="${size * 0.03125}" height="${size * 0.0625}" rx="${size * 0.015625}" fill="white" opacity="0.9"/>
        <rect x="${size * 0.2578125}" y="${size * 0.40625}" width="${size * 0.03125}" height="${size * 0.0625}" rx="${size * 0.015625}" fill="white" opacity="0.9"/>
        
        <!-- Знак вопроса -->
        <text x="${size * 0.25}" y="${size * 0.21484375}" text-anchor="middle" font-family="Arial, sans-serif" font-size="${size * 0.046875}" font-weight="bold" fill="#1976d2">?</text>
      </g>
    </svg>
  `;
  
  return canvas;
};

// Функция конвертации SVG в PNG с использованием Sharp
async function svgToPng(svgContent, size, outputPath) {
  if (sharp) {
    try {
      await sharp(Buffer.from(svgContent))
        .resize(size, size, {
          fit: 'contain',
          background: { r: 255, g: 255, b: 255, alpha: 1 }
        })
        .png({ quality: 90 })
        .toFile(outputPath);
      
      console.log(`✅ Создана PNG иконка: ${path.basename(outputPath)} (${size}x${size})`);
      return true;
    } catch (error) {
      console.error(`❌ Ошибка создания PNG ${outputPath}: ${error.message}`);
      return false;
    }
  } else {
    // Fallback: создаем SVG файл
    const svgFilename = outputPath.replace('.png', '.svg');
    fs.writeFileSync(svgFilename, svgContent);
    console.log(`📱 Создана SVG иконка: ${path.basename(svgFilename)} (${size}x${size})`);
    return true;
  }
}

// Создаем иконки для каждого размера
async function generateIcons() {
  let successCount = 0;
  const totalCount = sizes.length;
  
  for (const size of sizes) {
    const iconContent = createIcon(size);
    const filename = `icon-${size}x${size}.png`;
    const filepath = path.join(iconDir, filename);
    
    if (await svgToPng(iconContent, size, filepath)) {
      successCount++;
    }
  }
  
  console.log(`\n🎉 Генерация завершена: ${successCount}/${totalCount} иконок создано`);
  return successCount === totalCount;
}

// Создаем favicon и apple-touch-icon
async function generateSpecialIcons() {
  // Favicon
  const faviconContent = createIcon(32);
  const faviconPath = path.join(iconDir, 'favicon.png');
  await svgToPng(faviconContent, 32, faviconPath);
  
  // Apple Touch Icon
  const appleTouchIcon = createIcon(180);
  const appleTouchPath = path.join(iconDir, 'apple-touch-icon.png');
  await svgToPng(appleTouchIcon, 180, appleTouchPath);
}

// Основная функция
async function main() {
  // Проверяем, нужно ли генерировать иконки
  if (!needsIconGeneration()) {
    console.log('✅ Иконки PWA актуальны, пропускаем генерацию');
    return;
  }
  
  console.log('🎨 Генерация иконок PWA...\n');
  
  // Генерируем основные иконки
  const mainSuccess = await generateIcons();
  
  // Генерируем специальные иконки
  await generateSpecialIcons();
  
  if (mainSuccess) {
    console.log('\n✅ Все иконки PWA созданы успешно!');
    if (sharp) {
      console.log('🚀 Использована качественная конвертация с Sharp');
    } else {
      console.log('💡 Для лучшего качества установите: npm install sharp');
    }
    
    // Сохраняем хеш после успешной генерации
    saveIconHash();
  } else {
    console.log('\n⚠️  Некоторые иконки не были созданы');
  }
}

// Запуск генерации
if (require.main === module) {
  main().catch(error => {
    console.error(`❌ Критическая ошибка: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { generateIcons, generateSpecialIcons, svgToPng };
