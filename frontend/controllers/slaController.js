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

// SLA Rules

// List SLA rules
router.get('/sla', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/sla/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get SLA rules',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create SLA rule
router.post('/sla', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/sla/sla/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create SLA rule',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get SLA rule details
router.get('/sla/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/sla/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get SLA rule',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update SLA rule
router.put('/sla/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/sla/sla/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update SLA rule',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete SLA rule
router.delete('/sla/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/sla/sla/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete SLA rule',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get SLA statistics
router.get('/sla/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/sla/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get SLA statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get SLA violations
router.get('/sla/violations', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/sla/violations/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get SLA violations',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get SLA report
router.get('/sla/report', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/sla/report/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get SLA report',
      message: error.response?.data?.message || error.message
    });
  }
});

// Ticket SLA

// List ticket SLA
router.get('/ticket-sla', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/ticket-sla/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get ticket SLA',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create ticket SLA
router.post('/ticket-sla', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/sla/ticket-sla/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create ticket SLA',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get ticket SLA details
router.get('/ticket-sla/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/ticket-sla/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get ticket SLA',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update ticket SLA
router.put('/ticket-sla/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/sla/ticket-sla/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update ticket SLA',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete ticket SLA
router.delete('/ticket-sla/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/sla/ticket-sla/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete ticket SLA',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update ticket SLA times
router.post('/ticket-sla/:id/update-times', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/sla/ticket-sla/${req.params.id}/update_times/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update ticket SLA times',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get overdue SLA
router.get('/ticket-sla/overdue', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/ticket-sla/overdue/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get overdue SLA',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get upcoming deadlines
router.get('/ticket-sla/upcoming-deadlines', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/sla/ticket-sla/upcoming_deadlines/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get upcoming deadlines',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
