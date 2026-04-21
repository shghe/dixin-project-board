const express = require('express');
const bcrypt = require('bcryptjs');
const { getDb, saveDatabase } = require('../models/database');
const { authMiddleware, adminMiddleware } = require('../middleware/auth');

const router = express.Router();
router.use(authMiddleware);

router.get('/', adminMiddleware, (req, res) => {
  const db = getDb();
  const result = db.exec(`SELECT id, username, name, role, created_at FROM users ORDER BY id`);

  if (!result[0]) {
    return res.json([]);
  }

  const users = result[0].values.map(row => ({
    id: row[0],
    username: row[1],
    name: row[2],
    role: row[3],
    created_at: row[4]
  }));

  res.json(users);
});

router.post('/', adminMiddleware, (req, res) => {
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

  const result = db.exec(`SELECT last_insert_rowid() as id`);
  res.json({ id: result[0].values[0][0], username, name, role });
});

router.put('/:id', adminMiddleware, (req, res) => {
  const { id } = req.params;
  const { name, role, password } = req.body;
  const db = getDb();

  if (password) {
    const hashedPassword = bcrypt.hashSync(password, 10);
    db.run(`UPDATE users SET name=?, role=?, password=? WHERE id=?`, [name, role, hashedPassword, id]);
  } else {
    db.run(`UPDATE users SET name=?, role=? WHERE id=?`, [name, role, id]);
  }

  saveDatabase();
  res.json({ id: parseInt(id), name, role });
});

router.delete('/:id', adminMiddleware, (req, res) => {
  const { id } = req.params;
  const db = getDb();

  if (parseInt(id) === req.user.id) {
    return res.status(400).json({ error: '不能删除自己' });
  }

  db.run(`DELETE FROM projects WHERE user_id = ?`, [id]);
  db.run(`DELETE FROM users WHERE id = ?`, [id]);
  saveDatabase();
  res.json({ message: '删除成功' });
});

module.exports = router;
