const express = require('express');
const cors = require('cors');
const session = require('express-session');
const path = require('path');
const { initDatabase } = require('./models/database');

const authRoutes = require('./routes/auth');
const projectRoutes = require('./routes/projects');
const userRoutes = require('./routes/users');
const uploadRoutes = require('./routes/upload');
const captchaRoutes = require('./routes/captcha');

async function start() {
  await initDatabase();

  const app = express();

  app.use(cors({
    origin: true,
    credentials: true
  }));
  app.use(express.json());
  app.use(session({
    secret: 'project-management-secret',
    resave: false,
    saveUninitialized: true,
    cookie: { maxAge: 3600000 }
  }));

  app.use('/api/auth', authRoutes);
  app.use('/api/projects', projectRoutes);
  app.use('/api/users', userRoutes);
  app.use('/api/upload', uploadRoutes);
  app.use('/api', captchaRoutes);

  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', time: new Date().toISOString() });
  });

  // Serve frontend in production
  const distPath = path.join(__dirname, '..', 'client', 'dist');
  app.use(express.static(distPath));
  app.get('*', (req, res) => {
    res.sendFile(path.join(distPath, 'index.html'));
  });

  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

start().catch(err => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
