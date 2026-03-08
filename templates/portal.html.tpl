<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{{title}}</title>
<style>
:root{--paper:#f2eadc;--paper-2:#ebdfcc;--ink:#151515;--muted:#645d54;--soft:#8e8476;--rule:#1e1a15;--accent:#7d1111;--panel:#f7f0e4;--shadow:0 14px 38px rgba(0,0,0,.15);--sans:"Inter","PingFang SC","Noto Sans CJK SC",sans-serif;--serif:"Source Han Serif SC","Songti SC","STSong",serif;--mono:"JetBrains Mono","SFMono-Regular","Consolas",monospace;}
*{box-sizing:border-box;}html{scroll-behavior:smooth;}body{margin:0;background:radial-gradient(circle at top, rgba(255,255,255,.32), transparent 38%),#d8cdb9;color:var(--ink);font-family:var(--serif);}a{color:inherit}
.page{max-width:1500px;margin:14px auto;background:linear-gradient(180deg,var(--paper),var(--paper-2));border:1px solid rgba(0,0,0,.22);box-shadow:var(--shadow);padding:16px 20px 22px;}
.topline,.section-kicker,.panel-note,.board-note{font:10px/1.45 var(--sans);letter-spacing:.14em;text-transform:uppercase;}.topline{color:var(--muted);margin-bottom:6px;}.section-kicker{color:var(--accent);}h1{margin:0;font-size:clamp(34px,4.4vw,56px);line-height:.88;letter-spacing:.01em;}.dek{margin-top:7px;max-width:780px;font:13px/1.55 var(--sans);color:#302922;}
.masthead{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(320px,.95fr);gap:14px;align-items:end;border-bottom:3px double var(--rule);padding-bottom:10px;margin-bottom:10px;}
.signal-board{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px 12px;align-content:flex-end;padding-bottom:2px;}.signal-card{display:grid;grid-template-columns:auto auto;gap:2px 8px;align-items:baseline;min-width:0;padding-left:12px;position:relative;}.signal-card::before{content:"";position:absolute;left:0;top:2px;bottom:2px;width:1px;background:rgba(0,0,0,.14);}.signal-card:first-child{padding-left:0;}.signal-card:first-child::before{display:none;}.signal-card small{font:10px/1.4 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);}.signal-card .signal-value{font:700 16px/1 var(--sans);white-space:nowrap;}.signal-card .signal-value.is-text{font-size:12px;max-width:178px;overflow:hidden;text-overflow:ellipsis;}.signal-card span{grid-column:1 / -1;font:10px/1.35 var(--sans);color:#4f4538;max-width:220px;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:1;overflow:hidden;}
.lead-story{position:relative;overflow:hidden;border:1px solid rgba(0,0,0,.16);background:linear-gradient(180deg,rgba(255,255,255,.58),rgba(255,255,255,.30));padding:11px 14px 10px 18px;margin-bottom:10px;}.lead-story::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:linear-gradient(180deg,var(--accent),#260404);}.lead-strip{display:flex;flex-wrap:wrap;gap:8px 12px;font:10px/1.45 var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);}.lead-story h2{margin:6px 0 6px;font-size:clamp(22px,2.6vw,32px);line-height:1.05;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;}.lead-story p{margin:0;max-width:980px;font:13px/1.55 var(--sans);color:#312b24;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;}.lead-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;}.lead-link{display:inline-flex;align-items:center;justify-content:center;padding:7px 10px;border:1px solid rgba(0,0,0,.2);background:rgba(255,255,255,.44);text-decoration:none;font:11px/1.35 var(--sans);}.lead-link.is-strong{background:var(--ink);color:var(--paper);border-color:var(--ink);}
.newsroom{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(260px,.6fr);gap:14px;align-items:start;}.board-column{min-width:0;}.board-head{display:flex;justify-content:space-between;align-items:end;gap:12px;padding:0 0 8px;margin:0 0 10px;border-top:3px double var(--rule);border-bottom:1px solid rgba(0,0,0,.18);}.board-head h2{margin:4px 0 0;font-size:28px;line-height:1;}.board-note{text-align:right;color:var(--muted);}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;}.project-card{display:flex;flex-direction:column;gap:8px;min-height:100%;padding:12px 12px 11px;border:1px solid rgba(0,0,0,.16);background:linear-gradient(180deg,rgba(255,255,255,.58),rgba(255,255,255,.22));text-decoration:none;box-shadow:0 8px 22px rgba(0,0,0,.05);position:relative;}.project-card::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,var(--accent),rgba(18,18,18,.94));}.card-top,.card-footer{display:flex;justify-content:space-between;gap:8px;font:10px/1.4 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);}.project-card h3{margin:0;font-size:20px;line-height:1.04;}.card-description{margin:0;font:12px/1.5 var(--sans);color:#302922;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;}.activity-block{padding:8px 9px;border-left:2px solid var(--accent);background:rgba(23,18,14,.05);}.activity-block small{display:block;font:10px/1.4 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;}.activity-block b{display:block;font:700 14px/1.3 var(--serif);margin-bottom:4px;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;}.activity-block p{margin:0;font:11px/1.5 var(--sans);color:#342d26;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;overflow:hidden;}.card-footer{margin-top:auto;padding-top:7px;border-top:1px dotted rgba(0,0,0,.18);}
.updates-panel{border:1px solid rgba(0,0,0,.16);background:linear-gradient(180deg,rgba(255,255,255,.58),rgba(255,255,255,.34));padding:11px 13px;}.panel-head{display:flex;justify-content:space-between;align-items:end;gap:10px;margin-bottom:6px;}.panel-head h2{margin:4px 0 0;font-size:24px;line-height:1;}.panel-note{color:var(--muted);text-align:right;}.updates-list{display:grid;gap:0;border-top:1px solid rgba(0,0,0,.12);}.update-row{display:grid;grid-template-columns:84px minmax(0,1fr);gap:2px 10px;padding:8px 0;border-bottom:1px dotted rgba(0,0,0,.18);text-decoration:none;align-items:start;}.update-row:last-child{border-bottom:0;}.update-time{grid-row:1 / span 4;font:10px/1.45 var(--mono);color:var(--muted);}.update-project{grid-column:2;font:700 12px/1.35 var(--sans);}.update-title{grid-column:2;font:700 14px/1.28 var(--serif);}.update-kind{grid-column:2;justify-self:start;font:10px/1.35 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--accent);}.update-summary{grid-column:2;font:11px/1.45 var(--sans);color:#342d26;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;}
.footer{margin-top:14px;padding-top:8px;border-top:3px double var(--rule);font:10px/1.5 var(--mono);color:var(--muted);}
@media (max-width:1380px){.grid{grid-template-columns:repeat(3,minmax(0,1fr));}}
@media (max-width:1120px){.masthead,.newsroom{grid-template-columns:1fr;}.signal-board{justify-content:flex-start;border-top:1px solid rgba(0,0,0,.12);padding-top:8px;}}
@media (max-width:820px){.page{padding:14px 16px 20px;}.grid{grid-template-columns:repeat(2,minmax(0,1fr));}.board-head,.panel-head{flex-direction:column;align-items:start;}.board-note,.panel-note{text-align:left;}}
@media (max-width:640px){.page{margin:0;padding:14px 12px 20px;border-left:0;border-right:0;}.signal-board{display:grid;grid-template-columns:1fr;justify-content:stretch;gap:8px;}.signal-card{padding-left:0;padding-top:6px;border-top:1px solid rgba(0,0,0,.12);}.signal-card::before{display:none;}.signal-card:first-child{padding-top:0;border-top:0;}.grid{grid-template-columns:1fr;}.update-row{grid-template-columns:70px minmax(0,1fr);}}
</style>
</head>
<body>
<main class="page">
<header class="masthead">
  <div>
    <div class="topline">OpenClaw Newspaper Portal</div>
    <h1>{{heading}}</h1>
    <div class="dek">{{dek}}</div>
  </div>
  <div class="signal-board">{{heroSignals}}</div>
</header>
<section class="lead-story">
  <div class="section-kicker">Lead Signal</div>
  <div class="lead-strip">
    <span>{{leadProject}}</span>
    <span>{{leadKind}}</span>
    <span>{{leadTime}}</span>
  </div>
  <h2>{{leadTitle}}</h2>
  <p>{{leadSummary}}</p>
  <div class="lead-links">
    <a class="lead-link is-strong" href="{{leadUrl}}">进入这个项目</a>
    <a class="lead-link" href="#project-board">查看项目板</a>
  </div>
</section>
<section class="newsroom">
  <div class="board-column">
    <section class="board-head" id="project-board">
      <div>
        <div class="section-kicker">Project Board</div>
        <h2>项目值班台</h2>
      </div>
      <div class="board-note">{{boardMeta}}</div>
    </section>
    <section class="grid">{{cards}}</section>
  </div>
  <aside class="updates-panel">
    <div class="panel-head">
      <div>
        <div class="section-kicker">Recent Updates</div>
        <h2>最近动态</h2>
      </div>
      <div class="panel-note">{{recentMeta}}</div>
    </div>
    <div class="updates-list">{{recentUpdates}}</div>
  </aside>
</section>
<footer class="footer">Generated {{generatedAt}}</footer>
</main>
</body>
</html>
