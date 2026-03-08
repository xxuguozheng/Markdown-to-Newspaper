#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / 'templates'
PORTAL_TEMPLATE = (TEMPLATES / 'portal.html.tpl').read_text(encoding='utf-8')
PROJECT_TEMPLATE = (TEMPLATES / 'project.html.tpl').read_text(encoding='utf-8')
SITE_INDEX = ROOT / 'site' / 'index.html'
PORTAL_DATA = ROOT / 'site' / 'data' / 'portal-index.json'


def clean_text(value):
    return ' '.join(str(value or '').split())


def clip_text(value, limit=140):
    text = clean_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip(' ，。、,.；;：:') + '…'


def format_stamp(value, fallback='—'):
    if not value:
        return fallback
    return str(value).replace('T', ' ')[:16]


def edition_sort_key(item):
    return item.get('publishedAt') or item.get('updatedAt') or ''


def latest_for_project(editions, slug):
    items = [e for e in editions if e['projectSlug'] == slug]
    items.sort(key=edition_sort_key, reverse=True)
    return items


def build_project_signal(project, items):
    latest = items[0] if items else None
    project_updated = project.get('updatedAt') or ''
    aggregate_url = f'/projects/{project["slug"]}/index.html'

    if latest:
        activity = {
            'mode': 'edition',
            'title': latest.get('title') or 'Untitled edition',
            'summary': latest.get('summary') or project.get('summary') or project.get('description') or '',
            'kind': latest.get('densityLabel') or '最新版次',
            'at': edition_sort_key(latest) or project_updated,
            'publishedAt': latest.get('publishedAt'),
            'updatedAt': latest.get('updatedAt'),
            'url': latest.get('htmlUrl') or aggregate_url,
        }
    else:
        activity = {
            'mode': 'project',
            'title': '尚无归档版次',
            'summary': project.get('next') or project.get('summary') or project.get('description') or '项目位已建立，等待首版出刊。',
            'kind': '项目更新',
            'at': project_updated,
            'publishedAt': None,
            'updatedAt': project_updated,
            'url': aggregate_url,
        }

    activity['atText'] = format_stamp(activity['at'])
    return {
        'slug': project['slug'],
        'label': project['label'],
        'description': project.get('description', ''),
        'summary': project.get('summary', ''),
        'stage': project.get('stage') or '待补充',
        'blockers': project.get('blockers', ''),
        'next': project.get('next', ''),
        'updatedAt': project_updated,
        'updatedText': format_stamp(project_updated),
        'editionCount': len(items),
        'aggregateUrl': aggregate_url,
        'activity': activity,
        'items': items,
    }


def render_signal_card(label, value, detail, *, text=False):
    value_class = 'signal-value is-text' if text else 'signal-value'
    shown_value = clip_text(value, 26) if text else value
    shown_detail = clip_text(detail, 42)
    return (
        '<div class="signal-card">'
        f'<small>{escape(str(label))}</small>'
        f'<b class="{value_class}">{escape(str(shown_value))}</b>'
        f'<span>{escape(str(shown_detail))}</span>'
        '</div>'
    )


