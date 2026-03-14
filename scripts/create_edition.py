#!/usr/bin/env python3
"""
创建版次的脚本
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
PROJECTS_DIR = ROOT / 'projects'

def slugify(text: str) -> str:
    """将文本转换为 slug"""
    # 移除特殊字符，保留中文和英文
    slug = re.sub(r'[^\w\u4e00-\u9fa5\s-]', '', text)
    # 替换空格和连字符
    slug = re.sub(r'[\s]+', '-', slug)
    # 移除连续的连字符
    slug = re.sub(r'-+', '-', slug)
    # 移除首尾连字符
    slug = slug.strip('-')
    return slug.lower()

def generate_edition_filename(project_slug: str, title: str, date_str: str) -> str:
    """生成版次文件名"""
    title_slug = slugify(title)
    return f"{title_slug}-{date_str}.html"

def generate_edition_html(title: str, summary: str, content: str, project_slug: str, edition_type: str) -> str:
    """生成版次 HTML 内容"""
    now = datetime.now().isoformat()
    
    # 转换 Markdown 内容到 HTML
    content_html = content
    # 转换标题
    content_html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content_html, flags=re.MULTILINE)
    content_html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content_html, flags=re.MULTILINE)
    content_html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content_html, flags=re.MULTILINE)
    # 转换粗体
    content_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content_html)
    # 转换斜体
    content_html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content_html)
    # 转换列表
    content_html = re.sub(r'^- (.+)$', r'<li>\1</li>', content_html, flags=re.MULTILINE)
    # 包裹列表
    content_html = re.sub(r'(<li>.*</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', content_html)
    # 转换段落
    content_html = re.sub(r'\n\n+', '</p><p>', content_html)
    content_html = '<p>' + content_html + '</p>'
    # 清理空标签
    content_html = re.sub(r'<p></p>', '', content_html)
    
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body{{margin:0;background:#ddd6c8;color:#171717;font-family:"Source Han Serif SC","Songti SC",serif;}}
    .page{{max-width:1100px;margin:24px auto;background:#f5f1e8;padding:24px 28px;box-shadow:0 12px 36px rgba(0,0,0,.18);}}
    .topline{{font:11px/1.4 Inter,sans-serif;color:#666;text-transform:uppercase;letter-spacing:.08em;}}
    h1{{margin:8px 0 10px;font-size:clamp(32px,4vw,58px);line-height:.95;}}
    .summary{{font:16px/1.65 Inter,sans-serif;margin-bottom:18px;color:#2b251f;}}
    .body{{font-size:17px;line-height:1.72;}}
    .body h2{{margin-top:28px;margin-bottom:12px;font-size:24px;font-weight:600;}}
    .body h3{{margin-top:20px;margin-bottom:10px;font-size:20px;font-weight:600;}}
    .body p{{margin:0 0 14px;}}
    .body ul{{margin:0 0 14px;padding-left:20px;}}
    .body li{{margin:4px 0;}}
    .body strong{{font-weight:700;color:#1f1a15;}}
    .body em{{font-style:italic;color:#4f4538;}}
  </style>
</head>
<body>
  <main class="page">
    <div class="topline">OpenClaw Newspaper · {now}</div>
    <h1>{title}</h1>
    <div class="summary">{summary}</div>
    <article class="body">{content_html}</article>
  </main>
</body>
</html>'''
    
    return html

def update_project_index(project_slug: str, edition_data: dict):
    """更新项目索引文件"""
    project_dir = PROJECTS_DIR / project_slug
    index_file = project_dir / 'index.html'
    
    if not index_file.exists():
        print(f"警告: 项目索引文件不存在 {index_file}")
        return
    
    # 读取现有索引
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成版次条目
    edition_entry = f'''<section class="edition edition-{edition_data['type']}" id="edition-{edition_data['number']}">
      <div class="edition-head">
        <div class="edition-meta">
          <small>{'快报' if edition_data['type'] == 'brief' else '头版'} · 第 {edition_data['number']:02d} 版</small>
          <b>{edition_data['title']}</b>
          <span>{edition_data['date']}</span>
        </div>
        <p>{edition_data['summary']}</p>
      </div>
      <iframe class="edition-frame" src="{edition_data['filename']}" loading="lazy" title="{edition_data['title']}" data-edition-density="{edition_data['type']}"></iframe>
    </section>'''
    
    # 查找 stream 部分并插入新条目
    stream_match = re.search(r'(<section class="stream">)(.*?)(</section>)', content, re.DOTALL)
    if stream_match:
        new_stream = stream_match.group(1) + '\n' + edition_entry + '\n' + stream_match.group(2) + stream_match.group(3)
        content = content[:stream_match.start()] + new_stream + content[stream_match.end():]
    else:
        # 如果没有 stream 部分，创建一个新的
        content = content.replace('</main>', f'<section class="stream">\n{edition_entry}\n</section>\n</main>')
    
    # 更新项目信息
    info_match = re.search(r'(<div class="project-info">)(.*?)(</div>)', content, re.DOTALL)
    if info_match:
        info_content = info_match.group(2)
        # 更新更新时间
        info_content = re.sub(r'(<span>Updated</span>).*?(</div>)', r'\1<span>{edition_data["date"]}</span>\2', info_content)
        content = content[:info_match.start()] + info_match.group(1) + info_content + info_match.group(3) + content[info_match.end():]
    
    # 保存更新后的索引
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已更新项目索引: {index_file}")

def create_edition(request_file: str):
    """创建版次"""
    # 读取请求文件
    with open(request_file, 'r', encoding='utf-8') as f:
        edition_data = json.load(f)
    
    project_slug = edition_data['project_slug']
    title = edition_data['title']
    summary = edition_data['summary']
    content = edition_data['content']
    edition_type = edition_data.get('type', 'brief')
    
    # 检查项目目录是否存在
    project_dir = PROJECTS_DIR / project_slug
    if not project_dir.exists():
        raise ValueError(f"项目不存在: {project_slug}")
    
    # 生成文件名
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = generate_edition_filename(project_slug, title, date_str)
    
    # 生成版次 HTML
    edition_html = generate_edition_html(title, summary, content, project_slug, edition_type)
    
    # 保存版次文件
    edition_file = project_dir / filename
    with open(edition_file, 'w', encoding='utf-8') as f:
        f.write(edition_html)
    
    print(f"已创建版次文件: {edition_file}")
    
    # 计算版次编号
    existing_editions = list(project_dir.glob('*.html'))
    edition_number = len([f for f in existing_editions if f.name != 'index.html']) + 1
    
    # 更新项目索引
    update_project_index(project_slug, {
        'title': title,
        'summary': summary,
        'filename': filename,
        'type': edition_type,
        'number': edition_number,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    
    # 更新门户索引
    update_portal_index(project_slug, title, summary, edition_type)

def update_portal_index(project_slug: str, title: str, summary: str, edition_type: str):
    """更新门户索引"""
    portal_index_file = ROOT / 'site' / 'data' / 'portal-index.json'
    
    if not portal_index_file.exists():
        print(f"警告: 门户索引文件不存在 {portal_index_file}")
        return
    
    with open(portal_index_file, 'r', encoding='utf-8') as f:
        portal_data = json.load(f)
    
    # 更新统计信息
    portal_data['stats']['editionCount'] = portal_data['stats'].get('editionCount', 0) + 1
    portal_data['stats']['latestEdition'] = {
        'projectSlug': project_slug,
        'title': title,
        'publishedAt': datetime.now().isoformat()
    }
    portal_data['stats']['recentlyUpdatedProject'] = {
        'slug': project_slug,
        'label': project_slug,
        'updatedAt': datetime.now().isoformat()
    }
    
    # 添加更新记录
    recent_update = {
        'projectSlug': project_slug,
        'projectLabel': project_slug,
        'title': title,
        'summary': summary,
        'kind': '快报 / 小更新' if edition_type == 'brief' else '长分析 / 方案稿',
        'activityAt': datetime.now().isoformat(),
        'aggregateUrl': f'/projects/{project_slug}/index.html'
    }
    
    portal_data['recentUpdates'].insert(0, recent_update)
    # 只保留最近 8 条更新
    portal_data['recentUpdates'] = portal_data['recentUpdates'][:8]
    
    # 更新时间戳
    portal_data['generatedAt'] = datetime.now().isoformat()
    
    # 保存更新后的索引
    with open(portal_index_file, 'w', encoding='utf-8') as f:
        json.dump(portal_data, f, ensure_ascii=False, indent=2)
    
    print(f"已更新门户索引: {portal_index_file}")

def main():
    parser = argparse.ArgumentParser(description='创建版次')
    parser.add_argument('--request', required=True, help='请求 JSON 文件路径')
    args = parser.parse_args()
    
    try:
        create_edition(args.request)
        print("版次创建成功!")
        return 0
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
