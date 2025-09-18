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

// Metrics
router.get('/metrics', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/metrics/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get metrics', message: error.response?.data?.message || error.message });
  }
});

router.post('/metrics', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/metrics/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create metric', message: error.response?.data?.message || error.message });
  }
});

router.get('/metrics/by-category', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/metrics/by_category/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get metrics by category', message: error.response?.data?.message || error.message });
  }
});

router.get('/metrics/latest', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/metrics/latest/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get latest metrics', message: error.response?.data?.message || error.message });
  }
});

router.get('/metrics/aggregated', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/metrics/aggregated/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get aggregated metrics', message: error.response?.data?.message || error.message });
  }
});

router.post('/metrics/search', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/metrics/search/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to search metrics', message: error.response?.data?.message || error.message });
  }
});

router.get('/metrics/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/metrics/stats/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get metrics stats', message: error.response?.data?.message || error.message });
  }
});

// Alerts
router.get('/alerts', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/alerts/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get alerts', message: error.response?.data?.message || error.message });
  }
});

router.post('/alerts', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/alerts/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create alert', message: error.response?.data?.message || error.message });
  }
});

router.post('/alerts/:id/resolve', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/alerts/${req.params.id}/resolve/`, {}, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to resolve alert', message: error.response?.data?.message || error.message });
  }
});

router.get('/alerts/active', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/alerts/active/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get active alerts', message: error.response?.data?.message || error.message });
  }
});

router.get('/alerts/by-severity', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/alerts/by_severity/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get alerts by severity', message: error.response?.data?.message || error.message });
  }
});

// Traces
router.get('/traces', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/traces/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get traces', message: error.response?.data?.message || error.message });
  }
});

router.post('/traces', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/traces/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create trace', message: error.response?.data?.message || error.message });
  }
});

router.get('/traces/by-operation', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/traces/by_operation/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get traces by operation', message: error.response?.data?.message || error.message });
  }
});

router.get('/traces/slow', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/traces/slow_operations/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get slow operations', message: error.response?.data?.message || error.message });
  }
});

router.get('/traces/failed', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/traces/failed_operations/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get failed operations', message: error.response?.data?.message || error.message });
  }
});

// Dashboards
router.get('/dashboards', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/dashboards/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get dashboards', message: error.response?.data?.message || error.message });
  }
});

router.post('/dashboards', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/dashboards/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create dashboard', message: error.response?.data?.message || error.message });
  }
});

router.post('/dashboards/:id/add-widget', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/dashboards/${req.params.id}/add_widget/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to add widget', message: error.response?.data?.message || error.message });
  }
});

router.post('/dashboards/:id/remove-widget', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/dashboards/${req.params.id}/remove_widget/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to remove widget', message: error.response?.data?.message || error.message });
  }
});

router.post('/dashboards/:id/update-widgets', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/dashboards/${req.params.id}/update_widgets/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to update widgets', message: error.response?.data?.message || error.message });
  }
});

router.get('/dashboards/public', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/dashboards/public_dashboards/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get public dashboards', message: error.response?.data?.message || error.message });
  }
});

router.get('/dashboards/my', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/dashboards/my_dashboards/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get my dashboards', message: error.response?.data?.message || error.message });
  }
});

// Reports
router.get('/reports', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/reports/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get reports', message: error.response?.data?.message || error.message });
  }
});

router.post('/reports', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/reports/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create report', message: error.response?.data?.message || error.message });
  }
});

router.post('/reports/:id/generate', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/reports/${req.params.id}/generate/`, {}, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to generate report', message: error.response?.data?.message || error.message });
  }
});

router.get('/reports/my', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/reports/my_reports/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get my reports', message: error.response?.data?.message || error.message });
  }
});

// Thresholds
router.get('/thresholds', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/thresholds/`, { headers: getAuthHeaders(req), params: req.query });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get thresholds', message: error.response?.data?.message || error.message });
  }
});

router.post('/thresholds', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/thresholds/`, req.body, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to create threshold', message: error.response?.data?.message || error.message });
  }
});

router.post('/thresholds/:id/toggle', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/performance/thresholds/${req.params.id}/toggle/`, {}, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to toggle threshold', message: error.response?.data?.message || error.message });
  }
});

router.get('/thresholds/active', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/performance/thresholds/active_thresholds/`, { headers: getAuthHeaders(req) });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({ error: 'Failed to get active thresholds', message: error.response?.data?.message || error.message });
  }
});

module.exports = router;


