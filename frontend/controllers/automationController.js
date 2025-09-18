const express = require('express');
const router = express.Router();
const axios = require('axios');

// Backend API base URL
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Get authorization header
const getAuthHeaders = (req) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  return { Authorization: `Bearer ${token}` };
};

// Automation Rules

// List rules
router.get('/rules', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/automation/rules/`, {
      headers: getAuthHeaders(req),
      params: req.query,
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get rules', message: error.response?.data?.message || error.message });
  }
});

// Create rule
router.post('/rules', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/rules/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create rule', message: error.response?.data?.message || error.message });
  }
});

// Get rule
router.get('/rules/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/automation/rules/${req.params.id}/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get rule', message: error.response?.data?.message || error.message });
  }
});

// Update rule
router.put('/rules/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/automation/rules/${req.params.id}/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to update rule', message: error.response?.data?.message || error.message });
  }
});

// Delete rule
router.delete('/rules/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/automation/rules/${req.params.id}/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to delete rule', message: error.response?.data?.message || error.message });
  }
});

// Execute rule
router.post('/rules/:id/execute', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/rules/${req.params.id}/execute/`, {}, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to execute rule', message: error.response?.data?.message || error.message });
  }
});

// Toggle rule
router.post('/rules/:id/toggle', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/rules/${req.params.id}/toggle/`, {}, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to toggle rule', message: error.response?.data?.message || error.message });
  }
});

// List executions
router.get('/executions', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/automation/executions/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get executions', message: error.response?.data?.message || error.message });
  }
});

// Create execution
router.post('/executions', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/executions/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create execution', message: error.response?.data?.message || error.message });
  }
});

// Templates
router.get('/templates', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/automation/templates/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get templates', message: error.response?.data?.message || error.message });
  }
});

router.post('/templates', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/templates/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create template', message: error.response?.data?.message || error.message });
  }
});

router.post('/templates/:id/use', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/templates/${req.params.id}/use/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to use template', message: error.response?.data?.message || error.message });
  }
});

// Schedules
router.get('/schedules', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/automation/schedules/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get schedules', message: error.response?.data?.message || error.message });
  }
});

router.post('/schedules', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/schedules/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create schedule', message: error.response?.data?.message || error.message });
  }
});

router.post('/schedules/:id/toggle', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/automation/schedules/${req.params.id}/toggle/`, {}, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to toggle schedule', message: error.response?.data?.message || error.message });
  }
});

// Stats & Report
router.get('/rules/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/automation/rules/stats/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get automation stats', message: error.response?.data?.message || error.message });
  }
});

router.get('/rules/report', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/automation/rules/report/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get automation report', message: error.response?.data?.message || error.message });
  }
});

module.exports = router;


