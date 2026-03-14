# 启动主 HTTP 服务器（端口 8000）
Start-Process "powershell.exe" -ArgumentList "-Command", "py -m http.server 8000" -WindowStyle Normal -WorkingDirectory "$PWD"

# 等待 2 秒
Start-Sleep -Seconds 2

# 启动管理 API 服务器（端口 8001）
Start-Process "powershell.exe" -ArgumentList "-Command", "py scripts/admin_api.py" -WindowStyle Normal -WorkingDirectory "$PWD"

Write-Host "服务器启动完成！"
Write-Host "主页面：http://localhost:8000/site/index.html"
Write-Host "项目管理：http://localhost:8000/site/admin/index.html"
Write-Host "按任意键关闭窗口..."
Read-Host