@echo off

rem 启动主 HTTP 服务器（端口 8000）
start "Main Server" cmd /c "py -m http.server 8000"

rem 等待 2 秒
ping 127.0.0.1 -n 3 > nul

rem 启动管理 API 服务器（端口 8001）
start "Admin API Server" cmd /c "py scripts/admin_api.py"

echo 服务器启动完成！
echo 主页面：http://localhost:8000/site/index.html
echo 项目管理：http://localhost:8000/site/admin/index.html
echo 按任意键关闭窗口...
pause > nul