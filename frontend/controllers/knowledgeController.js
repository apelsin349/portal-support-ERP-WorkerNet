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
      error: 'Failed to get articles',
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
      error: 'Failed to create article',
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
      error: 'Failed to get article',
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
      error: 'Failed to update article',
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
      error: 'Failed to delete article',
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
      error: 'Failed to rate article',
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
      error: 'Failed to mark article as helpful',
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
      error: 'Failed to get featured articles',
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
      error: 'Failed to get popular articles',
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
      error: 'Failed to get recent articles',
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
      error: 'Failed to search articles',
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
      error: 'Failed to get categories',
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
      error: 'Failed to create category',
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
      error: 'Failed to get category',
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
      error: 'Failed to update category',
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
      error: 'Failed to delete category',
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
      error: 'Failed to get category tree',
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
      error: 'Failed to get articles in category',
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
      error: 'Failed to get knowledge base statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
