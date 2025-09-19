const express = require('express');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// API Routes
app.use('/api', require('./routes/api'));

// Main routes
app.get('/', (req, res) => {
  res.json({
    message: 'Фронтенд портала WorkerNet',
    version: '1.0.0',
    status: 'работает',
    endpoints: {
      health: '/health',
      api: '/api',
      docs: '/api/docs'
    }
  });
});

app.get('/health', (req, res) => {
  res.json({
    status: 'работает',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Произошла ошибка!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Внутренняя ошибка сервера'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Не найдено',
    message: `Маршрут ${req.method} ${req.path} не найден`
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Фронтенд сервер запущен на порту ${PORT}`);
  console.log(`📊 Проверка состояния: http://localhost:${PORT}/health`);
  console.log(`🔗 API эндпоинты: http://localhost:${PORT}/api`);
  console.log(`🌐 Внешний доступ: http://10.0.21.221:${PORT}`);
});
