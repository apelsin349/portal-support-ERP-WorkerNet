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

// Ticket Ratings

// List ticket ratings
router.get('/ticket-ratings', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/ticket-ratings/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get ticket ratings',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create ticket rating
router.post('/ticket-ratings', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ratings/ticket-ratings/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create ticket rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get ticket rating details
router.get('/ticket-ratings/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/ticket-ratings/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get ticket rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update ticket rating
router.put('/ticket-ratings/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ratings/ticket-ratings/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update ticket rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete ticket rating
router.delete('/ticket-ratings/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ratings/ticket-ratings/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete ticket rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get ticket ratings by ticket
router.get('/ticket-ratings/by-ticket', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/ticket-ratings/by_ticket/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get ticket ratings by ticket',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get ticket ratings by agent
router.get('/ticket-ratings/by-agent', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/ticket-ratings/by_agent/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get ticket ratings by agent',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get my ticket ratings
router.get('/ticket-ratings/my-ratings', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/ticket-ratings/my_ratings/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get my ticket ratings',
      message: error.response?.data?.message || error.message
    });
  }
});

// Agent Ratings

// List agent ratings
router.get('/agent-ratings', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/agent-ratings/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get agent ratings',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create agent rating
router.post('/agent-ratings', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ratings/agent-ratings/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create agent rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get agent rating details
router.get('/agent-ratings/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/agent-ratings/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get agent rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update agent rating
router.put('/agent-ratings/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ratings/agent-ratings/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update agent rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete agent rating
router.delete('/agent-ratings/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ratings/agent-ratings/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete agent rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get agent ratings by agent
router.get('/agent-ratings/by-agent', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/agent-ratings/by_agent/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get agent ratings by agent',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get my agent ratings
router.get('/agent-ratings/my-ratings', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/agent-ratings/my_ratings/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get my agent ratings',
      message: error.response?.data?.message || error.message
    });
  }
});

// Service Ratings

// List service ratings
router.get('/service-ratings', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/service-ratings/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get service ratings',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create service rating
router.post('/service-ratings', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ratings/service-ratings/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create service rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get service rating details
router.get('/service-ratings/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/service-ratings/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get service rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update service rating
router.put('/service-ratings/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ratings/service-ratings/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update service rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete service rating
router.delete('/service-ratings/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ratings/service-ratings/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete service rating',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get my service ratings
router.get('/service-ratings/my-ratings', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/service-ratings/my_ratings/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get my service ratings',
      message: error.response?.data?.message || error.message
    });
  }
});

// Rating Surveys

// List surveys
router.get('/surveys', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/surveys/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get surveys',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create survey
router.post('/surveys', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ratings/surveys/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create survey',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get survey details
router.get('/surveys/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/surveys/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get survey',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update survey
router.put('/surveys/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ratings/surveys/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update survey',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete survey
router.delete('/surveys/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ratings/surveys/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete survey',
      message: error.response?.data?.message || error.message
    });
  }
});

// Respond to survey
router.post('/surveys/:id/respond', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ratings/surveys/${req.params.id}/respond/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to respond to survey',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get survey responses
router.get('/surveys/:id/responses', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/surveys/${req.params.id}/responses/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get survey responses',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get active surveys
router.get('/surveys/active', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/surveys/active_surveys/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get active surveys',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get my surveys
router.get('/surveys/my-surveys', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/surveys/my_surveys/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get my surveys',
      message: error.response?.data?.message || error.message
    });
  }
});

// Rating Categories

// List categories
router.get('/categories', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/categories/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get rating categories',
      message: error.response?.data?.message || error.message
    });
  }
});

// Create category
router.post('/categories', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ratings/categories/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to create rating category',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get category details
router.get('/categories/:id', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/categories/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get rating category',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update category
router.put('/categories/:id', async (req, res) => {
  try {
    const response = await axios.put(`${BACKEND_URL}/api/ratings/categories/${req.params.id}/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to update rating category',
      message: error.response?.data?.message || error.message
    });
  }
});

// Delete category
router.delete('/categories/:id', async (req, res) => {
  try {
    const response = await axios.delete(`${BACKEND_URL}/api/ratings/categories/${req.params.id}/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to delete rating category',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get rating statistics
router.get('/stats', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/categories/stats/`, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get rating statistics',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get rating report
router.get('/report', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/ratings/categories/report/`, {
      headers: getAuthHeaders(req),
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to get rating report',
      message: error.response?.data?.message || error.message
    });
  }
});

// Search ratings
router.post('/search', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/ratings/categories/search/`, req.body, {
      headers: getAuthHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to search ratings',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
