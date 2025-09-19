const fs = require('fs');
const path = require('path');

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

// Создаем иконки для каждого размера
sizes.forEach(size => {
  const iconContent = createIcon(size);
  const filename = `icon-${size}x${size}.png`;
  const filepath = path.join(iconDir, filename);
  
  // В реальном проекте здесь должна быть конвертация SVG в PNG
  // Для демонстрации создаем SVG файлы
  const svgFilename = `icon-${size}x${size}.svg`;
  const svgFilepath = path.join(iconDir, svgFilename);
  
  fs.writeFileSync(svgFilepath, iconContent);
  console.log(`Создана иконка: ${svgFilename}`);
});

// Создаем favicon
const faviconContent = createIcon(32);
fs.writeFileSync(path.join(iconDir, 'favicon.svg'), faviconContent);

// Создаем apple-touch-icon
const appleTouchIcon = createIcon(180);
fs.writeFileSync(path.join(iconDir, 'apple-touch-icon.svg'), appleTouchIcon);

console.log('Иконки созданы успешно!');
console.log('Примечание: В реальном проекте используйте библиотеки типа sharp или jimp для конвертации SVG в PNG');
