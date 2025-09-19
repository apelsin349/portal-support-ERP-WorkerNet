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

// Knowledge Articles

// List articles
router.get('/articles', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/articles/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить статьи',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create article
router.post('/articles', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/knowledge/articles/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось создать статью',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get article details
router.get('/articles/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/articles/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить статью',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update article
router.put('/articles/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/knowledge/articles/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось обновить статью',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete article
router.delete('/articles/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/knowledge/articles/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось удалить статью',
      message: error.response?.data?.message || error.message
    });
  }
});

// Rate article
router.post('/articles/:id/rate', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/knowledge/articles/${req.params.id}/rate/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось оценить статью',
      message: error.response?.data?.message || error.message
    });
  }
});

// Mark article as helpful
router.post('/articles/:id/helpful', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/knowledge/articles/${req.params.id}/helpful/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось отметить статью как полезную',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get featured articles
router.get('/articles/featured', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/articles/featured/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить рекомендуемые статьи',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get popular articles
router.get('/articles/popular', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/articles/popular/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить популярные статьи',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get recent articles
router.get('/articles/recent', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/articles/recent/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить последние статьи',
      message: error.response?.data?.message || error.message
    });
  }
});

// Search articles
router.post('/articles/search', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/knowledge/articles/search/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось выполнить поиск статей',
      message: error.response?.data?.message || error.message
    });
  }
});

// Knowledge Categories

// List categories
router.get('/categories', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/categories/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить категории',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create category
router.post('/categories', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/knowledge/categories/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось создать категорию',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get category details
router.get('/categories/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/categories/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить категорию',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update category
router.put('/categories/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/knowledge/categories/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось обновить категорию',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete category
router.delete('/categories/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/knowledge/categories/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось удалить категорию',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get category tree
router.get('/categories/tree', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/categories/tree/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить дерево категорий',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get articles in category
router.get('/categories/:id/articles', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/categories/${req.params.id}/articles/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить статьи в категории',
      message: error.response?.data?.message || error.message
    });
  }
});

// Knowledge Statistics

// Get knowledge base statistics
router.get('/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/knowledge/articles/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить статистику базы знаний',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
