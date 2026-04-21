const express = require('express');
const svgCaptcha = require('svg-captcha');

const router = express.Router();

router.get('/captcha', (req, res) => {
  const captcha = svgCaptcha.create({
    width: 120,
    height: 40,
    fontSize: 42,
    noise: 3,
    background: '#f5f5f5'
  });
  req.session.captcha = captcha.text.toLowerCase();
  res.type('svg');
  res.send(captcha.data);
});

module.exports = router;
