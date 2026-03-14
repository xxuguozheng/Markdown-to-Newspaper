#!/usr/bin/env python3
"""
Markdown to Newspaper HTML converter
Converts custom Markdown syntax to newspaper-style HTML layout
"""

import re
from datetime import datetime

class MarkdownToNewspaper:
    def __init__(self):
        self.current_section = None
        self.in_grid = False
        self.grid_columns = []
        self.current_column = []
    
    def convert(self, markdown):
        """Convert Markdown to newspaper HTML"""
        lines = markdown.strip().split('\n')
        html_parts = []
        
        # Add HTML header
        html_parts.append('''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%(title)s</title>
  <style>
    :root { --paper:#f5f1e8; --ink:#171717; --muted:#665f54; --rule:#1d1d1d; --accent:#0d5b52; --accent-2:#7f1111; --sans:"Inter","PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif; --serif:"Source Han Serif SC","Songti SC","STSong",serif; }
    *{box-sizing:border-box} body{margin:0;background:#ddd6c8;color:var(--ink);font-family:var(--serif);line-height:1.45}
    .page{max-width:1320px;margin:24px auto;background:var(--paper);box-shadow:0 12px 36px rgba(0,0,0,.18);border:1px solid rgba(0,0,0,.16);padding:18px 24px 30px}
    .masthead{border-bottom:4px double var(--rule);padding-bottom:10px;margin-bottom:14px}
    .topline{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font:10px/1.35 var(--sans);letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin-bottom:7px}
    .title{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:end;gap:16px}.title h1{margin:0;font-size:clamp(30px,4.2vw,58px);line-height:.95;font-weight:900;letter-spacing:-.02em;text-transform:uppercase}.edition{font:10px/1.3 var(--sans);text-align:right;color:var(--muted)}
    .strap{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px 12px;font:11px/1.4 var(--sans);color:#25201b}.strap span::before{content:"◆ ";color:var(--accent)}
    .lead-banner{display:grid;grid-template-columns:1.55fr .9fr;gap:18px;border-bottom:1px solid rgba(0,0,0,.78);padding-bottom:14px;margin-bottom:16px}.lead-banner h2{margin:0 0 8px;font-size:clamp(28px,3vw,44px);line-height:1.02}.lead-banner p{margin:0;font-size:15px;line-height:1.55}
    .summary-card{background:rgba(255,255,255,.45);border-left:4px solid var(--accent);padding:12px 13px}.summary-card small{display:block;font:10px/1.35 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:5px}.summary-card b{display:block;font:800 16px/1.35 var(--sans);margin-bottom:6px}.summary-card p{font:13px/1.65 var(--sans);color:#2b251f}
    .grid{display:grid;grid-template-columns:1.42fr 1fr 1fr;gap:18px}.story{border-top:1px solid rgba(0,0,0,.72);padding-top:10px;margin-bottom:16px}.story.lead{border-top:none;padding-top:0}
    .kicker{font:10px/1.3 var(--sans);text-transform:uppercase;letter-spacing:.1em;color:var(--accent-2);font-weight:800;margin-bottom:5px}.headline{margin:0 0 7px;font-size:clamp(24px,2.5vw,38px);line-height:1.02;font-weight:900}.headline.small{font-size:23px;line-height:1.08}.dek{margin:0 0 10px;font-size:15px;line-height:1.45;color:#25201b}.meta{margin-bottom:10px;font:11px/1.45 var(--sans);color:var(--muted)}
    .body{font-size:14.5px;line-height:1.58;text-align:justify;column-count:2;column-gap:18px}.body.single{column-count:1}.body p{margin:0 0 10px}
    .briefs{display:grid;gap:10px}.brief{border-left:3px solid var(--rule);padding-left:10px;font-size:12.5px;line-height:1.52}.brief b{display:block;font:700 11px/1.3 var(--sans);letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px}
    .box{border:1px solid rgba(0,0,0,.75);background:rgba(255,255,255,.28);padding:10px 11px;margin-bottom:16px}.box h3{margin:0 0 8px;font:800 13px/1.35 var(--sans);text-transform:uppercase;letter-spacing:.07em}
    .list{margin:0;padding-left:18px;font-size:12.5px;line-height:1.5}.list li{margin-bottom:6px}.quote{font-size:16px;line-height:1.32;font-weight:700;padding:10px 0;border-top:1px dashed rgba(0,0,0,.5);border-bottom:1px dashed rgba(0,0,0,.5);margin:10px 0}.tag{display:inline-block;padding:1px 6px;border:1px solid rgba(0,0,0,.6);font:10px/1.35 var(--sans);margin:0 5px 5px 0}
    .footer{margin-top:16px;padding-top:10px;border-top:3px double var(--rule);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font:10px/1.5 var(--sans);color:var(--muted)}
    @media (max-width:1024px){.grid{grid-template-columns:1.35fr 1fr}.grid>.col:last-child{grid-column:1/-1}.lead-banner{grid-template-columns:1fr}} @media (max-width:760px){.page{margin:0;min-height:100vh}.title{grid-template-columns:1fr}.edition{text-align:left}.grid{grid-template-columns:1fr}.body{column-count:1}}
  </style>
</head>
<body>
  <main class="page">''' % {'title': self._extract_title(markdown)})
        
        # First pass: extract all content sections
        sections = self._parse_sections(lines)
        
        # Generate masthead and lead banner
        html_parts.append(self._generate_masthead(sections['title'], sections['headline'], sections['lead_text']))
        
        # Generate grid with all content
        html_parts.append(self._generate_full_grid(sections))
        
        # Add HTML footer
        html_parts.append('''  </main>
  <footer class="footer">
    <span>OpenClaw Newspaper</span>
    <span>Generated on %(date)s</span>
    <span>Edition</span>
  </footer>
</body>
</html>''' % {'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        
        return '\n'.join(html_parts)
    
    def _parse_sections(self, lines):
        """Parse markdown into sections"""
        sections = {
            'title': '',
            'headline': '',
            'lead_text': '',
            'kicker': '',
            'meta': '',
            'body_content': [],
            'box_content': [],
            'list_items': [],
            'quote_content': '',
            'columns': [[], [], []]  # Three columns for grid layout
        }
        
        current_column = 0
        in_box = False
        box_title = ''
        box_content = []
        in_quote = False
        quote_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('# '):
                sections['title'] = line[2:].strip()
            elif line.startswith('## '):
                sections['kicker'] = line[3:].strip()
            elif line.startswith('### '):
                if not sections['headline']:
                    sections['headline'] = line[4:].strip()
                    # Look for lead text
                    for j in range(i+1, min(i+6, len(lines))):
                        if lines[j].startswith('> '):
                            sections['lead_text'] = lines[j][2:].strip()
                            break
                else:
                    # Additional headlines go to body
                    sections['body_content'].append(f'<h3>{line[4:].strip()}</h3>')
            elif line.startswith('> '):
                if not sections['lead_text']:
                    sections['lead_text'] = line[2:].strip()
            elif line.startswith('**') and line.endswith('**'):
                sections['meta'] = line[2:-2].strip()
            elif line.startswith(':::box '):
                in_box = True
                box_title = line[7:].strip()
                box_content = []
            elif line == ':::' and in_box:
                in_box = False
                sections['box_content'].append({'title': box_title, 'content': ' '.join(box_content)})
            elif in_box:
                box_content.append(line)
            elif line.startswith(':::quote'):
                in_quote = True
                quote_lines = []
            elif line == ':::' and in_quote:
                in_quote = False
                sections['quote_content'] = ' '.join(quote_lines)
            elif in_quote:
                quote_lines.append(line)
            elif line.startswith('- '):
                sections['list_items'].append(line[2:].strip())
            elif line == '|||':
                current_column += 1
                if current_column >= 3:
                    current_column = 0
            elif line and not line.startswith('#') and not line.startswith('---'):
                # Regular paragraph
                if current_column < 3:
                    sections['columns'][current_column].append(line)
                else:
                    sections['body_content'].append(f'<p>{line}</p>')
            
            i += 1
        
        return sections
    
    def _generate_masthead(self, title, headline, lead_text):
        """Generate masthead HTML"""
        today = datetime.now().strftime('%Y-%m-%d')
        main_title = title.split(' · ')[0] if ' · ' in title else title
        edition = title.split(' · ')[1] if ' · ' in title else 'Edition'
        
        if not headline:
            headline = main_title
        if not lead_text:
            lead_text = "本版包含深度分析、专业见解和实用指南，为您提供全面的信息。"
        
        return f'''
    <header class="masthead">
      <div class="topline">
        <span>OpenClaw Newspaper</span>
        <span>{title}</span>
        <span>{today}</span>
      </div>
      <div class="title">
        <h1>{main_title}</h1>
        <div class="edition">{edition}</div>
      </div>
      <div class="strap">
        <span>深度解析</span>
        <span>专业分析</span>
        <span>实用指南</span>
      </div>
    </header>

    <section class="lead-banner">
      <div>
        <div class="kicker">Front Page</div>
        <h2>{headline}</h2>
        <p>{lead_text}</p>
      </div>
      <aside class="summary-card">
        <small>本期摘要</small>
        <b>核心内容概览</b>
        <p>本版包含深度分析、专业见解和实用指南，为您提供全面的信息。</p>
      </aside>
    </section>'''
    
    def _generate_full_grid(self, sections):
        """Generate full grid layout with all content"""
        grid_html = ['    <section class="grid">']
        
        # Column 1: Main content
        col1_content = []
        if sections['kicker']:
            col1_content.append(f'<div class="kicker">{sections["kicker"]}</div>')
        if sections['headline']:
            col1_content.append(f'<h2 class="headline">{sections["headline"]}</h2>')
        if sections['lead_text']:
            col1_content.append(f'<p class="dek">{sections["lead_text"]}</p>')
        if sections['meta']:
            col1_content.append(f'<div class="meta">{sections["meta"]}</div>')
        
        # Add body content
        for item in sections['body_content']:
            col1_content.append(item)
        
        # Add first column paragraphs
        for para in sections['columns'][0]:
            col1_content.append(f'<p>{para}</p>')
        
        # Add box content
        for box in sections['box_content']:
            col1_content.append(f'<div class="box"><h3>{box["title"]}</h3><p>{box["content"]}</p></div>')
        
        col1_html = '\n'.join(col1_content)
        grid_html.append(f'''      <div class="col">
        <article class="story lead">
          <div class="body">
{col1_html}
          </div>
        </article>
      </div>''')
        
        # Column 2: Secondary content or list items
        col2_content = []
        col2_content.append('<div class="kicker">朋友版 · What To Watch</div>')
        col2_content.append('<h2 class="headline small">快速指南</h2>')
        col2_content.append('<p class="dek">实用的操作建议和注意事项</p>')
        
        # Add list items as briefs
        if sections['list_items']:
            col2_content.append('<div class="briefs">')
            for item in sections['list_items'][:6]:  # Limit to 6 items
                col2_content.append(f'<div class="brief"><b>要点</b>{item}</div>')
            col2_content.append('</div>')
        
        # Add second column paragraphs
        for para in sections['columns'][1]:
            col2_content.append(f'<p>{para}</p>')
        
        col2_html = '\n'.join(col2_content)
        grid_html.append(f'''      <div class="col">
        <article class="story">
{col2_html}
        </article>
      </div>''')
        
        # Column 3: Additional info
        col3_content = []
        col3_content.append('<div class="kicker">快扫栏 · Radar Rail</div>')
        col3_content.append('<h2 class="headline small">关键数据</h2>')
        col3_content.append('<div class="box"><h3>平台优势</h3><ul class="list"><li>零技术门槛</li><li>全场景CPS</li><li>工具化操作</li><li>合规安全</li></ul></div>')
        
        # Add quote if exists
        if sections['quote_content']:
            col3_content.append(f'<div class="quote">{sections["quote_content"]}</div>')
        
        # Add third column paragraphs
        for para in sections['columns'][2]:
            col3_content.append(f'<p>{para}</p>')
        
        col3_html = '\n'.join(col3_content)
        grid_html.append(f'''      <div class="col">
        <article class="story">
{col3_html}
        </article>
      </div>''')
        
        grid_html.append('    </section>')
        return '\n'.join(grid_html)
    
    def _extract_title(self, markdown):
        """Extract title from markdown"""
        for line in markdown.split('\n'):
            if line.startswith('# '):
                return line[2:].strip()
        return 'Newspaper Edition'

def main():
    """Main function"""
    import sys
    if len(sys.argv) != 3:
        print("Usage: python markdown_to_newspaper.py <input.md> <output.html>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown = f.read()
    
    converter = MarkdownToNewspaper()
    html = converter.convert(markdown)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Converted {input_file} to {output_file}")

if __name__ == '__main__':
    main()
