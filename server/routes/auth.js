const express = require('express');
const bcrypt = require('bcryptjs');
const { getDb, saveDatabase } = require('../models/database');
const { generateToken } = require('../middleware/auth');

const router = express.Router();

router.post('/login', (req, res) => {
  const { username, password, captcha } = req.body;
  const db = getDb();

  if (!captcha || captcha.toLowerCase() !== (req.session.captcha || '').toLowerCase()) {
    return res.status(401).json({ error: '验证码错误' });
  }

  const user = db.exec(
    `SELECT * FROM users WHERE username = ?`,
    [username]
  )[0];

  if (!user || user.values.length === 0) {
    return res.status(401).json({ error: '用户名或密码错误' });
  }

  const row = user.values[0];
  const hashedPassword = row[2];

  if (!bcrypt.compareSync(password, hashedPassword)) {
    return res.status(401).json({ error: '用户名或密码错误' });
  }

  req.session.captcha = null;

  const userData = {
    id: row[0],
    username: row[1],
    name: row[3],
    role: row[4]
  };

  const token = generateToken(userData);
  res.json({ token, user: userData });
});

router.post('/register', (req, res) => {
  const { username, password, name, role = 'member' } = req.body;
  const db = getDb();

  const existing = db.exec(`SELECT id FROM users WHERE username = ?`, [username]);
  if (existing[0]?.values.length > 0) {
    return res.status(400).json({ error: '用户名已存在' });
  }

  const hashedPassword = bcrypt.hashSync(password, 10);
  db.run(
    `INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)`,
    [username, hashedPassword, name, role]
  );

  saveDatabase();
  res.json({ message: '注册成功' });
});

router.get('/me', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const jwt = require('jsonwebtoken');
  const { SECRET_KEY } = require('../middleware/auth');

  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    res.json(decoded);
  } catch (err) {
    res.status(401).json({ error: '无效token' });
  }
});

module.exports = router;
