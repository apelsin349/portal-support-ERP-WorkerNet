const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from src directory
app.use(express.static(path.join(__dirname, 'src')));

// Basic health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'portal-support-frontend' });
});

// Serve main page
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Portal Support ERP WorkerNet</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 4px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Portal Support ERP WorkerNet</h1>
            <div class="status">
                <h3>Frontend Service Status</h3>
                <p>✅ Frontend service is running</p>
                <p>📦 Package.json found and loaded</p>
                <p>🔧 Ready for development</p>
            </div>
            <p>This is a placeholder frontend for the Portal Support ERP WorkerNet system.</p>
        </div>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`Frontend server running on port ${PORT}`);
});
