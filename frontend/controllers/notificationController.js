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

// List notifications
router.get('/', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/notifications/notifications/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get notifications',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create notification
router.post('/', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/notifications/notifications/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create notification',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get notification details
router.get('/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/notifications/notifications/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get notification',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update notification
router.put('/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/notifications/notifications/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update notification',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete notification
router.delete('/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/notifications/notifications/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete notification',
      message: error.response?.data?.message || error.message
    });
  }
});

// Mark notification as read
router.post('/:id/mark-read', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/notifications/notifications/${req.params.id}/mark_read/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to mark notification as read',
      message: error.response?.data?.message || error.message
    });
  }
});

// Mark notification as unread
router.post('/:id/mark-unread', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/notifications/notifications/${req.params.id}/mark_unread/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to mark notification as unread',
      message: error.response?.data?.message || error.message
    });
  }
});

// Mark all notifications as read
router.post('/mark-all-read', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/notifications/notifications/mark_all_read/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to mark all notifications as read',
      message: error.response?.data?.message || error.message
    });
  }
});

// Bulk update notifications
router.post('/bulk-update', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/notifications/notifications/bulk_update/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to bulk update notifications',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get unread count
router.get('/unread/count', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/notifications/notifications/unread_count/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get unread count',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get notification statistics
router.get('/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/notifications/notifications/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get notification statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get notification preferences
router.get('/preferences', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/notifications/notifications/preferences/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get notification preferences',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update notification preferences
router.post('/preferences', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/notifications/notifications/preferences/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update notification preferences',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get notifications by type
router.get('/by-type', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/notifications/notifications/by_type/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get notifications by type',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get urgent notifications
router.get('/urgent', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/notifications/notifications/urgent/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get urgent notifications',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
