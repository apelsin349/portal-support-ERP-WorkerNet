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

// List incidents
router.get('/', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/incidents/incidents/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get incidents',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create incident
router.post('/', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/incidents/incidents/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get incident details
router.get('/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update incident
router.put('/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete incident
router.delete('/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Add update to incident
router.post('/:id/add-update', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/add_update/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to add update to incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Escalate incident
router.post('/:id/escalate', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/escalate/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to escalate incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Assign incident
router.post('/:id/assign', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/assign/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to assign incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Resolve incident
router.post('/:id/resolve', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/resolve/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to resolve incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Close incident
router.post('/:id/close', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/incidents/incidents/${req.params.id}/close/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to close incident',
      message: error.response?.data?.message || error.message
    });
  }
});

// Search incidents
router.post('/search', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/incidents/incidents/search/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to search incidents',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get incident statistics
router.get('/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/incidents/incidents/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get incident statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get incident report
router.get('/report', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/incidents/incidents/report/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get incident report',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get my incidents
router.get('/my/incidents', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/incidents/incidents/my_incidents/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get my incidents',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get urgent incidents
router.get('/urgent', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/incidents/incidents/urgent/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get urgent incidents',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
