const express = require('express');
const router = express.Router();

// Import controllers
const authController = require('../controllers/authController');
const ticketController = require('../controllers/ticketController');
const knowledgeController = require('../controllers/knowledgeController');
const notificationController = require('../controllers/notificationController');
const chatController = require('../controllers/chatController');
const slaController = require('../controllers/slaController');
const abTestingController = require('../controllers/abTestingController');
const incidentController = require('../controllers/incidentController');
const templateController = require('../controllers/templateController');
const ratingController = require('../controllers/ratingController');
const automationController = require('../controllers/automationController');
const performanceController = require('../controllers/performanceController');

// API Documentation
router.get('/docs', (req, res) => {
  res.json({
    title: 'WorkerNet Portal API Documentation',
    version: '1.0.0',
    description: 'API endpoints for Portal Support ERP WorkerNet',
    endpoints: {
      auth: {
        base: '/api/auth',
        endpoints: [
          'POST /register - User registration',
          'POST /login - User login',
          'POST /logout - User logout',
          'GET /profile - Get user profile',
          'PUT /profile - Update user profile',
          'POST /change-password - Change password',
          'POST /reset-password - Reset password',
          'POST /verify-email - Verify email'
        ]
      },
      tickets: {
        base: '/api/tickets',
        endpoints: [
          'GET / - List tickets',
          'POST / - Create ticket',
          'GET /:id - Get ticket details',
          'PUT /:id - Update ticket',
          'DELETE /:id - Delete ticket',
          'POST /:id/assign - Assign ticket',
          'POST /:id/comment - Add comment',
          'POST /:id/attachment - Add attachment'
        ]
      },
      knowledge: {
        base: '/api/knowledge',
        endpoints: [
          'GET /articles - List articles',
          'POST /articles - Create article',
          'GET /articles/:id - Get article details',
          'PUT /articles/:id - Update article',
          'DELETE /articles/:id - Delete article',
          'GET /categories - List categories',
          'POST /search - Search articles'
        ]
      },
      notifications: {
        base: '/api/notifications',
        endpoints: [
          'GET / - List notifications',
          'POST / - Create notification',
          'GET /:id - Get notification details',
          'PUT /:id - Update notification',
          'DELETE /:id - Delete notification',
          'POST /mark-read - Mark as read',
          'GET /stats - Get statistics'
        ]
      },
      chat: {
        base: '/api/chat',
        endpoints: [
          'GET /messages - List messages',
          'POST /messages - Send message',
          'GET /conversations - List conversations',
          'GET /conversation - Get conversation',
          'POST /search - Search messages'
        ]
      },
      sla: {
        base: '/api/sla',
        endpoints: [
          'GET /sla - List SLA rules',
          'POST /sla - Create SLA rule',
          'GET /sla/:id - Get SLA details',
          'PUT /sla/:id - Update SLA rule',
          'DELETE /sla/:id - Delete SLA rule',
          'GET /stats - Get SLA statistics',
          'GET /violations - Get SLA violations'
        ]
      },
      abTesting: {
        base: '/api/ab-testing',
        endpoints: [
          'GET /feature-flags - List feature flags',
          'POST /feature-flags - Create feature flag',
          'GET /tests - List A/B tests',
          'POST /tests - Create A/B test',
          'GET /tests/:id - Get test details',
          'POST /tests/:id/assign - Assign user to test'
        ]
      },
      incidents: {
        base: '/api/incidents',
        endpoints: [
          'GET / - List incidents',
          'POST / - Create incident',
          'GET /:id - Get incident details',
          'PUT /:id - Update incident',
          'DELETE /:id - Delete incident',
          'POST /:id/escalate - Escalate incident',
          'POST /:id/resolve - Resolve incident'
        ]
      },
      templates: {
        base: '/api/templates',
        endpoints: [
          'GET /templates - List templates',
          'POST /templates - Create template',
          'GET /templates/:id - Get template details',
          'PUT /templates/:id - Update template',
          'DELETE /templates/:id - Delete template',
          'POST /templates/:id/use - Use template'
        ]
      },
      ratings: {
        base: '/api/ratings',
        endpoints: [
          'GET /ticket-ratings - List ticket ratings',
          'POST /ticket-ratings - Create ticket rating',
          'GET /agent-ratings - List agent ratings',
          'POST /agent-ratings - Create agent rating',
          'GET /surveys - List rating surveys',
          'POST /surveys - Create rating survey'
        ]
      },
      automation: {
        base: '/api/automation',
        endpoints: [
          'GET /rules - List automation rules',
          'POST /rules - Create automation rule',
          'GET /rules/:id - Get rule details',
          'PUT /rules/:id - Update rule',
          'DELETE /rules/:id - Delete rule',
          'POST /rules/:id/execute - Execute rule'
        ]
      },
      performance: {
        base: '/api/performance',
        endpoints: [
          'GET /metrics - List performance metrics',
          'POST /metrics - Create performance metric',
          'GET /alerts - List performance alerts',
          'GET /dashboards - List performance dashboards',
          'GET /reports - List performance reports'
        ]
      }
    }
  });
});

// Authentication routes
router.use('/auth', authController);

// Ticket management routes
router.use('/tickets', ticketController);

// Knowledge base routes
router.use('/knowledge', knowledgeController);

// Notification routes
router.use('/notifications', notificationController);

// Chat routes
router.use('/chat', chatController);

// SLA routes
router.use('/sla', slaController);

// A/B Testing routes
router.use('/ab-testing', abTestingController);

// Incident management routes
router.use('/incidents', incidentController);

// Template routes
router.use('/templates', templateController);

// Rating routes
router.use('/ratings', ratingController);

// Automation routes
router.use('/automation', automationController);

// Performance monitoring routes
router.use('/performance', performanceController);

module.exports = router;
