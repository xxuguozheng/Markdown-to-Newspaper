#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Dict, Any

def parse_markdown_to_project(markdown_text: str) -> Dict[str, Any]:
    """
    将 Markdown 格式的项目信息转换为项目数据格式
    
    Markdown 格式要求：
    # 项目名称
    ## 摘要
    ## 阶段
    ## 阻塞与问题
    ## 下一步计划
    ## 正文内容
    """
    result = {
        'label': '',
        'summary': '',
        'stage': '待补充',
        'blockers': '',
        'next': '',
        'description': '',
        'content_html': ''
    }
    
    # 分割 Markdown 内容
    lines = markdown_text.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        # 检测一级标题（项目名称）
        if line.startswith('# ') and not line.startswith('##'):
            result['label'] = line[2:].strip()
            current_section = None
            continue
        
        # 检测二级标题
        if line.startswith('## '):
            section_name = line[3:].strip()
            
            # 保存上一个section的内容
            if current_section and current_content:
                content = '\n'.join(current_content).strip()
                if current_section == '摘要':
                    result['summary'] = content
                elif current_section == '阶段':
                    result['stage'] = content
                elif current_section == '阻塞与问题':
                    result['blockers'] = content
                elif current_section == '下一步计划':
                    result['next'] = content
                elif current_section == '正文内容':
                    result['description'] = content
                    result['content_html'] = convert_markdown_to_html(content)
            
            current_section = section_name
            current_content = []
        else:
            if current_section:
                current_content.append(line)
    
    # 处理最后一个section
    if current_section and current_content:
        content = '\n'.join(current_content).strip()
        if current_section == '摘要':
            result['summary'] = content
        elif current_section == '阶段':
            result['stage'] = content
        elif current_section == '阻塞与问题':
            result['blockers'] = content
        elif current_section == '下一步计划':
            result['next'] = content
        elif current_section == '正文内容':
            result['description'] = content
            result['content_html'] = convert_markdown_to_html(content)
    
    return result

def convert_markdown_to_html(markdown_text: str) -> str:
    """
    简单的 Markdown 到 HTML 转换器
    保持报纸样式的排版
    """
    if not markdown_text:
        return ''
    
    html = markdown_text
    
    # 转换标题
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    
    # 转换粗体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # 转换斜体
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # 转换列表
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', html)
    
    # 转换段落
    html = re.sub(r'\n\n+', '</p><p>', html)
    html = f'<p>{html}</p>'
    
    # 清理空标签
    html = re.sub(r'<p></p>', '', html)
    
    return html

def generate_newspaper_html(project_data: Dict[str, Any], project_slug: str) -> str:
    """
    生成报纸样式的 HTML
    """
    label = project_data.get('label', '未命名项目')
    summary = project_data.get('summary', '')
    content_html = project_data.get('content_html', '')
    
    # 生成报纸样式 HTML
    newspaper_html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{label}</title>
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
    <div class="topline">OpenClaw Newspaper · {project_slug}</div>
    <h1>{label}</h1>
    <div class="summary">{summary}</div>
    <article class="body">{content_html}</article>
  </main>
</body>
</html>'''
    
    return newspaper_html

if __name__ == '__main__':
    # 测试 Markdown 转换
    test_markdown = '''# 测试项目

## 摘要
这是一个测试项目的摘要，用于验证 Markdown 转换功能。

## 阶段
开发阶段

## 阻塞与问题
暂无阻塞

## 下一步计划
继续开发

## 正文内容
这是正文内容的第一段。

### 子标题
这是正文内容的子标题部分。

- 列表项1
- 列表项2
- **粗体文本**
- *斜体文本*

这是正文内容的最后一段。'''
    
    result = parse_markdown_to_project(test_markdown)
    print("转换结果:")
    print(result)
    print("\n生成的报纸 HTML:")
    print(generate_newspaper_html(result, 'test-project'))