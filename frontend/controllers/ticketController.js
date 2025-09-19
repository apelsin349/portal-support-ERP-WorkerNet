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

// List tickets
router.get('/', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/tickets/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить тикеты',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create ticket
router.post('/', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/tickets/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось создать тикет',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get ticket details
router.get('/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/tickets/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить тикет',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update ticket
router.put('/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/tickets/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось обновить тикет',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete ticket
router.delete('/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/tickets/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось удалить тикет',
      message: error.response?.data?.message || error.message
    });
  }
});

// Assign ticket
router.post('/:id/assign', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/tickets/${req.params.id}/assign/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось назначить тикет',
      message: error.response?.data?.message || error.message
    });
  }
});

// Add comment to ticket
router.post('/:id/comment', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/tickets/${req.params.id}/comment/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось добавить комментарий',
      message: error.response?.data?.message || error.message
    });
  }
});

// Add attachment to ticket
router.post('/:id/attachment', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/tickets/${req.params.id}/attachment/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось добавить вложение',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get ticket statistics
router.get('/stats/overview', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/tickets/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить статистику тикетов',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get my tickets
router.get('/my/tickets', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/tickets/my-tickets/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить мои тикеты',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get urgent tickets
router.get('/urgent/tickets', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/tickets/urgent/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить срочные тикеты',
      message: error.response?.data?.message || error.message
    });
  }
});

// Search tickets
router.post('/search', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/tickets/search/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось выполнить поиск тикетов',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
