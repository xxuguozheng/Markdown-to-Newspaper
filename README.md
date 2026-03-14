# Markdown-to-Newspaper

一个将 Markdown 内容转换为报纸风格排版的静态网站生成工具，支持项目管理、版次创建和响应式布局。

## 项目简介

Markdown-to-Newspaper 是一个基于静态 HTML 的报纸风格内容管理系统，它允许用户：

- 通过 Markdown 编辑器创建和管理内容
- 自动将 Markdown 转换为报纸风格的 HTML 排版
- 支持多栏布局、响应式设计和视觉层次
- 提供项目管理界面，支持创建项目和版次
- 本地运行，无需服务器部署

## 功能特性

- **Markdown 转报纸排版**：自动将 Markdown 内容转换为具有报纸风格的 HTML 页面
- **项目管理**：创建和管理项目，每个项目可以包含多个版次
- **版次管理**：为项目创建多个版次，每个版次都有独立的内容和布局
- **响应式设计**：适配不同屏幕尺寸，在桌面、平板和移动设备上都有良好的显示效果
- **多栏布局**：支持三栏网格布局，模拟真实报纸的排版效果
- **视觉层次**：通过标题层级、引用块、信息框等元素创建清晰的视觉层次
- **本地运行**：使用 Python 内置的 HTTP 服务器即可本地运行

## 快速开始

### 环境要求

- Python 3.6+
- 现代浏览器（Chrome、Firefox、Safari、Edge 等）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/xxuguozheng/Markdown-to-Newspaper.git
   cd Markdown-to-Newspaper
   ```

2. **启动本地服务器**
   ```bash
   python -m http.server 8000
   ```

3. **启动管理 API**（可选）
   ```bash
   python scripts/admin_api.py
   ```

4. **访问系统**
   - 主门户：http://localhost:8000/site/index.html
   - 项目管理：http://localhost:8000/site/admin/index.html

## 项目结构

```
├── data/                  # 数据目录
│   ├── source/            # 唯一数据源
│   │   ├── projects.json  # 项目数据
│   │   └── editions.json  # 版次数据
│   ├── receipts/          # 发布回执
│   └── requests/          # 发布请求
├── projects/              # 按项目归档的报纸页
│   └── [项目名]/          # 项目目录
│       └── [版次].html    # 版次页面
├── scripts/               # 脚本目录
│   ├── markdown_to_newspaper.py  # Markdown 转报纸排版
│   ├── render_newspaper.py       # 渲染页面
│   ├── publish_to_newspaper.py   # 发布流水线
│   └── admin_api.py              # 管理 API
├── site/                  # 网站目录
│   ├── index.html         # 主门户页面
│   └── admin/             # 管理界面
├── templates/             # 模板目录
└── README.md              # 项目说明
```

## 核心功能

### 1. Markdown 编辑器

在项目管理界面中，用户可以使用 Markdown 编辑器创建和编辑内容。系统会自动将 Markdown 转换为报纸风格的 HTML 排版。

### 2. 项目管理

- 创建新项目，设置项目名称、描述、摘要等信息
- 管理项目的状态和阶段
- 查看项目的所有版次

### 3. 版次管理

- 为项目创建新的版次
- 设置版次标题、摘要和内容密度
- 自动生成版次 ID 和 HTML 文件

### 4. 报纸风格排版

- 三栏网格布局
- 响应式设计（桌面、平板、移动设备）
- 支持标题层级、引用块、信息框等元素
- 自动生成导航和目录

## 技术栈

- **前端**：HTML5, CSS3, JavaScript
- **后端**：Python 3
- **数据存储**：JSON 文件
- **服务器**：Python 内置 HTTP 服务器

## 常用命令

```bash
# 1. 从旧 portal-index 回填真源
python scripts/seed_source_data.py

# 2. 用真源重渲染门户与项目页
python scripts/render_newspaper.py

# 3. 发布一篇新报纸
python scripts/publish_to_newspaper.py --request data/requests/example-publish-request.json

# 4. 新建项目（dry-run）
python scripts/project_interface.py --action create_project --request examples/create-project-test-2026-03-08.json --dry-run

# 5. 新建项目（真实写入）
python scripts/project_interface.py --action create_project --request examples/create-project-test-2026-03-08.json

# 6. 更新项目元信息
python scripts/project_interface.py --action update_project_meta --request examples/update-project-meta-test-2026-03-08.json
```

## Markdown 语法扩展

系统支持以下 Markdown 语法扩展：

- **多栏布局**：使用 `|||` 分隔符创建多栏内容
- **引用块**：使用 `:::quote` 标记创建引用块
- **信息框**：使用 `:::box` 标记创建信息框
- **标题层级**：支持 H1-H6 标题
- **列表**：有序列表和无序列表
- **链接**：支持内联链接和引用链接
- **图片**：支持图片嵌入

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目。

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 鸣谢

本项目基于 [OpenClaw-Newspaper](https://github.com/Vimalinx-zero/OpenClaw-Newspaper) 项目进行开发和扩展，感谢原作者的贡献和开源精神。

## 联系方式

- 项目地址：https://github.com/xxuguozheng/Markdown-to-Newspaper
- 原项目地址：https://github.com/Vimalinx-zero/OpenClaw-Newspaper