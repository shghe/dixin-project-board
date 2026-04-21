const XLSX = require('xlsx');
const bcrypt = require('bcryptjs');
const { getDb, saveDatabase } = require('../models/database');

function importFromExcel(filePath) {
  const workbook = XLSX.readFile(filePath);
  const db = getDb();
  const results = { users: 0, projects: 0, errors: [] };

  const userSheetNames = workbook.SheetNames.filter(name =>
    !['地环院', '样式'].includes(name)
  );

  for (const sheetName of userSheetNames) {
    try {
      const userName = sheetName;

      let user = db.exec(`SELECT id FROM users WHERE name = ?`, [userName])[0];
      let userId;

      if (!user || user.values.length === 0) {
        const hashedPassword = bcrypt.hashSync('123456', 10);
        db.run(
          `INSERT INTO users (username, password, name, role) VALUES (?, ?, ?, ?)`,
          [userName, hashedPassword, userName, 'member']
        );
        const result = db.exec(`SELECT last_insert_rowid() as id`);
        userId = result[0].values[0][0];
        results.users++;
      } else {
        userId = user.values[0][0];
      }

      const sheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(sheet, {header: 1, defval: ''});
      const range = XLSX.utils.decode_range(sheet['!ref']);
      const headerRow = 10;
      const startRow = 12;

      if (data.length <= startRow) continue;

      const headers = data[headerRow] || [];
      const nameIndex = headers.indexOf('姓名');
      const projectNameIndex = headers.indexOf('项目名称');
      const typeIndex = headers.indexOf('项目类型');
      const roleIndex = headers.indexOf('项目角色');
      const workContentIndex = headers.indexOf('主要工作内容');
      const startDateIndex = headers.indexOf('开始日期');
      const endDateIndex = headers.indexOf('截止日期');
      const progressIndex = headers.indexOf('进度');
      const statusIndex = headers.indexOf('当前状态');
      const remarkIndex = headers.indexOf('备注');

      for (let r = startRow; r <= range.e.r; r++) {
        const row = data[r];
        if (!row || row.length === 0) continue;

        const projectName = projectNameIndex >= 0 ? row[projectNameIndex] : '';
        if (!projectName || projectName === '填项目名称') continue;

        const status = statusIndex >= 0 ? row[statusIndex] : '未完成';
        let endDate = endDateIndex >= 0 ? row[endDateIndex] : '';
        let progress = progressIndex >= 0 ? row[progressIndex] : 0;

        if (typeof endDate === 'number') {
          const date = new Date((endDate - 25569) * 86400 * 1000);
          endDate = date.toISOString().split('T')[0];
        }

        if (typeof progress === 'string' && progress.includes('%')) {
          progress = parseFloat(progress.replace('%', '')) / 100;
        }

        const isCompleted = status === '完成' ? 1 : 0;
        const now = new Date();
        const isOverdue = status !== '完成' && endDate && new Date(endDate) < now ? 1 : 0;

        db.run(
          `INSERT INTO projects (user_id, name, type, role, work_content, start_date, end_date, progress, status, is_completed, is_overdue, remark)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            userId,
            projectName,
            typeIndex >= 0 ? row[typeIndex] : '',
            roleIndex >= 0 ? row[roleIndex] : '',
            workContentIndex >= 0 ? row[workContentIndex] : '',
            startDateIndex >= 0 ? row[startDateIndex] : '',
            endDate,
            progress,
            status,
            isCompleted,
            isOverdue,
            remarkIndex >= 0 ? row[remarkIndex] : ''
          ]
        );
        results.projects++;
      }
    } catch (err) {
      results.errors.push(`Sheet ${sheetName}: ${err.message}`);
    }
  }

  saveDatabase();
  return results;
}

module.exports = { importFromExcel };
