const express = require('express');
const { getDb, saveDatabase } = require('../models/database');
const { authMiddleware, adminMiddleware } = require('../middleware/auth');

const router = express.Router();
router.use(authMiddleware);

function calculateProjectFields(project) {
  const now = new Date();

  if (project.status === '完成') {
    project.is_completed = 1;
  } else {
    project.is_completed = 0;
  }

  if (project.status !== '完成' && project.end_date) {
    const endDate = new Date(project.end_date);
    project.is_overdue = endDate < now ? 1 : 0;
  } else {
    project.is_overdue = 0;
  }

  return project;
}

router.get('/', (req, res) => {
  const db = getDb();
  let result;

  if (req.user.role === 'admin' && req.query.userId) {
    result = db.exec(`SELECT * FROM projects WHERE user_id = ? ORDER BY id`, [req.query.userId]);
  } else {
    result = db.exec(`SELECT * FROM projects ORDER BY user_id, id`);
  }

  if (!result[0]) {
    return res.json([]);
  }

  const columns = result[0].columns;
  const projects = result[0].values.map(row => {
    const project = {};
    columns.forEach((col, i) => project[col] = row[i]);
    return calculateProjectFields(project);
  });

  res.json(projects);
});

router.get('/stats', (req, res) => {
  const db = getDb();
  let userIds = [];

  if (req.user.role === 'admin' && req.query.userId) {
    userIds = [parseInt(req.query.userId)];
  } else {
    const users = db.exec(`SELECT id FROM users`);
    userIds = users[0]?.values.map(r => r[0]) || [];
  }

  const stats = userIds.map(userId => {
    const user = db.exec(`SELECT name FROM users WHERE id = ?`, [userId]);
    const userName = user[0]?.values[0]?.[0] || '';

    const projects = db.exec(`SELECT status, end_date FROM projects WHERE user_id = ?`, [userId]);
    const rows = projects[0]?.values || [];

    let normal = 0, completed = 0, overdue = 0, inProgress = 0, delayed = 0, cancelled = 0, paused = 0;
    const now = new Date();
    now.setHours(0, 0, 0, 0);

    rows.forEach(row => {
      const status = row[0] || '未完成';
      const endDate = row[1] ? new Date(row[1]) : null;
      if (endDate) endDate.setHours(0, 0, 0, 0);

      if (status === '完成') {
        completed++;
      } else if (status === '进行中') {
        inProgress++;
        if (endDate && endDate < now) overdue++;
      } else if (status === '滞后') {
        delayed++;
        if (endDate && endDate < now) overdue++;
      } else if (status === '取消') {
        cancelled++;
      } else if (status === '暂停') {
        paused++;
      } else {
        normal++;
        if (endDate && endDate < now) overdue++;
      }
    });

    return {
      userId,
      userName,
      normal,
      completed,
      overdue,
      inProgress,
      delayed,
      cancelled,
      paused,
      total: rows.length
    };
  });

  if (req.query.userId) {
    res.json(stats[0] || { userId: req.query.userId, userName: '', normal: 0, completed: 0, overdue: 0, inProgress: 0, delayed: 0, cancelled: 0, paused: 0, total: 0 });
  } else {
    res.json(stats);
  }
});

router.post('/', (req, res) => {
  const { name, type, role, work_content, start_date, end_date, progress, status, remark } = req.body;
  const db = getDb();

  let project = { name, type, role, work_content, start_date, end_date, progress, status, remark };
  project = calculateProjectFields(project);

  db.run(
    `INSERT INTO projects (user_id, name, type, role, work_content, start_date, end_date, progress, status, is_completed, is_overdue, remark)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [req.user.id, name, type, role, work_content, start_date, end_date, progress || 0, status || '未完成', project.is_completed, project.is_overdue, remark]
  );

  saveDatabase();

  const result = db.exec(`SELECT last_insert_rowid() as id`);
  const id = result[0].values[0][0];

  res.json({ id, ...project });
});

router.put('/:id', (req, res) => {
  const { id } = req.params;
  const { name, type, role, work_content, start_date, end_date, progress, status, remark } = req.body;
  const db = getDb();

  const existing = db.exec(`SELECT user_id FROM projects WHERE id = ?`, [id]);
  if (existing[0]?.values[0]?.[0] !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: '无权修改此项目' });
  }

  let project = { name, type, role, work_content, start_date, end_date, progress, status, remark };
  project = calculateProjectFields(project);

  db.run(
    `UPDATE projects SET name=?, type=?, role=?, work_content=?, start_date=?, end_date=?, progress=?, status=?, is_completed=?, is_overdue=?, remark=?, updated_at=CURRENT_TIMESTAMP
     WHERE id=?`,
    [name, type, role, work_content, start_date, end_date, progress || 0, status || '未完成', project.is_completed, project.is_overdue, remark, id]
  );

  saveDatabase();
  res.json({ id: parseInt(id), ...project });
});

router.delete('/:id', (req, res) => {
  const { id } = req.params;
  const db = getDb();

  const existing = db.exec(`SELECT user_id FROM projects WHERE id = ?`, [id]);
  if (existing[0]?.values[0]?.[0] !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: '无权删除此项目' });
  }

  db.run(`DELETE FROM projects WHERE id = ?`, [id]);
  saveDatabase();
  res.json({ message: '删除成功' });
});

module.exports = router;