def render_portal(projects, editions, generated_at):
    project_signals = []
    portal_projects = {}

    for project in projects:
        items = latest_for_project(editions, project['slug'])
        signal = build_project_signal(project, items)
        project_signals.append(signal)

        portal_projects[project['slug']] = {
            'label': signal['label'],
            'description': signal['description'],
            'items': [
                {
                    'name': Path(e['htmlUrl']).name,
                    'title': e['title'],
                    'rawTitle': e['rawTitle'],
                    'summary': e['summary'],
                    'url': e['htmlUrl'],
                    'publishedAt': e.get('publishedAt'),
                    'updatedAt': e['updatedAt'],
                    'size': e['size'],
                    'density': e['density'],
                    'densityLabel': e['densityLabel'],
                }
                for e in items
            ],
            'aggregateUrl': signal['aggregateUrl'],
            'recent': {
                'mode': signal['activity']['mode'],
                'title': signal['activity']['title'],
                'summary': signal['activity']['summary'],
                'kind': signal['activity']['kind'],
                'activityAt': signal['activity']['at'],
                'activityAtText': signal['activity']['atText'],
                'url': signal['activity']['url'],
            },
            'info': {
                'summary': signal['summary'],
                'stage': signal['stage'],
                'blockers': signal['blockers'],
                'updated': signal['updatedText'],
                'next': signal['next'],
            },
        }

    project_signals.sort(key=lambda entry: entry['slug'])
    project_signals.sort(key=lambda entry: (entry['activity']['at'] or '', entry['updatedAt'] or ''), reverse=True)

    total_projects = len(project_signals)
    total_editions = len(editions)
    published_projects = sum(1 for entry in project_signals if entry['editionCount'])
    waiting_projects = total_projects - published_projects
    latest_edition = max(editions, key=edition_sort_key) if editions else None
    project_lookup = {project['slug']: project for project in projects}
    latest_project = max(projects, key=lambda project: project.get('updatedAt', '')) if projects else None

    lead_signal = project_signals[0] if project_signals else None
    lead_title = clip_text(lead_signal['activity']['title'], 56) if lead_signal else '项目门户已刷新'
    lead_summary = (
        clip_text(lead_signal['activity']['summary'], 110)
        if lead_signal
        else '当前没有项目信号可展示。'
    )
    lead_project = lead_signal['label'] if lead_signal else 'OpenClaw Newspaper'
    lead_time = lead_signal['activity']['atText'] if lead_signal else format_stamp(generated_at)
    lead_kind = lead_signal['activity']['kind'] if lead_signal else 'Portal Update'
    lead_url = lead_signal['aggregateUrl'] if lead_signal else '/site/index.html'

    latest_edition_project = project_lookup.get(latest_edition['projectSlug']) if latest_edition else None
    signal_cards = [
        render_signal_card('Projects', total_projects, f'{published_projects} 已出刊 / {waiting_projects} 待首版'),
        render_signal_card('Editions', total_editions, f'最新 {format_stamp(edition_sort_key(latest_edition), generated_at)}'),
        render_signal_card(
            'Updated',
            latest_project['label'] if latest_project else '—',
            format_stamp(latest_project.get('updatedAt') if latest_project else None, generated_at),
            text=True,
        ),
        render_signal_card(
            'Lead Edition',
            clip_text(latest_edition['title'], 26) if latest_edition else '暂无归档版次',
            f'{latest_edition_project["label"] if latest_edition_project else "待补充"} · {format_stamp(edition_sort_key(latest_edition), generated_at)}',
            text=True,
        ),
    ]

    cards = []
    for entry in project_signals:
        count_text = f'{entry["editionCount"]} 版' if entry['editionCount'] else '待首版'
        signal_text = '版次信号' if entry['activity']['mode'] == 'edition' else '项目信号'
        cards.append(
            f'<a class="project-card" href="{escape(entry["aggregateUrl"])}">'
            f'<div class="card-top"><span>{escape(entry["stage"])}</span><span>{escape(count_text)}</span></div>'
            f'<h3>{escape(entry["label"])}</h3>'
            f'<p class="card-description">{escape(clip_text(entry["description"], 60))}</p>'
            f'<div class="activity-block">'
            f'<small>最近动作 · {escape(entry["activity"]["kind"])}</small>'
            f'<b>{escape(clip_text(entry["activity"]["title"], 44))}</b>'
            f'<p>{escape(clip_text(entry["activity"]["summary"], 92))}</p>'
            f'</div>'
            f'<div class="card-footer"><span>{escape(entry["activity"]["atText"])}</span><span>{escape(signal_text)}</span><span>进入项目长页</span></div>'
            f'</a>'
        )

    recent_updates = []
    recent_updates_limit = min(5, len(project_signals))
    for entry in project_signals[:recent_updates_limit]:
        recent_updates.append(
            f'<a class="update-row" href="{escape(entry["aggregateUrl"])}">'
            f'<span class="update-time">{escape(entry["activity"]["atText"])}</span>'
            f'<span class="update-project">{escape(entry["label"])}</span>'
            f'<span class="update-title">{escape(clip_text(entry["activity"]["title"], 36))}</span>'
            f'<span class="update-kind">{escape(entry["activity"]["kind"])}</span>'
            f'<span class="update-summary">{escape(clip_text(entry["activity"]["summary"], 72))}</span>'
            f'</a>'
        )

    board_meta = f'按最近动作排序 · {total_editions} 版归档 · {waiting_projects} 个待首版项目'
    recent_meta = f'最近 {recent_updates_limit} 条 · 按动作时间'
    html = (
        PORTAL_TEMPLATE.replace('{{title}}', 'OpenClaw Newspaper Projects')
        .replace('{{heading}}', '项目总控台')
        .replace('{{dek}}', '把项目入口、头条和值班信号压进一页：先扫头条，再进各项目长页连续读报。')
        .replace('{{heroSignals}}', ''.join(signal_cards))
        .replace('{{leadProject}}', escape(lead_project))
        .replace('{{leadKind}}', escape(lead_kind))
        .replace('{{leadTime}}', escape(lead_time))
        .replace('{{leadTitle}}', escape(lead_title))
        .replace('{{leadSummary}}', escape(lead_summary))
        .replace('{{leadUrl}}', escape(lead_url))
        .replace('{{recentMeta}}', escape(recent_meta))
        .replace('{{recentUpdates}}', ''.join(recent_updates))
        .replace('{{boardMeta}}', escape(board_meta))
        .replace('{{cards}}', ''.join(cards))
        .replace('{{generatedAt}}', generated_at)
    )
    SITE_INDEX.write_text(html, encoding='utf-8')
    PORTAL_DATA.write_text(
        json.dumps(
            {
                'generatedAt': generated_at,
                'stats': {
                    'projectCount': total_projects,
                    'editionCount': total_editions,
                    'publishedProjectCount': published_projects,
                    'waitingProjectCount': waiting_projects,
                    'latestEdition': {
                        'projectSlug': latest_edition['projectSlug'],
                        'title': latest_edition['title'],
                        'publishedAt': latest_edition.get('publishedAt'),
                    }
                    if latest_edition
                    else None,
                    'recentlyUpdatedProject': {
                        'slug': latest_project['slug'],
                        'label': latest_project['label'],
                        'updatedAt': latest_project.get('updatedAt'),
                    }
                    if latest_project
                    else None,
                },
                'recentUpdates': [
                    {
                        'projectSlug': entry['slug'],
                        'projectLabel': entry['label'],
                        'title': entry['activity']['title'],
                        'summary': entry['activity']['summary'],
                        'kind': entry['activity']['kind'],
                        'activityAt': entry['activity']['at'],
                        'aggregateUrl': entry['aggregateUrl'],
                    }
                    for entry in project_signals
                ],
                'projects': portal_projects,
            },
            ensure_ascii=False,
            indent=2,
        )
        + '\n',
        encoding='utf-8',
    )


