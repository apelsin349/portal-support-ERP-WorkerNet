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

// Response Templates

// List templates
router.get('/templates', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get templates',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create template
router.post('/templates', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/templates/templates/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create template',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get template details
router.get('/templates/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get template',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update template
router.put('/templates/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/templates/templates/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update template',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete template
router.delete('/templates/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/templates/templates/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete template',
      message: error.response?.data?.message || error.message
    });
  }
});

// Use template
router.post('/templates/:id/use', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/templates/templates/${req.params.id}/use/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to use template',
      message: error.response?.data?.message || error.message
    });
  }
});

// Preview template
router.post('/templates/:id/preview', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/templates/templates/${req.params.id}/preview/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to preview template',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create template version
router.post('/templates/:id/create-version', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/templates/templates/${req.params.id}/create_version/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create template version',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get template variables
router.get('/templates/:id/variables', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/${req.params.id}/variables/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get template variables',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get template versions
router.get('/templates/:id/versions', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/${req.params.id}/versions/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get template versions',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get template usage history
router.get('/templates/:id/usage-history', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/${req.params.id}/usage_history/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get template usage history',
      message: error.response?.data?.message || error.message
    });
  }
});

// Search templates
router.post('/templates/search', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/templates/templates/search/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to search templates',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get template statistics
router.get('/templates/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get template statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get template report
router.get('/templates/report', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/report/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get template report',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get my templates
router.get('/templates/my-templates', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/my_templates/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get my templates',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get popular templates
router.get('/templates/popular', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/templates/popular/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get popular templates',
      message: error.response?.data?.message || error.message
    });
  }
});

// Template Categories

// List categories
router.get('/categories', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/categories/`, {
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
    const response = await axios.post(`${BACKEND_URL}/api/templates/categories/`, req.body, {
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
    const response = await axios.get(`${BACKEND_URL}/api/templates/categories/${req.params.id}/`, {
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
    const response = await axios.put(`${BACKEND_URL}/api/templates/categories/${req.params.id}/`, req.body, {
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
    const response = await axios.delete(`${BACKEND_URL}/api/templates/categories/${req.params.id}/`, {
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

// Get templates in category
router.get('/categories/:id/templates', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/categories/${req.params.id}/templates/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get templates in category',
      message: error.response?.data?.message || error.message
    });
  }
});

// Template Variables

// List variables
router.get('/variables', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/variables/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get variables',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create variable
router.post('/variables', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/templates/variables/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create variable',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get variable details
router.get('/variables/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/templates/variables/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get variable',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update variable
router.put('/variables/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/templates/variables/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update variable',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete variable
router.delete('/variables/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/templates/variables/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete variable',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
