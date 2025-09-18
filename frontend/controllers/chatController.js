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

// List messages
router.get('/messages', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/chat/messages/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get messages',
      message: error.response?.data?.message || error.message
    });
  }
});

// Send message
router.post('/messages', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat/messages/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to send message',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get message details
router.get('/messages/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/chat/messages/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get message',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update message
router.put('/messages/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/chat/messages/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update message',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete message
router.delete('/messages/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/chat/messages/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete message',
      message: error.response?.data?.message || error.message
    });
  }
});

// Mark message as read
router.post('/messages/:id/mark-read', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat/messages/${req.params.id}/mark_read/`, {}, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to mark message as read',
      message: error.response?.data?.message || error.message
    });
  }
});

// Mark conversation as read
router.post('/mark-conversation-read', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat/messages/mark_conversation_read/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to mark conversation as read',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get conversations
router.get('/conversations', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/chat/messages/conversations/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get conversations',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get conversation
router.get('/conversation', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/chat/messages/conversation/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get conversation',
      message: error.response?.data?.message || error.message
    });
  }
});

// Search messages
router.post('/search', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat/messages/search/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to search messages',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get unread count
router.get('/unread/count', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/chat/messages/unread_count/`, {
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

// Get chat statistics
router.get('/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/chat/messages/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get chat statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

// React to message
router.post('/messages/:id/react', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat/messages/${req.params.id}/react/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to react to message',
      message: error.response?.data?.message || error.message
    });
  }
});

// Typing status
router.post('/typing', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat/messages/typing/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update typing status',
      message: error.response?.data?.message || error.message
    });
  }
});

// Online status
router.get('/online-status', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/chat/messages/online_status/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get online status',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
