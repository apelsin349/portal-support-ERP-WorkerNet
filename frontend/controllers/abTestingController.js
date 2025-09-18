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

// Feature Flags

// List feature flags
router.get('/feature-flags', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/feature-flags/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get feature flags',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create feature flag
router.post('/feature-flags', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/feature-flags/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create feature flag',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get feature flag details
router.get('/feature-flags/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/feature-flags/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get feature flag',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update feature flag
router.put('/feature-flags/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ab-testing/feature-flags/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update feature flag',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete feature flag
router.delete('/feature-flags/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ab-testing/feature-flags/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete feature flag',
      message: error.response?.data?.message || error.message
    });
  }
});

// Toggle feature flag
router.post('/feature-flags/:id/toggle', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/feature-flags/${req.params.id}/toggle/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to toggle feature flag',
      message: error.response?.data?.message || error.message
    });
  }
});

// Check feature flags
router.get('/feature-flags/check', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/feature-flags/check/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to check feature flags',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get feature flag usage stats
router.get('/feature-flags/usage-stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/feature-flags/usage_stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get feature flag usage stats',
      message: error.response?.data?.message || error.message
    });
  }
});

// A/B Tests

// List A/B tests
router.get('/tests', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/tests/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B tests',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create A/B test
router.post('/tests', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/tests/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create A/B test',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get A/B test details
router.get('/tests/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update A/B test
router.put('/tests/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update A/B test',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete A/B test
router.delete('/tests/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete A/B test',
      message: error.response?.data?.message || error.message
    });
  }
});

// Start A/B test
router.post('/tests/:id/start', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/start/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to start A/B test',
      message: error.response?.data?.message || error.message
    });
  }
});

// Stop A/B test
router.post('/tests/:id/stop', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/stop/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to stop A/B test',
      message: error.response?.data?.message || error.message
    });
  }
});

// Assign user to A/B test
router.post('/tests/:id/assign-user', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/assign_user/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to assign user to A/B test',
      message: error.response?.data?.message || error.message
    });
  }
});

// Track A/B test event
router.post('/tests/:id/track-event', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/track_event/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to track A/B test event',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get A/B test statistics
router.get('/tests/:id/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/tests/${req.params.id}/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get active A/B tests
router.get('/tests/active', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/tests/active_tests/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get active A/B tests',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get user A/B tests
router.get('/tests/user-tests', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/tests/user_tests/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get user A/B tests',
      message: error.response?.data?.message || error.message
    });
  }
});

// A/B Test Variants

// List A/B test variants
router.get('/variants', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/variants/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test variants',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create A/B test variant
router.post('/variants', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/variants/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create A/B test variant',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get A/B test variant details
router.get('/variants/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/variants/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test variant',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update A/B test variant
router.put('/variants/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ab-testing/variants/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update A/B test variant',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete A/B test variant
router.delete('/variants/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ab-testing/variants/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete A/B test variant',
      message: error.response?.data?.message || error.message
    });
  }
});

// A/B Test Participants

// List A/B test participants
router.get('/participants', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/participants/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test participants',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get A/B test participant details
router.get('/participants/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/participants/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test participant',
      message: error.response?.data?.message || error.message
    });
  }
});

// A/B Test Events

// List A/B test events
router.get('/events', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/events/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test events',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create A/B test event
router.post('/events', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ab-testing/events/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create A/B test event',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get A/B test event details
router.get('/events/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ab-testing/events/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get A/B test event',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
