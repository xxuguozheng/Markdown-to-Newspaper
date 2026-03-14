#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
REQUESTS_DIR = DATA_DIR / 'requests'

class AdminAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            # 解析请求路径
            path = urlparse(self.path).path
            
            if path == '/api/create_project':
                self.handle_create_project(params)
            elif path == '/api/update_project_meta':
                self.handle_update_project_meta(params)
            elif path == '/api/create_edition':
                self.handle_create_edition(params)
            else:
                self.send_error(404, 'Not Found')
        except Exception as e:
            self.send_error(500, f'Internal Server Error: {str(e)}')
    
    def handle_create_project(self, params):
        # 构建项目数据
        project_data = {
            'slug': params.get('slug', [''])[0].strip(),
            'label': params.get('label', [''])[0].strip(),
            'description': params.get('description', [''])[0].strip(),
            'summary': params.get('summary', [''])[0].strip(),
            'stage': params.get('stage', ['待补充'])[0].strip(),
            'blockers': params.get('blockers', [''])[0].strip(),
            'next': params.get('next', [''])[0].strip(),
            'status': params.get('status', ['active'])[0].strip()
        }
        
        # 验证必填字段
        if not project_data['slug'] or not project_data['label']:
            self.send_error(400, 'Slug and label are required')
            return
        
        # 创建请求文件
        request_file = REQUESTS_DIR / f'create-project-{os.urandom(8).hex()}.json'
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        # 调用 project_interface.py 创建项目
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'project_interface.py'),
             '--action', 'create_project',
             '--request', str(request_file)],
            capture_output=True,
            text=True
        )
        
        # 返回结果
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_update_project_meta(self, params):
        # 构建项目数据
        project_data = {
            'slug': params.get('slug', [''])[0].strip(),
            'label': params.get('label', [''])[0].strip(),
            'description': params.get('description', [''])[0].strip(),
            'summary': params.get('summary', [''])[0].strip(),
            'stage': params.get('stage', [''])[0].strip(),
            'blockers': params.get('blockers', [''])[0].strip(),
            'next': params.get('next', [''])[0].strip(),
            'status': params.get('status', ['active'])[0].strip()
        }
        
        # 验证必填字段
        if not project_data['slug']:
            self.send_error(400, 'Slug is required')
            return
        
        # 创建请求文件
        request_file = REQUESTS_DIR / f'update-project-{os.urandom(8).hex()}.json'
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        # 调用 project_interface.py 更新项目
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'project_interface.py'),
             '--action', 'update_project_meta',
             '--request', str(request_file)],
            capture_output=True,
            text=True
        )
        
        # 返回结果
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_create_edition(self, params):
        """处理创建版次的请求"""
        # 构建版次数据
        edition_data = {
            'project_slug': params.get('project_slug', [''])[0].strip(),
            'title': params.get('title', [''])[0].strip(),
            'summary': params.get('summary', [''])[0].strip(),
            'content': params.get('content', [''])[0].strip(),
            'type': params.get('type', ['brief'])[0].strip()
        }
        
        # 验证必填字段
        if not edition_data['project_slug']:
            self.send_error(400, 'Project slug is required')
            return
        
        if not edition_data['title']:
            self.send_error(400, 'Title is required')
            return
        
        # 创建请求文件
        request_file = REQUESTS_DIR / f'create-edition-{os.urandom(8).hex()}.json'
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(edition_data, f, ensure_ascii=False, indent=2)
        
        # 调用创建版次的脚本
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'create_edition.py'),
             '--request', str(request_file)],
            capture_output=True,
            text=True
        )
        
        # 返回结果
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            'ok': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(port=8001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AdminAPIHandler)
    print(f'Admin API server running on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()