def render_project(project, projects, editions):
    items = latest_for_project(editions, project['slug'])
    project_dir = ROOT / 'projects' / project['slug']
    project_dir.mkdir(parents=True, exist_ok=True)

    switches = []
    for p in projects:
        cls = 'project-switch is-active' if p['slug'] == project['slug'] else 'project-switch'
        switches.append(f'<a class="{cls}" href="/projects/{p["slug"]}/index.html">{escape(p["label"])}</a>')

    edition_links = []
    edition_sections = []
    for idx, item in enumerate(items, start=1):
        density_name = '头版' if item['density'] == 'longform' else '快报'
        edition_links.append(
            f'<a class="side-link" href="#edition-{idx}"><small>{density_name} · 第 {idx:02d} 版</small><b>{escape(item["title"])}</b><span>{escape(item["publishedAt"].replace("T", " ")[:16])}</span></a>'
        )
        edition_sections.append(
            f'<section class="edition edition-{escape(item["density"])}" id="edition-{idx}">'
            f'<div class="edition-head"><div class="edition-meta"><small>{density_name} · 第 {idx:02d} 版</small><b>{escape(item["title"])}</b><span>{escape(item["publishedAt"].replace("T", " ")[:16])}</span></div>'
            f'<p>{escape(item["summary"])}</p></div>'
            f'<iframe class="edition-frame" src="{escape(item["htmlUrl"])}" loading="lazy" title="{escape(item["title"])}" data-edition-density="{escape(item["density"])}"></iframe>'
            f'</section>'
        )

    hero = items[0] if items else None
    hero_title = f'{hero["title"]}已经挂进报纸系统，直接去读最新版就行。' if hero else '这个项目位还没有报纸版次。'
    hero_summary = hero['summary'] if hero else project['summary']
    hero_links = []
    if hero:
        hero_links.append('<a class="preview-link is-strong" href="#edition-1">直达最新版</a>')
    hero_links.append('<a class="preview-link" href="/site/index.html">项目门户</a>')

    html = PROJECT_TEMPLATE
    replacements = {
        '{{projectLabel}}': escape(project['label']),
        '{{projectSwitches}}': ''.join(switches),
        '{{projectSummary}}': escape(project['summary']),
        '{{projectStage}}': escape(project['stage']),
        '{{editionCount}}': str(len(items)),
        '{{projectUpdated}}': escape(project['updatedAt'].replace('T', ' ')[:16]),
        '{{projectBlockers}}': escape(project['blockers']),
        '{{projectNext}}': escape(project['next']),
        '{{editionLinks}}': ''.join(edition_links),
        '{{heroTitle}}': escape(hero_title),
        '{{heroSummary}}': escape(hero_summary),
        '{{heroLinks}}': ''.join(hero_links),
        '{{editionSections}}': ''.join(edition_sections),
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    (project_dir / 'index.html').write_text(html, encoding='utf-8')


def run_render(projects_path: str | Path, editions_path: str | Path):
    projects_json = json.loads(Path(projects_path).read_text(encoding='utf-8'))
    editions_json = json.loads(Path(editions_path).read_text(encoding='utf-8'))
    projects = projects_json['projects']
    editions = editions_json['editions']
    generated_at = projects_json.get('generatedAt') or editions_json.get('generatedAt') or 'unknown'
    render_portal(projects, editions, generated_at)
    for project in projects:
        render_project(project, projects, editions)
    return len(projects)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--projects', default=str(ROOT / 'data' / 'source' / 'projects.json'))
    parser.add_argument('--editions', default=str(ROOT / 'data' / 'source' / 'editions.json'))
    args = parser.parse_args()
    count = run_render(args.projects, args.editions)
    print(f'rendered portal and {count} project pages')


if __name__ == '__main__':
    main()
