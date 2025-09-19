const express = require('express');
const router = express.Router();
const axios = require('axios');

// Backend API base URL
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// User registration
router.post('/register', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/register/`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Ошибка регистрации',
      message: error.response?.data?.message || error.message
    });
  }
});

// User login
router.post('/login', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/login/`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Ошибка входа',
      message: error.response?.data?.message || error.message
    });
  }
});

// User logout
router.post('/logout', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/logout/`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Ошибка выхода',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get user profile
router.get('/profile', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const response = await axios.get(`${BACKEND_URL}/api/auth/profile/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить профиль',
      message: error.response?.data?.message || error.message
    });
  }
});

// Update user profile
router.put('/profile', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const response = await axios.put(`${BACKEND_URL}/api/auth/profile/`, req.body, {
      headers: { Authorization: `Bearer ${token}` }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось обновить профиль',
      message: error.response?.data?.message || error.message
    });
  }
});

// Change password
router.post('/change-password', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const response = await axios.post(`${BACKEND_URL}/api/auth/change-password/`, req.body, {
      headers: { Authorization: `Bearer ${token}` }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось изменить пароль',
      message: error.response?.data?.message || error.message
    });
  }
});

// Reset password
router.post('/reset-password', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/reset-password/`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось сбросить пароль',
      message: error.response?.data?.message || error.message
    });
  }
});

// Verify email
router.post('/verify-email', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/verify-email/`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось подтвердить email',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get tenant list
router.get('/tenants', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const response = await axios.get(`${BACKEND_URL}/api/auth/tenants/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить арендаторов',
      message: error.response?.data?.message || error.message
    });
  }
});

// Get user list
router.get('/users', async (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const response = await axios.get(`${BACKEND_URL}/api/auth/users/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось получить пользователей',
      message: error.response?.data?.message || error.message
    });
  }
});

// Refresh token
router.post('/refresh-token', async (req, res) => {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/refresh-token/`, req.body);
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Не удалось обновить токен',
      message: error.response?.data?.message || error.message
    });
  }
});

module.exports = router;
