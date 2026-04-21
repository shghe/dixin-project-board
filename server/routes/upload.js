const express = require('express');
const multer = require('multer');
const path = require('path');
const { authMiddleware, adminMiddleware } = require('../middleware/auth');
const { importFromExcel } = require('../utils/importExcel');

const router = express.Router();
router.use(authMiddleware);

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, '..', 'uploads'));
  },
  filename: (req, file, cb) => {
    const uniqueName = Date.now() + '-' + file.originalname;
    cb(null, uniqueName);
  }
});

const upload = multer({ storage });

if (!require('fs').existsSync(path.join(__dirname, '..', 'uploads'))) {
  require('fs').mkdirSync(path.join(__dirname, '..', 'uploads'));
}

router.post('/import', adminMiddleware, upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: '请上传文件' });
  }

  try {
    const results = importFromExcel(req.file.path);
    res.json({
      message: '导入成功',
      results
    });
  } catch (err) {
    res.status(500).json({ error: `导入失败: ${err.message}` });
  }
});

module.exports = router;
