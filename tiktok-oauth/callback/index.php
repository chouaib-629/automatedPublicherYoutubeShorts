<?php
$code = $_GET['code'] ?? '';
header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html><head><title>TikTok OAuth</title></head>
<body>
  <h1>TikTok OAuth callback</h1>
  <p><?php echo $code ? 'Copy this code (use once): <strong>' . htmlspecialchars($code) . '</strong>' : 'No code in URL.'; ?></p>
</body></html>
