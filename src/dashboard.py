"""Dashboard — returns a complete HTML string for a multi-page screen time dashboard.
Theme: macaron day — Cinnamoroll-inspired Glassmorphism with swipeable pages.
"""


def render_dashboard() -> str:
    return r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>&#x5c4f;&#x5e55;&#x72b6;&#x6001;&#x8ffd;&#x8e2a;</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700;900&family=ZCOOL+XiaoWei&display=swap');

*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}

:root{
  --bg-start:#d4e8f5;
  --bg-mid:#b8d8ee;
  --bg-end:#a8d0e0;
  --card-bg:rgba(255,255,255,0.65);
  --card-border:rgba(180,220,245,0.4);
  --card-shadow:0 8px 32px rgba(120,180,220,0.15);
  --text:#3a5068;
  --text-dim:#8ba4b8;
  --text-light:#b0c8d8;
  --primary:#7ec8e3;
  --primary-light:#b8e4f0;
  --secondary:#a8e6cf;
  --accent-pink:#ffc0cb;
  --success:#8ee4af;
  --warning:#ffe4a0;
  --danger:#ffb4b4;
  --gradient:linear-gradient(135deg,#7ec8e3,#a8e6cf);
  --gradient-warm:linear-gradient(135deg,#b8e4f0,#ffd6e0);
}

html,body{height:100%;overflow:hidden}

body{
  font-family:'Zen Maru Gothic',-apple-system,BlinkMacSystemFont,sans-serif;
  color:var(--text);
  background:linear-gradient(135deg,var(--bg-start),var(--bg-mid),var(--bg-end),var(--bg-start));
  background-size:400% 400%;
  animation:bgFlow 20s ease infinite;
  position:relative;
}

@keyframes bgFlow{
  0%{background-position:0% 50%}
  25%{background-position:100% 0%}
  50%{background-position:100% 50%}
  75%{background-position:0% 100%}
  100%{background-position:0% 50%}
}

/* Kaomoji watermark layer */
.kaomoji-bg{
  position:fixed;top:0;left:0;width:100%;height:100%;
  pointer-events:none;z-index:0;overflow:hidden;
}
.kaomoji-bg span{
  position:absolute;
  color:#3a5068;
  font-family:'Zen Maru Gothic',sans-serif;
  animation:kaomojiFade 30s ease-in-out infinite;
}
@keyframes kaomojiFade{
  0%,100%{transform:translateY(0)}
  50%{transform:translateY(-12px)}
}

/* Animations */
@keyframes fadeInUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes countPop{from{opacity:0;transform:scale(0.8)}to{opacity:1;transform:scale(1)}}
@keyframes breatheGlow{
  0%,100%{box-shadow:0 8px 32px rgba(120,180,220,0.15),0 0 20px rgba(142,228,175,0.15)}
  50%{box-shadow:0 8px 32px rgba(120,180,220,0.15),0 0 40px rgba(142,228,175,0.25),0 0 60px rgba(142,228,175,0.1)}
}
@keyframes livePulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.6;transform:scale(0.85)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes barGrow{from{width:0}}
@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(-20px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
@keyframes toastOut{from{opacity:1;transform:translateX(-50%) translateY(0)}to{opacity:0;transform:translateX(-50%) translateY(-20px)}}
@keyframes navDotSlide{from{opacity:0;transform:scale(0)}to{opacity:1;transform:scale(1)}}
@keyframes weekBarGrow{from{height:4px}to{height:var(--bar-h)}}

/* Pages container */
.pages-container{
  display:flex;
  width:500vw;
  height:calc(100vh - 56px);
  overflow-x:auto;
  overflow-y:hidden;
  scroll-snap-type:x mandatory;
  scroll-behavior:smooth;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:none;
  position:relative;z-index:1;
}
.pages-container::-webkit-scrollbar{display:none}

.page{
  width:100vw;
  min-width:100vw;
  height:100%;
  overflow-y:auto;
  overflow-x:hidden;
  scroll-snap-align:start;
  padding:24px 16px 30px;
  scrollbar-width:thin;
  scrollbar-color:rgba(126,200,227,0.2) transparent;
}
.page::-webkit-scrollbar{width:4px}
.page::-webkit-scrollbar-track{background:transparent}
.page::-webkit-scrollbar-thumb{background:rgba(126,200,227,0.25);border-radius:2px}

.page-inner{max-width:480px;margin:0 auto}

/* Glass card base */
.glass{
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:24px;
  box-shadow:var(--card-shadow);
  transition:all 0.35s cubic-bezier(0.22,1,0.36,1);
}
.glass:hover{
  transform:translateY(-3px);
  box-shadow:0 12px 40px rgba(120,180,220,0.22);
  border-color:rgba(180,220,245,0.6);
}

/* Page titles */
.page-title{
  font-family:'ZCOOL XiaoWei','Zen Maru Gothic',serif;
  font-size:1.8em;
  color:var(--text);
  text-align:center;
  margin-bottom:4px;
}
.page-subtitle{
  font-size:0.85em;
  color:var(--text-dim);
  text-align:center;
  margin-bottom:20px;
  font-weight:500;
}

/* Night owl & all-nighter alerts */
.alert-card{
  padding:18px 20px;border-radius:20px;margin-bottom:14px;display:none;
  animation:fadeInUp 0.4s ease;text-align:center;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
}
.alert-card.show{display:block}

.night-owl-alert{
  background:rgba(255,228,160,0.35);
  border:1px solid rgba(255,228,160,0.5);
}
.night-owl-alert .alert-text{color:#7a6830;font-size:0.88em;font-weight:500}

.all-nighter-alert{
  background:rgba(255,180,180,0.3);
  border:1px solid rgba(255,180,180,0.5);
}
.all-nighter-alert .alert-text{color:#8a4444;font-size:0.88em;font-weight:700}

/* Current time display */
.time-display{
  text-align:center;margin-bottom:16px;
  font-size:0.82em;color:var(--text-dim);font-weight:500;
  display:flex;align-items:center;justify-content:center;gap:8px;
}
.status-dot{
  width:8px;height:8px;border-radius:50%;
  background:var(--success);animation:livePulse 2s ease infinite;
  display:inline-block;
}
.status-dot.idle{background:var(--text-dim);animation:none}

/* Current activity card */
.current-card{
  padding:22px;border-radius:24px;
  background:rgba(142,228,175,0.12);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid rgba(142,228,175,0.25);
  margin-bottom:16px;display:none;
  animation:breatheGlow 3s ease-in-out infinite;
}
.current-card.show{display:block}
.current-label{display:flex;align-items:center;gap:8px;font-size:0.78em;font-weight:700;letter-spacing:1px}
.current-label .badge-live{
  display:inline-flex;align-items:center;gap:6px;
  background:rgba(142,228,175,0.2);color:#4a8a6a;
  padding:4px 14px;border-radius:50px;
  border:1px solid rgba(142,228,175,0.4);
  font-size:1em;
}
.current-label .live-dot{width:8px;height:8px;border-radius:50%;background:var(--success);animation:livePulse 1.5s ease infinite}
.current-app{font-size:1.4em;font-weight:700;margin-top:10px;color:var(--text)}
.current-duration{color:#4a8a6a;font-size:1.05em;margin-top:6px;font-variant-numeric:tabular-nums;font-weight:500}
.idle-message{
  text-align:center;padding:20px;margin-bottom:16px;
  font-size:0.92em;color:var(--text-dim);font-weight:500;
  background:var(--card-bg);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);border-radius:24px;
  box-shadow:var(--card-shadow);display:none;
}
.idle-message.show{display:block}

/* Stats grid 2x2 */
.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:16px}
.stat-card{
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:24px;padding:20px 16px;
  text-align:center;position:relative;overflow:hidden;
  box-shadow:var(--card-shadow);
  transition:all 0.35s cubic-bezier(0.22,1,0.36,1);
  animation:fadeInUp 0.5s ease backwards;
}
.stat-card:nth-child(1){animation-delay:0.08s}
.stat-card:nth-child(2){animation-delay:0.16s}
.stat-card:nth-child(3){animation-delay:0.24s}
.stat-card:nth-child(4){animation-delay:0.32s}
.stat-card:hover{
  transform:translateY(-3px);
  box-shadow:0 12px 40px rgba(120,180,220,0.22);
  border-color:rgba(180,220,245,0.6);
}
.stat-icon{
  width:44px;height:44px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 10px;
}
.stat-icon svg{width:22px;height:22px}
.stat-icon.c1{background:rgba(126,200,227,0.15)}
.stat-icon.c1 svg{stroke:#7ec8e3}
.stat-icon.c2{background:rgba(168,230,207,0.2)}
.stat-icon.c2 svg{stroke:#6abf9a}
.stat-icon.c3{background:rgba(255,192,203,0.18)}
.stat-icon.c3 svg{stroke:#e8929e}
.stat-icon.c4{background:rgba(255,228,160,0.2)}
.stat-icon.c4 svg{stroke:#c8a84a}
.stat-value{font-size:1.5em;font-weight:900;color:var(--primary);animation:countPop 0.5s ease backwards}
.stat-card:nth-child(1) .stat-value{animation-delay:0.15s}
.stat-card:nth-child(2) .stat-value{animation-delay:0.23s}
.stat-card:nth-child(3) .stat-value{animation-delay:0.31s}
.stat-card:nth-child(4) .stat-value{animation-delay:0.39s}
.stat-label{font-size:0.75em;color:var(--text-dim);margin-top:6px;font-weight:500}

/* Status pills row */
.status-pills{
  display:flex;align-items:center;justify-content:center;gap:10px;
  margin-bottom:16px;
}
.status-pill{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 14px;border-radius:50px;
  font-size:0.78em;font-weight:600;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  background:var(--card-bg);
  box-shadow:0 2px 12px rgba(120,180,220,0.1);
  transition:all 0.3s ease;
}
.status-pill .pill-dot{
  width:7px;height:7px;border-radius:50%;
}
.status-pill.charging-on{border-color:rgba(142,228,175,0.4);color:#4a8a6a}
.status-pill.charging-on .pill-dot{background:var(--success);animation:livePulse 2s ease infinite}
.status-pill.charging-off{border-color:rgba(255,180,180,0.3);color:var(--text-dim)}
.status-pill.charging-off .pill-dot{background:var(--text-dim)}
.status-pill.loc-home{border-color:rgba(126,200,227,0.4);color:#4a7a8a}
.status-pill.loc-home .pill-dot{background:var(--primary);animation:livePulse 2s ease infinite}
.status-pill.loc-away{border-color:rgba(255,228,160,0.4);color:#7a6830}
.status-pill.loc-away .pill-dot{background:var(--warning)}

/* Longest session card */
.longest-card{
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:24px;padding:22px;margin-bottom:16px;
  box-shadow:var(--card-shadow);
  animation:fadeInUp 0.5s ease;display:none;
}
.longest-card.show{display:block}
.longest-header{font-size:0.82em;color:var(--text-dim);font-weight:700;margin-bottom:12px}
.longest-value{font-size:2em;font-weight:900;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.longest-app{font-size:0.92em;color:var(--text);margin-top:6px;font-weight:500}
.longest-time{font-size:0.78em;color:var(--text-dim);margin-top:6px}

/* ============ PAGE 2: Apps ============ */
.app-list{display:flex;flex-direction:column;gap:10px}
.app-row{
  display:flex;align-items:center;gap:12px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:24px;padding:16px 18px;
  box-shadow:var(--card-shadow);
  transition:all 0.35s cubic-bezier(0.22,1,0.36,1);
  animation:fadeInUp 0.35s ease backwards;
}
.app-row:hover{
  transform:translateY(-3px);
  box-shadow:0 12px 40px rgba(120,180,220,0.22);
  border-color:rgba(180,220,245,0.6);
}
.app-row.active-session{border-color:rgba(142,228,175,0.4);box-shadow:var(--card-shadow),0 0 20px rgba(142,228,175,0.12)}
.app-dot{
  width:8px;height:8px;border-radius:50%;flex-shrink:0;
}
.app-info{flex:1;min-width:0}
.app-name{font-size:0.9em;font-weight:700;display:flex;align-items:center;gap:8px;color:var(--text)}
.app-badge{font-size:0.65em;padding:3px 10px;border-radius:50px;font-weight:700;letter-spacing:0.5px}
.app-badge.live{background:rgba(142,228,175,0.2);color:#4a8a6a;border:1px solid rgba(142,228,175,0.4)}
.app-bar-bg{height:8px;background:rgba(126,200,227,0.1);border-radius:50px;margin-top:8px;overflow:hidden;position:relative}
.app-bar-fill{
  height:100%;border-radius:50px;background:var(--gradient);
  animation:barGrow 0.8s cubic-bezier(0.22,1,0.36,1) forwards;
  position:relative;overflow:hidden;
}
.app-bar-fill::after{
  content:'';position:absolute;top:0;left:0;right:0;bottom:0;
  background:linear-gradient(90deg,transparent 0%,rgba(255,255,255,0.3) 50%,transparent 100%);
  border-radius:50px;
}
.app-bar-fill.live{background:linear-gradient(90deg,var(--success),var(--primary))}
.app-right{display:flex;align-items:center;gap:10px;flex-shrink:0}
.app-time{text-align:right}
.app-time-value{font-size:1.1em;font-weight:900;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.app-time-pct{font-size:0.68em;color:var(--text-dim);font-weight:500}
.app-actions{display:flex;gap:6px;margin-top:8px}
.app-toggle-btn{
  padding:4px 12px;border-radius:50px;
  border:1px solid var(--card-border);background:rgba(255,255,255,0.5);
  color:var(--text-dim);font-size:0.72em;font-weight:500;
  cursor:pointer;transition:all 0.25s;
  font-family:'Zen Maru Gothic',sans-serif;
}
.app-toggle-btn:hover{border-color:var(--primary);color:var(--primary);background:rgba(126,200,227,0.1)}
.app-toggle-btn.stop:hover{border-color:var(--danger);color:#c07070;background:rgba(255,180,180,0.1)}

/* ============ PAGE 3: Data ============ */
.data-card{
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:24px;padding:22px;margin-bottom:16px;
  box-shadow:var(--card-shadow);
}
.data-card-title{font-size:0.88em;color:var(--text-dim);margin-bottom:16px;text-align:center;font-weight:700}

/* Heatmap: 4 rows x 6 cols */
.heatmap{display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin-top:8px}
.heatmap-cell{
  aspect-ratio:1;border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-size:0.62em;color:var(--text-dim);font-weight:500;
  background:rgba(126,200,227,0.04);border:1px solid rgba(180,220,245,0.2);
  transition:all 0.25s;cursor:default;position:relative;
}
.heatmap-cell:hover{transform:scale(1.15);z-index:1;box-shadow:0 0 12px rgba(126,200,227,0.2)}
.heatmap-cell.l1{background:rgba(126,200,227,0.12);border-color:rgba(126,200,227,0.2)}
.heatmap-cell.l2{background:rgba(126,200,227,0.28);border-color:rgba(126,200,227,0.35);color:var(--text)}
.heatmap-cell.l3{background:rgba(126,200,227,0.48);border-color:rgba(126,200,227,0.55);color:#fff}
.heatmap-cell.l4{background:rgba(126,200,227,0.72);border-color:var(--primary);color:#fff;font-weight:700;box-shadow:0 0 10px rgba(126,200,227,0.3)}
.heatmap-legend{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:14px;font-size:0.7em;color:var(--text-dim);font-weight:500}
.heatmap-legend-cell{width:16px;height:16px;border-radius:6px}

/* Weekly chart */
.weekly-chart{display:flex;align-items:flex-end;justify-content:space-around;height:180px;gap:8px;padding:20px 0 0}
.week-col{display:flex;flex-direction:column;align-items:center;flex:1;height:100%;justify-content:flex-end}
.week-bar{
  width:100%;max-width:48px;border-radius:14px 14px 6px 6px;
  background:linear-gradient(180deg,rgba(126,200,227,0.5),rgba(168,230,207,0.3));
  min-height:4px;
  animation:weekBarGrow 0.6s cubic-bezier(0.22,1,0.36,1) forwards;
  position:relative;cursor:default;
}
.week-bar.today{background:var(--gradient);box-shadow:0 0 16px rgba(126,200,227,0.3)}
.week-bar:hover{filter:brightness(1.1)}
.week-bar-val{font-size:0.7em;color:var(--text-dim);margin-bottom:6px;font-weight:500}
.week-bar-label{font-size:0.72em;color:var(--text-dim);margin-top:8px;font-weight:500}
.week-bar-label.today{color:var(--primary);font-weight:700}

/* Calendar */
.calendar-header{
  display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:14px;
}
.calendar-header .cal-arrow{
  background:none;border:none;cursor:pointer;font-size:1.2em;color:var(--text-dim);
  padding:4px 10px;border-radius:8px;transition:all 0.2s;
  font-family:'Zen Maru Gothic',sans-serif;
}
.calendar-header .cal-arrow:hover{background:rgba(126,200,227,0.1);color:var(--primary)}
.calendar-header .cal-month{font-size:1em;font-weight:700;color:var(--text)}
.calendar-days{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:6px}
.calendar-day-header{
  text-align:center;font-size:0.72em;color:var(--text-dim);font-weight:600;padding:4px 0;
}
.calendar-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.calendar-cell{
  aspect-ratio:1;border-radius:10px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  font-size:0.78em;color:var(--text-dim);font-weight:500;
  background:rgba(255,255,255,0.3);
  transition:all 0.2s;cursor:default;position:relative;
}
.calendar-cell.has-data{cursor:pointer}
.calendar-cell.has-data:hover{transform:scale(1.08);box-shadow:0 0 10px rgba(126,200,227,0.2)}
.calendar-cell.today .cal-today-dot{
  width:5px;height:5px;border-radius:50%;background:var(--primary);
  margin-top:2px;
  box-shadow:0 0 4px rgba(126,200,227,0.6);
}
.calendar-cell.today.cl3 .cal-today-dot,
.calendar-cell.today.cl4 .cal-today-dot{
  background:#fff;
  box-shadow:0 0 4px rgba(255,255,255,0.6);
}
.calendar-cell.cl1{background:rgba(126,200,227,0.22);color:var(--text)}
.calendar-cell.cl2{background:rgba(126,200,227,0.40);color:var(--text)}
.calendar-cell.cl3{background:rgba(126,200,227,0.58);color:#fff}
.calendar-cell.cl4{background:rgba(126,200,227,0.78);color:#fff;font-weight:700}
@keyframes calCellFadeIn{from{opacity:0;transform:translateY(8px) scale(0.95)}to{opacity:1;transform:translateY(0) scale(1)}}
.calendar-cell.animated{animation:calCellFadeIn 0.3s ease backwards}
.calendar-cell.empty{background:transparent}

.day-report-back{
  display:inline-flex;align-items:center;gap:6px;
  background:none;border:1px solid var(--card-border);
  color:var(--text-dim);padding:8px 16px;border-radius:50px;
  font-size:0.85em;font-weight:500;cursor:pointer;
  transition:all 0.2s;margin-bottom:16px;
  font-family:'Zen Maru Gothic',sans-serif;
}
.day-report-back:hover{border-color:var(--primary);color:var(--primary);background:rgba(126,200,227,0.08)}
.day-report-header{
  font-size:1.1em;font-weight:700;color:var(--text);text-align:center;margin-bottom:16px;
}
.day-report-total{
  font-size:2.2em;font-weight:900;text-align:center;
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:16px;
}
.day-report-apps{display:flex;flex-direction:column;gap:8px;margin-bottom:16px}
.day-report-app{
  display:flex;align-items:center;gap:10px;
  font-size:0.88em;color:var(--text);
}
.day-report-app .dr-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.day-report-app .dr-name{flex:1;font-weight:500}
.day-report-app .dr-time{font-weight:700;color:var(--primary)}
.day-report-app .dr-pct{font-size:0.8em;color:var(--text-dim);min-width:40px;text-align:right}

/* ============ PAGE 4: Sessions ============ */
/* Collapsible hourly stacked bar chart */
.hourly-toggle-btn{
  width:100%;padding:12px 20px;margin-bottom:12px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:20px;
  box-shadow:var(--card-shadow);
  font-size:0.88em;font-weight:600;color:var(--text);
  cursor:pointer;transition:all 0.3s ease;
  font-family:'Zen Maru Gothic',sans-serif;
  text-align:center;
}
.hourly-toggle-btn:hover{
  transform:translateY(-2px);
  box-shadow:0 12px 40px rgba(120,180,220,0.22);
  border-color:rgba(180,220,245,0.6);
}
.hourly-wrap{
  max-height:0;overflow:hidden;transition:max-height 0.4s ease;
}
.hourly-wrap.expanded{
  max-height:500px;
}
.hourly-chart{
  display:flex;align-items:flex-end;gap:1px;
  height:250px;
  margin-bottom:16px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:24px;
  box-shadow:var(--card-shadow);
  padding:16px 8px 8px;
  overflow:visible;
  position:relative;
}
.hourly-now-line{
  position:absolute;top:12px;bottom:24px;width:2px;
  background:#e05050;z-index:5;pointer-events:none;
  border-radius:1px;
}
.hourly-col{
  flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;
  height:100%;position:relative;
}
.hourly-bar{
  width:100%;border-radius:3px 3px 0 0;
  display:flex;flex-direction:column;justify-content:flex-end;
  min-height:0;transition:height 0.3s ease;
  overflow:hidden;cursor:pointer;
}
.hourly-bar-val{
  font-size:0.5em;color:var(--text-dim);margin-bottom:2px;font-weight:500;
  text-align:center;min-height:12px;
}
.hourly-seg{width:100%;min-height:1px}
.hourly-label{
  font-size:0.48em;color:var(--text-dim);margin-top:2px;font-weight:500;
  text-align:center;
}
.hourly-tooltip{
  position:fixed;z-index:100;
  background:rgba(255,255,255,0.92);
  backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
  border:1px solid var(--card-border);
  border-radius:12px;padding:8px 12px;
  box-shadow:0 4px 16px rgba(0,0,0,0.12);
  font-size:0.75em;color:var(--text);
  pointer-events:none;white-space:nowrap;
  display:none;
}
.hourly-tooltip .ht-hour{font-weight:700;margin-bottom:4px}
.hourly-tooltip .ht-app{display:flex;align-items:center;gap:6px;margin:2px 0}
.hourly-tooltip .ht-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}

.session-list{display:flex;flex-direction:column;gap:8px;max-height:calc(100vh - 360px);overflow-y:auto}
.session-item{
  padding:14px 16px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-radius:20px;
  border:1px solid var(--card-border);
  box-shadow:var(--card-shadow);
  font-size:0.85em;
  transition:all 0.3s ease;
  cursor:pointer;
  animation:fadeInUp 0.35s ease backwards;
}
.session-item:hover{border-color:rgba(180,220,245,0.6)}
.session-summary{display:flex;align-items:center;gap:10px}
.session-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.session-app{font-weight:700;min-width:80px;color:var(--text)}
.session-time{color:var(--text-dim);flex:1;font-variant-numeric:tabular-nums;font-weight:500;font-size:0.9em}
.session-dur{color:var(--primary);font-weight:700;min-width:55px;text-align:right}

/* Session expanded edit form */
.session-edit{
  max-height:0;overflow:hidden;opacity:0;
  transition:max-height 0.35s ease,opacity 0.3s ease,margin-top 0.3s ease;
  margin-top:0;
}
.session-item.expanded .session-edit{
  max-height:300px;opacity:1;margin-top:14px;
}
.session-edit-inner{
  padding-top:12px;border-top:1px solid var(--card-border);
  display:flex;flex-direction:column;gap:10px;
}
.session-edit label{font-size:0.78em;color:var(--text-dim);font-weight:500;display:block;margin-bottom:4px}
.session-edit input{
  width:100%;padding:10px 12px;border-radius:14px;
  border:1px solid var(--card-border);
  background:rgba(255,255,255,0.6);color:var(--text);
  font-size:0.85em;
  font-family:'Zen Maru Gothic',sans-serif;
  transition:border-color 0.3s;
}
.session-edit input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 12px rgba(126,200,227,0.15)}
.session-edit-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:4px}
.se-btn{
  padding:8px 18px;border-radius:50px;
  border:1px solid var(--card-border);background:rgba(255,255,255,0.6);
  color:var(--text-dim);font-size:0.8em;font-weight:500;
  cursor:pointer;transition:all 0.25s;
  font-family:'Zen Maru Gothic',sans-serif;
}
.se-btn:hover{border-color:var(--primary);color:var(--primary);background:rgba(126,200,227,0.08)}
.se-btn.save{background:var(--gradient);color:#fff;border:none;font-weight:700;box-shadow:0 4px 16px rgba(126,200,227,0.3)}
.se-btn.save:hover{box-shadow:0 6px 20px rgba(126,200,227,0.4);transform:translateY(-1px)}
.se-btn.delete{color:#c07070;border-color:rgba(255,180,180,0.4)}
.se-btn.delete:hover{background:rgba(255,180,180,0.1);border-color:var(--danger);color:#a05050}

/* ============ PAGE 5: Settings ============ */
.setting-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:18px 20px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:20px;
  box-shadow:var(--card-shadow);
  margin-bottom:12px;
  font-size:0.92em;font-weight:500;color:var(--text);
}
.setting-label{display:flex;align-items:center;gap:10px}
.setting-label svg{width:20px;height:20px;stroke:var(--text-dim);fill:none;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}

/* Toggle switch */
.toggle{
  position:relative;width:48px;height:24px;
  background:#d0dce5;border-radius:50px;
  cursor:pointer;transition:background 0.35s ease;
  border:none;padding:0;
}
.toggle.on{background:linear-gradient(135deg,#7ec8e3,#a8e6cf)}
.toggle-thumb{
  position:absolute;top:2px;left:2px;
  width:20px;height:20px;border-radius:50%;
  background:#fff;
  box-shadow:0 2px 6px rgba(0,0,0,0.15);
  transition:left 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.toggle.on .toggle-thumb{left:26px}

/* History panel */
.setting-row-wrap{margin-bottom:12px}
.setting-row-wrap .setting-row{margin-bottom:0;border-radius:20px 20px 20px 20px}
.setting-row-wrap.expanded .setting-row{border-radius:20px 20px 0 0;margin-bottom:0}
.history-btn{
  background:none;border:none;cursor:pointer;padding:4px 8px;
  font-size:0.75em;color:var(--text-dim);font-weight:500;
  border-radius:8px;transition:all 0.2s;
  font-family:'Zen Maru Gothic',sans-serif;
}
.history-btn:hover{background:rgba(126,200,227,0.1);color:var(--primary)}
.history-panel{
  max-height:0;overflow:hidden;opacity:0;
  transition:max-height 0.35s ease,opacity 0.3s ease;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);border-top:none;
  border-radius:0 0 20px 20px;
  box-shadow:var(--card-shadow);
}
.setting-row-wrap.expanded .history-panel{
  max-height:400px;opacity:1;overflow-y:auto;
}
.history-event{
  display:flex;align-items:center;justify-content:space-between;
  padding:10px 16px;border-bottom:1px solid rgba(180,220,245,0.15);
  font-size:0.8em;
}
.history-event:last-child{border-bottom:none}
.history-event-info{display:flex;flex-direction:column;gap:2px}
.history-event-type{font-weight:600;color:var(--text)}
.history-event-time{font-size:0.85em;color:var(--text-dim)}
.history-del-btn{
  background:none;border:1px solid rgba(255,180,180,0.3);
  color:#c07070;padding:4px 10px;border-radius:50px;
  font-size:0.78em;cursor:pointer;transition:all 0.2s;
  font-family:'Zen Maru Gothic',sans-serif;
}
.history-del-btn:hover{background:rgba(255,180,180,0.1);border-color:var(--danger)}
.history-empty{padding:16px;text-align:center;color:var(--text-dim);font-size:0.82em}

/* Settings buttons */
.setting-btn{
  width:100%;padding:16px 20px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:20px;
  box-shadow:var(--card-shadow);
  margin-bottom:12px;
  font-size:0.92em;font-weight:600;color:var(--text);
  cursor:pointer;transition:all 0.3s ease;
  font-family:'Zen Maru Gothic',sans-serif;
  text-align:center;
}
.setting-btn:hover{
  transform:translateY(-2px);
  box-shadow:0 12px 40px rgba(120,180,220,0.22);
  border-color:rgba(180,220,245,0.6);
}
.setting-btn.danger-btn{color:#c07070}
.setting-btn.danger-btn:hover{border-color:var(--danger);background:rgba(255,180,180,0.1)}

/* App color settings */
.app-color-section{
  margin-top:16px;margin-bottom:16px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:20px;
  box-shadow:var(--card-shadow);
  padding:16px 20px;
}
.app-color-title{
  font-size:0.92em;font-weight:700;color:var(--text);
  margin-bottom:12px;text-align:center;
}
.app-color-list{display:flex;flex-direction:column;gap:8px}
.app-color-row{
  display:flex;align-items:center;gap:10px;
  font-size:0.85em;color:var(--text);
}
.app-color-dot{
  width:14px;height:14px;border-radius:50%;flex-shrink:0;
  border:1px solid rgba(0,0,0,0.1);
}
.app-color-name{flex:1;font-weight:500}
.app-color-input{
  width:32px;height:26px;border:none;border-radius:6px;
  cursor:pointer;padding:0;background:transparent;
}
.app-color-input::-webkit-color-swatch-wrapper{padding:0}
.app-color-input::-webkit-color-swatch{border:1px solid rgba(0,0,0,0.1);border-radius:4px}

.watermark-section{
  margin-top:16px;margin-bottom:16px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:20px;
  box-shadow:var(--card-shadow);
  padding:16px 20px;
}
.watermark-title{
  font-size:0.92em;font-weight:700;color:var(--text);
  margin-bottom:14px;text-align:center;
}
.watermark-row{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:10px;font-size:0.85em;color:var(--text);
}
.watermark-row:last-child{margin-bottom:0}
.watermark-row label{font-weight:500;min-width:80px}
.watermark-row input[type="color"]{
  width:32px;height:26px;border:none;border-radius:6px;
  cursor:pointer;padding:0;background:transparent;
}
.watermark-row input[type="color"]::-webkit-color-swatch-wrapper{padding:0}
.watermark-row input[type="color"]::-webkit-color-swatch{border:1px solid rgba(0,0,0,0.1);border-radius:4px}
.watermark-row input[type="range"]{
  width:120px;height:6px;border-radius:3px;
  -webkit-appearance:none;appearance:none;
  background:rgba(126,200,227,0.2);outline:none;
  cursor:pointer;
}
.watermark-row input[type="range"]::-webkit-slider-thumb{
  -webkit-appearance:none;appearance:none;
  width:16px;height:16px;border-radius:50%;
  background:var(--primary);border:2px solid #fff;
  box-shadow:0 2px 6px rgba(0,0,0,0.15);
}
.watermark-row .wm-val{
  min-width:40px;text-align:right;font-variant-numeric:tabular-nums;
  color:var(--text-dim);font-size:0.9em;
}

/* Timezone settings */
.tz-section{
  margin-bottom:16px;
  background:var(--card-bg);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:20px;
  box-shadow:var(--card-shadow);
  padding:16px 20px;
}
.tz-title{
  font-size:0.92em;font-weight:700;color:var(--text);
  margin-bottom:12px;text-align:center;
}
.tz-current{
  text-align:center;font-size:0.85em;color:var(--text-dim);
  margin-bottom:12px;font-weight:500;
}
.tz-row{
  display:flex;align-items:center;justify-content:center;
  gap:10px;margin-bottom:10px;
}
.tz-row label{font-size:0.85em;font-weight:500;color:var(--text)}
.tz-input{
  width:80px;padding:8px 10px;border-radius:12px;
  border:1px solid var(--card-border);
  background:rgba(255,255,255,0.6);color:var(--text);
  font-size:0.88em;font-family:'Zen Maru Gothic',sans-serif;
  text-align:center;
}
.tz-input:focus{outline:none;border-color:var(--primary)}
.tz-save-btn{
  display:block;width:100%;padding:10px;margin-top:10px;
  background:var(--gradient);color:#fff;
  border:none;border-radius:16px;
  font-size:0.88em;font-weight:600;cursor:pointer;
  font-family:'Zen Maru Gothic',sans-serif;
  transition:all 0.3s ease;
}
.tz-save-btn:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(126,200,227,0.3)}

.settings-footer{
  text-align:center;color:var(--text-dim);
  font-size:0.75em;margin-top:32px;padding-bottom:20px;
  font-weight:500;
}

/* Collapsible section headers */
.section-header{
  cursor:pointer;
  padding:14px 16px;
  font-weight:600;
  font-size:0.9em;
  color:var(--text);
  display:flex;
  align-items:center;
  gap:8px;
  transition:opacity 0.2s;
}
.section-header:hover{opacity:0.7}

/* ============ Bottom Nav ============ */
.bottom-nav{
  position:fixed;bottom:0;left:0;right:0;
  height:56px;z-index:50;
  background:rgba(255,255,255,0.7);
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  border-top:1px solid rgba(180,220,245,0.3);
  display:flex;align-items:center;justify-content:space-around;
  padding:0 8px;
}
.nav-item{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:2px;padding:6px 12px;
  cursor:pointer;position:relative;
  transition:all 0.25s ease;
  border:none;background:transparent;
  -webkit-tap-highlight-color:transparent;
}
.nav-item svg{
  width:20px;height:20px;
  stroke:var(--text-dim);fill:none;
  stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;
  transition:stroke 0.25s ease;
}
.nav-item.active svg{stroke:var(--primary)}
.nav-dot{
  width:4px;height:4px;border-radius:50%;
  background:transparent;
  transition:all 0.3s ease;
}
.nav-item.active .nav-dot{
  background:var(--primary);
  animation:navDotSlide 0.3s ease;
}

/* ============ Toast ============ */
.toast{
  position:fixed;top:20px;left:50%;
  transform:translateX(-50%);
  background:rgba(255,255,255,0.75);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid var(--card-border);
  border-radius:20px;padding:12px 20px;
  font-size:0.85em;font-weight:500;color:var(--text);
  box-shadow:0 8px 32px rgba(120,180,220,0.2);
  z-index:200;
  animation:toastIn 0.3s ease forwards;
  pointer-events:none;
}
.toast.hide{animation:toastOut 0.3s ease forwards}

/* Loading shimmer */
.loading{
  background:linear-gradient(90deg,rgba(126,200,227,0.05) 25%,rgba(126,200,227,0.1) 50%,rgba(126,200,227,0.05) 75%);
  background-size:200% 100%;animation:shimmer 1.5s infinite;
  border-radius:16px;min-height:40px;
}

/* Responsive */
@media(max-width:600px){
  .page{padding:20px 14px 24px}
  .page-title{font-size:1.5em}
  .weekly-chart{height:140px}
  .session-summary{flex-wrap:wrap;gap:6px}
  .session-time{min-width:100%;order:3;font-size:0.78em}
}
</style>
</head>
<body>

<!-- Kaomoji watermark layer -->
<div class="kaomoji-bg">
  <span style="top:5%;left:8%;font-size:18px;--kao-op:0.14;animation-delay:0s;transform:rotate(-8deg)">(>_<)</span>
  <span style="top:12%;right:12%;font-size:24px;--kao-op:0.13;animation-delay:-4s;transform:rotate(5deg)">(*^-^*)</span>
  <span style="top:22%;left:20%;font-size:16px;--kao-op:0.16;animation-delay:-8s;transform:rotate(-3deg)">(=^-^=)</span>
  <span style="top:30%;right:6%;font-size:20px;--kao-op:0.14;animation-delay:-2s;transform:rotate(10deg)">(-_-) zzz</span>
  <span style="top:40%;left:5%;font-size:30px;--kao-op:0.12;animation-delay:-6s;transform:rotate(-12deg)">(^o^)/</span>
  <span style="top:48%;right:18%;font-size:14px;--kao-op:0.18;animation-delay:-10s;transform:rotate(7deg)">(*^_^*)</span>
  <span style="top:55%;left:25%;font-size:22px;--kao-op:0.13;animation-delay:-14s;transform:rotate(-5deg)">(>_<)</span>
  <span style="top:62%;right:8%;font-size:28px;--kao-op:0.14;animation-delay:-3s;transform:rotate(15deg)">(*^-^*)</span>
  <span style="top:70%;left:12%;font-size:16px;--kao-op:0.16;animation-delay:-7s;transform:rotate(-10deg)">(=^-^=)</span>
  <span style="top:78%;right:22%;font-size:18px;--kao-op:0.12;animation-delay:-11s;transform:rotate(3deg)">(-_-) zzz</span>
  <span style="top:85%;left:6%;font-size:40px;--kao-op:0.12;animation-delay:-5s;transform:rotate(8deg)">(^o^)/</span>
  <span style="top:90%;right:10%;font-size:15px;--kao-op:0.15;animation-delay:-9s;transform:rotate(-6deg)">(*^_^*)</span>
  <span style="top:18%;left:55%;font-size:20px;--kao-op:0.13;animation-delay:-13s;transform:rotate(12deg)">(>_<)</span>
  <span style="top:35%;left:45%;font-size:16px;--kao-op:0.14;animation-delay:-1s;transform:rotate(-15deg)">(=^-^=)</span>
  <span style="top:52%;left:60%;font-size:24px;--kao-op:0.12;animation-delay:-12s;transform:rotate(6deg)">(-_-) zzz</span>
  <span style="top:68%;left:50%;font-size:18px;--kao-op:0.16;animation-delay:-15s;transform:rotate(-4deg)">(*^-^*)</span>
  <span style="top:82%;left:40%;font-size:22px;--kao-op:0.13;animation-delay:-8s;transform:rotate(9deg)">(^o^)/</span>
  <span style="top:8%;left:70%;font-size:14px;--kao-op:0.18;animation-delay:-16s;transform:rotate(-7deg)">(*^_^*)</span>
  <span style="top:44%;left:80%;font-size:26px;--kao-op:0.12;animation-delay:-6s;transform:rotate(11deg)">(>_<)</span>
  <span style="top:75%;left:70%;font-size:17px;--kao-op:0.14;animation-delay:-10s;transform:rotate(-13deg)">(=^-^=)</span>
  <span style="top:95%;left:55%;font-size:20px;--kao-op:0.13;animation-delay:-4s;transform:rotate(4deg)">(-_-) zzz</span>
  <span style="top:3%;left:40%;font-size:15px;--kao-op:0.15;animation-delay:-7s;transform:rotate(-9deg)">(^o^)/</span>
  <span style="top:58%;left:3%;font-size:19px;--kao-op:0.13;animation-delay:-2s;transform:rotate(14deg)">(*^-^*)</span>
  <span style="top:25%;right:3%;font-size:32px;--kao-op:0.12;animation-delay:-11s;transform:rotate(-2deg)">(*^_^*)</span>
  <span style="top:15%;left:35%;font-size:14px;--kao-op:0.16;animation-delay:-14s;transform:rotate(8deg)">(>_<)</span>
  <span style="top:65%;right:30%;font-size:20px;--kao-op:0.14;animation-delay:-3s;transform:rotate(-11deg)">(=^-^=)</span>
  <span style="top:88%;left:22%;font-size:16px;--kao-op:0.13;animation-delay:-9s;transform:rotate(6deg)">(-_-) zzz</span>
  <span style="top:38%;right:35%;font-size:18px;--kao-op:0.15;animation-delay:-5s;transform:rotate(-8deg)">(^o^)/</span>
  <span style="top:73%;left:85%;font-size:14px;--kao-op:0.18;animation-delay:-12s;transform:rotate(3deg)">(*^_^*)</span>
  <span style="top:50%;left:92%;font-size:22px;--kao-op:0.12;animation-delay:-1s;transform:rotate(-6deg)">(>_<)</span>
</div>

<div class="hourly-tooltip" id="hourlyTooltip"></div>

<!-- =============== PAGES =============== -->
<div class="pages-container" id="pagesContainer">

  <!-- PAGE 1: Home -->
  <div class="page" id="page-home">
    <div class="page-inner">
      <div class="page-title" style="animation:fadeInUp 0.5s ease forwards">&#x5c4f;&#x5e55;&#x65f6;&#x95f4;</div>
      <div class="page-subtitle">&#x4eca;&#x65e5;&#x4f7f;&#x7528;&#x62a5;&#x544a;&#xff5e;</div>

      <div class="time-display">
        <span class="status-dot idle" id="statusDot"></span>
        <span id="dateDisplay">&#x52a0;&#x8f7d;&#x4e2d;...</span>
      </div>

      <!-- Night Owl Alert -->
      <div class="alert-card night-owl-alert" id="nightOwl">
        <div class="alert-text" id="nightOwlText">&#x73b0;&#x5728;&#x5f88;&#x665a;&#x4e86;&#x54e6;&#xff5e;&#x65e9;&#x70b9;&#x4f11;&#x606f;&#x5427;&#xff5e;</div>
      </div>

      <!-- All-Nighter Alert -->
      <div class="alert-card all-nighter-alert" id="allNighter">
        <div class="alert-text" id="allNighterText">&#x4e00;&#x6574;&#x591c;&#x6ca1;&#x7761;&#x5462;...&#x8981;&#x6ce8;&#x610f;&#x8eab;&#x4f53;&#x5440;&#xff5e;</div>
      </div>

      <!-- Current Activity -->
      <div class="current-card" id="currentCard">
        <div class="current-label">
          <span class="badge-live"><span class="live-dot"></span> &#x4f7f;&#x7528;&#x4e2d; &#x2661;</span>
        </div>
        <div class="current-app" id="currentApp">--</div>
        <div class="current-duration" id="currentDur">--</div>
      </div>

      <div class="idle-message" id="idleMessage">&#x6ca1;&#x6709;&#x5728;&#x4f7f;&#x7528;&#x624b;&#x673a;&#x5462; (*^_^*)</div>

      <!-- Stats Grid 2x2 -->
      <div class="stats-grid" id="statsGrid">
        <div class="stat-card">
          <div class="stat-icon c1">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div class="stat-value" id="statTotal">--</div>
          <div class="stat-label">&#x603b;&#x65f6;&#x957f;</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon c2">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
          </div>
          <div class="stat-value" id="statApps">--</div>
          <div class="stat-label">&#x5e94;&#x7528;&#x6570;</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon c3">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>
          </div>
          <div class="stat-value" id="statOpens">--</div>
          <div class="stat-label">&#x6253;&#x5f00;&#x6b21;&#x6570;</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon c4">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          </div>
          <div class="stat-value" id="statTop">--</div>
          <div class="stat-label" id="statTopLabel">&#x6700;&#x5e38;&#x7528;</div>
        </div>
      </div>

      <!-- Longest Session -->
      <div class="longest-card" id="longestCard">
        <div class="longest-header">&#x4eca;&#x65e5;&#x6700;&#x957f;&#x8fde;&#x7eed;&#x4f7f;&#x7528;</div>
        <div class="longest-value" id="longestValue">--</div>
        <div class="longest-app" id="longestApp">--</div>
        <div class="longest-time" id="longestTime">--</div>
      </div>

      <!-- Status Pills -->
      <div class="status-pills" id="statusPills">
        <div class="status-pill charging-off" id="chargingPill">
          <span class="pill-dot"></span>
          <span id="chargingPillText">&#x672a;&#x5145;&#x7535;</span>
        </div>
        <div class="status-pill loc-away" id="locationPill">
          <span class="pill-dot"></span>
          <span id="locationPillText">&#x5916;&#x51fa;</span>
        </div>
      </div>
    </div>
  </div>

  <!-- PAGE 2: Apps -->
  <div class="page" id="page-apps">
    <div class="page-inner">
      <div class="page-title">&#x5e94;&#x7528;&#x6392;&#x884c;</div>
      <div class="page-subtitle">&#x4eca;&#x65e5;&#x5e94;&#x7528;&#x4f7f;&#x7528;&#x60c5;&#x51b5;&#xff5e;</div>
      <div class="app-list" id="appList"><div class="loading" style="height:200px"></div></div>
    </div>
  </div>

  <!-- PAGE 3: Data -->
  <div class="page" id="page-data">
    <div class="page-inner">
      <div class="page-title" style="font-family:'ZCOOL XiaoWei','Zen Maru Gothic',serif">&#x6570;&#x636e;&#x5206;&#x6790;</div>
      <div class="page-subtitle">&#x65e5;&#x5386;&#x8d70;&#x52bf;&#x4e00;&#x76ee;&#x4e86;&#x7136;&#xff5e;</div>

      <!-- Calendar view -->
      <div id="calendarView">
        <div class="data-card">
          <div class="calendar-header">
            <button class="cal-arrow" id="calPrev" onclick="calendarPrevMonth()">&lt;</button>
            <span class="cal-month" id="calMonth"></span>
            <button class="cal-arrow" id="calNext" onclick="calendarNextMonth()">&gt;</button>
          </div>
          <div class="calendar-days">
            <div class="calendar-day-header">&#x4e00;</div>
            <div class="calendar-day-header">&#x4e8c;</div>
            <div class="calendar-day-header">&#x4e09;</div>
            <div class="calendar-day-header">&#x56db;</div>
            <div class="calendar-day-header">&#x4e94;</div>
            <div class="calendar-day-header">&#x516d;</div>
            <div class="calendar-day-header">&#x65e5;</div>
          </div>
          <div class="calendar-grid" id="calendarGrid"></div>
        </div>

        <div class="data-card">
          <div class="data-card-title">&#x6bcf;&#x5468;&#x5c4f;&#x5e55;&#x65f6;&#x95f4;&#x8d8b;&#x52bf;</div>
          <div class="weekly-chart" id="weeklyChart"></div>
        </div>
      </div>

      <!-- Day report view (hidden by default) -->
      <div id="dayReportView" style="display:none">
        <button class="day-report-back" onclick="backToCalendar()">&larr; &#x8fd4;&#x56de;&#x65e5;&#x5386;</button>
        <div id="dayReportContent"></div>
      </div>
    </div>
  </div>

  <!-- PAGE 4: Sessions -->
  <div class="page" id="page-sessions">
    <div class="page-inner">
      <div class="page-title">&#x4eca;&#x65e5;&#x4f1a;&#x8bdd;</div>
      <div class="page-subtitle">&#x4eca;&#x5929;&#x7684;&#x4f7f;&#x7528;&#x8bb0;&#x5f55;&#xff5e;</div>
      <button class="hourly-toggle-btn" id="hourlyToggleBtn" onclick="toggleHourlyChart()">&#x67e5;&#x770b;&#x65f6;&#x95f4;&#x5206;&#x5e03;</button>
      <div class="hourly-wrap" id="hourlyWrap">
        <div class="hourly-chart" id="hourlyChart"></div>
      </div>
      <div class="session-list" id="sessionList"><div class="loading" style="height:150px"></div></div>
    </div>
  </div>

  <!-- PAGE 5: Settings -->
  <div class="page" id="page-settings">
    <div class="page-inner">
      <div class="page-title">&#x8bbe;&#x7f6e;</div>
      <div class="page-subtitle">&#x529f;&#x80fd;&#x63a7;&#x5236;&#xff5e;</div>

      <div class="setting-row-wrap" id="chargingWrap">
        <div class="setting-row">
          <div class="setting-label">
            <svg viewBox="0 0 24 24"><path d="M6.7 17.3l-3.4 1.2 1.2-3.4L17.3 2.3a1.4 1.4 0 0 1 2 0l1.4 1.4a1.4 1.4 0 0 1 0 2z"/><line x1="13" y1="6" x2="18" y2="11"/></svg>
            &#x5145;&#x7535;&#x72b6;&#x6001;
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <button class="history-btn" onclick="event.stopPropagation();toggleHistory('charging')">&#x5386;&#x53f2;</button>
            <button class="toggle" id="chargingToggle" onclick="toggleCharging()">
              <div class="toggle-thumb"></div>
            </button>
          </div>
        </div>
        <div class="history-panel" id="chargingHistory"></div>
      </div>

      <div class="setting-row-wrap" id="locationWrap">
        <div class="setting-row">
          <div class="setting-label">
            <svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            &#x5728;&#x5bb6;
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <button class="history-btn" onclick="event.stopPropagation();toggleHistory('location')">&#x5386;&#x53f2;</button>
            <button class="toggle" id="locationToggle" onclick="toggleLocation()">
              <div class="toggle-thumb"></div>
            </button>
          </div>
        </div>
        <div class="history-panel" id="locationHistory"></div>
      </div>

      <button class="setting-btn" onclick="doRefresh()">&#x5237;&#x65b0;&#x6570;&#x636e;</button>
      <button class="setting-btn danger-btn" onclick="resetAll()">&#x91cd;&#x7f6e;&#x6240;&#x6709;</button>

      <div class="tz-section">
        <div class="section-header" onclick="toggleSection('tz-content')">
          <span id="tz-content-arrow">&#x25b8;</span> &#x65f6;&#x533a;&#x8bbe;&#x7f6e;
        </div>
        <div id="tz-content" style="display:none">
          <div class="tz-current" id="tzCurrent">&#x5f53;&#x524d;&#x65f6;&#x533a;&#xff1a;loading...</div>
          <div class="tz-row">
            <label>UTC &#x504f;&#x79fb;</label>
            <input type="number" class="tz-input" id="tzOffsetInput" min="-12" max="14" step="0.5" value="-4">
          </div>
          <button class="tz-save-btn" onclick="saveTimezone()">&#x4fdd;&#x5b58;</button>
        </div>
      </div>

      <div class="app-color-section">
        <div class="section-header" onclick="toggleSection('appcolor-content')">
          <span id="appcolor-content-arrow">&#x25b8;</span> &#x5e94;&#x7528;&#x989c;&#x8272;
        </div>
        <div id="appcolor-content" style="display:none">
          <div class="app-color-list" id="appColorList"></div>
        </div>
      </div>

      <div class="watermark-section">
        <div class="section-header" onclick="toggleSection('bgcolor-content')">
          <span id="bgcolor-content-arrow">&#x25b8;</span> &#x80cc;&#x666f;&#x989c;&#x8272;
        </div>
        <div id="bgcolor-content" style="display:none">
          <div class="watermark-row">
            <label>&#x8d77;&#x59cb;</label>
            <input type="color" id="bgColor1" value="#d4e8f5" onchange="onBgChange()">
          </div>
          <div class="watermark-row">
            <label>&#x4e2d;&#x95f4;</label>
            <input type="color" id="bgColor2" value="#b8d8ee" onchange="onBgChange()">
          </div>
          <div class="watermark-row">
            <label>&#x7ec8;&#x70b9;</label>
            <input type="color" id="bgColor3" value="#a8d0e0" onchange="onBgChange()">
          </div>
        </div>
      </div>
      <div class="watermark-section">
        <div class="section-header" onclick="toggleSection('wm-content')">
          <span id="wm-content-arrow">&#x25b8;</span> &#x6c34;&#x5370;&#x8bbe;&#x7f6e;
        </div>
        <div id="wm-content" style="display:none">
          <div class="watermark-row">
            <label>&#x989c;&#x8272;</label>
            <input type="color" id="wmColor" value="#3a5068" onchange="onWatermarkChange()">
          </div>
          <div class="watermark-row">
            <label>&#x900f;&#x660e;&#x5ea6;</label>
            <input type="range" id="wmOpacity" min="0" max="100" value="100" oninput="onWatermarkChange();document.getElementById('wmOpacityVal').textContent=this.value+'%'">
            <span class="wm-val" id="wmOpacityVal">100%</span>
          </div>
          <div class="watermark-row">
            <label>&#x5927;&#x5c0f;</label>
            <input type="range" id="wmSize" min="50" max="200" value="100" oninput="onWatermarkChange();document.getElementById('wmSizeVal').textContent=this.value+'%'">
            <span class="wm-val" id="wmSizeVal">100%</span>
          </div>
          <div class="watermark-row" style="flex-direction:column;align-items:stretch;gap:6px">
            <label>&#x5185;&#x5bb9;</label>
            <input type="text" id="wmContent" style="width:100%;padding:8px 12px;border-radius:12px;border:1px solid var(--card-border);background:rgba(255,255,255,0.6);color:var(--text);font-size:0.85em;font-family:'Zen Maru Gothic',sans-serif" placeholder="(>_<), (*^-^*), (=^-^=), ..." oninput="onWatermarkChange()">
            <span style="font-size:0.72em;color:var(--text-dim)">&#x7528;&#x82f1;&#x6587;&#x9017;&#x53f7;&#x5206;&#x9694;&#xff0c;&#x7559;&#x7a7a;&#x7528;&#x9ed8;&#x8ba4;</span>
          </div>
        </div>
      </div>

      <div class="settings-footer">&#x5c4f;&#x5e55;&#x65f6;&#x95f4;&#x8ffd;&#x8e2a;&#x5668; v3.5.1 &#x2661; &#x6bcf;30&#x79d2;&#x81ea;&#x52a8;&#x5237;&#x65b0;</div>
    </div>
  </div>

</div>

<!-- Bottom Nav -->
<nav class="bottom-nav" id="bottomNav">
  <button class="nav-item active" data-page="0" onclick="goToPage(0)">
    <svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
    <div class="nav-dot"></div>
  </button>
  <button class="nav-item" data-page="1" onclick="goToPage(1)">
    <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
    <div class="nav-dot"></div>
  </button>
  <button class="nav-item" data-page="2" onclick="goToPage(2)">
    <svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
    <div class="nav-dot"></div>
  </button>
  <button class="nav-item" data-page="3" onclick="goToPage(3)">
    <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
    <div class="nav-dot"></div>
  </button>
  <button class="nav-item" data-page="4" onclick="goToPage(4)">
    <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
    <div class="nav-dot"></div>
  </button>
</nav>

<script>
function toggleSection(id){
  const el=document.getElementById(id);
  const arrow=document.getElementById(id+'-arrow');
  if(el.style.display==='none'){
    el.style.display='block';
    if(arrow) arrow.textContent='\u25be';
  }else{
    el.style.display='none';
    if(arrow) arrow.textContent='\u25b8';
  }
}

const API = window.location.origin;

const DOT_COLORS = ['#7ec8e3','#a8e6cf','#ffc0cb','#ffe4a0','#8ee4af','#b8e4f0','#ffd6e0','#c8e6ff'];
function dotColor(i){ return DOT_COLORS[i % DOT_COLORS.length]; }

const APP_COLORS = ['#4A90D9','#E8556D','#50C878','#F5A623','#9B59B6','#E74C3C','#1ABC9C','#F39C12','#3498DB','#E91E63','#2ECC71','#FF6B35','#8E44AD','#16A085','#D35400','#2980B9'];
function appColor(name) {
  const saved = localStorage.getItem('appColor_' + name);
  if (saved) return saved;
  let h = 0;
  for(let i=0; i<name.length; i++) h = ((h << 5) - h + name.charCodeAt(i)) | 0;
  return APP_COLORS[Math.abs(h) % APP_COLORS.length];
}
function setAppColor(name, color) {
  localStorage.setItem('appColor_' + name, color);
}

const WEEKDAY_CN = ['\u5468\u65e5','\u5468\u4e00','\u5468\u4e8c','\u5468\u4e09','\u5468\u56db','\u5468\u4e94','\u5468\u516d'];

function fmt(sec){
  if(!sec||sec<0) return '0\u79d2';
  sec=Math.round(sec);
  if(sec<60) return sec+'\u79d2';
  const m=Math.floor(sec/60);
  if(m<60) return m+'\u5206\u949f';
  const h=Math.floor(m/60),rm=m%60;
  return rm?h+'\u5c0f\u65f6'+rm+'\u5206':h+'\u5c0f\u65f6';
}
function fmtMins(mins){return fmt(mins*60)}

let currentPage = 0;
let activeSessionStart = null;
let activeApp = null;
let timerInterval = null;
let chargingOn = false;
let locationOn = false;

// ============ Page Navigation ============
const pagesContainer = document.getElementById('pagesContainer');
const navItems = document.querySelectorAll('.nav-item');

function goToPage(idx){
  currentPage = idx;
  const pages = document.querySelectorAll('.page');
  pages[idx].scrollIntoView({behavior:'smooth',block:'nearest',inline:'start'});
  updateNav(idx);
  if(idx===2){loadCalendar();loadHeatmap();loadWeekly();}
  if(idx===3) loadSessions();
}

function updateNav(idx){
  navItems.forEach((item,i)=>{
    item.classList.toggle('active', i===idx);
  });
}

// Detect scroll-snap position changes
let scrollTimeout;
pagesContainer.addEventListener('scroll', function(){
  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(()=>{
    const pageWidth = window.innerWidth;
    const scrollLeft = pagesContainer.scrollLeft;
    const idx = Math.round(scrollLeft / pageWidth);
    if(idx !== currentPage){
      currentPage = idx;
      updateNav(idx);
      if(idx===2){loadCalendar();loadHeatmap();loadWeekly();}
      if(idx===3) loadSessions();
    }
  }, 100);
});

// Touch swipe detection
let touchStartX = 0;
let touchStartY = 0;
let touchStartTime = 0;
pagesContainer.addEventListener('touchstart', function(e){
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
  touchStartTime = Date.now();
}, {passive:true});

pagesContainer.addEventListener('touchend', function(e){
  const dx = e.changedTouches[0].clientX - touchStartX;
  const dy = e.changedTouches[0].clientY - touchStartY;
  const dt = Date.now() - touchStartTime;
  if(Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50 && dt < 400){
    if(dx < 0 && currentPage < 4) goToPage(currentPage + 1);
    else if(dx > 0 && currentPage > 0) goToPage(currentPage - 1);
  }
}, {passive:true});

// ============ Toast ============
function showToast(msg){
  const existing = document.querySelector('.toast');
  if(existing) existing.remove();
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(()=>{t.classList.add('hide')}, 2000);
  setTimeout(()=>{t.remove()}, 2300);
}

// ============ Live Timer ============
function startLiveTimer(){
  if(timerInterval) clearInterval(timerInterval);
  if(!activeSessionStart) return;
  timerInterval = setInterval(()=>{
    const now=Date.now();
    const dur=Math.floor((now-activeSessionStart)/1000);
    const el=document.getElementById('currentDur');
    if(el) el.textContent=fmt(dur);
  },1000);
}

// ============ Main Data Fetch ============
async function refreshAll(){
  try{
    const [todayRes,nightRes,allNightRes,longestRes]=await Promise.all([
      fetch(API+'/api/screentime/today'),
      fetch(API+'/api/screentime/nightowl'),
      fetch(API+'/api/screentime/allnighter'),
      fetch(API+'/api/screentime/longest'),
    ]);
    const data=await todayRes.json();
    const night=await nightRes.json();
    const allNight=await allNightRes.json();
    const longest=await longestRes.json();

    // Night owl banner
    const owlBanner=document.getElementById('nightOwl');
    if(night.is_staying_up_late){
      owlBanner.classList.add('show');
      document.getElementById('nightOwlText').textContent='\u73b0\u5728\u5f88\u665a\u4e86\u54e6\uff5e\u65e9\u70b9\u4f11\u606f\u5427\uff5e';
    }else{owlBanner.classList.remove('show')}

    // All-nighter banner
    const allBanner=document.getElementById('allNighter');
    if(allNight.is_all_nighter){allBanner.classList.add('show')}else{allBanner.classList.remove('show')}

    // Time display
    document.getElementById('dateDisplay').textContent=data.date+' \u00b7 '+data.current_time+' '+data.timezone;

    // Current activity
    const curCard=document.getElementById('currentCard');
    const idleMsg=document.getElementById('idleMessage');
    const statusDot=document.getElementById('statusDot');
    const activeApps=data.apps.filter(a=>a.status==='active');
    if(activeApps.length>0){
      curCard.classList.add('show');
      idleMsg.classList.remove('show');
      const a=activeApps[0];
      document.getElementById('currentApp').textContent=a.app;
      activeSessionStart=Date.now()-(a.current_session_seconds*1000);
      activeApp=a.app;
      startLiveTimer();
      statusDot.classList.remove('idle');
    }else{
      curCard.classList.remove('show');
      idleMsg.classList.add('show');
      activeSessionStart=null;
      activeApp=null;
      if(timerInterval){clearInterval(timerInterval);timerInterval=null}
      statusDot.classList.add('idle');
    }

    // Stats
    document.getElementById('statTotal').textContent=data.total_formatted;
    document.getElementById('statApps').textContent=data.app_count;
    document.getElementById('statOpens').textContent=data.total_opens;
    if(data.apps.length>0){
      document.getElementById('statTop').textContent=data.apps[0].app;
      document.getElementById('statTopLabel').textContent='\u6700\u5e38\u7528';
    } else {
      document.getElementById('statTop').textContent='-';
    }

    // Track known apps for color settings
    trackApps(data.apps.map(a=>a.app));

    // App list (Page 2)
    const maxSec=data.apps.length>0?data.apps[0].total_seconds:1;
    document.getElementById('appList').innerHTML=data.apps.map((a,i)=>{
      const isActive=a.status==='active';
      const pct=Math.max(2,a.total_seconds/maxSec*100);
      const dc=appColor(a.app);
      return `<div class="app-row ${isActive?'active-session':''}" style="animation-delay:${i*0.05}s">
        <div class="app-dot" style="background:${dc}"></div>
        <div class="app-info">
          <div class="app-name">${a.app}${isActive?' <span class="app-badge live">\u4f7f\u7528\u4e2d \u2661</span>':''}</div>
          <div style="display:flex;align-items:center;gap:10px;margin-top:4px;font-size:0.72em;color:var(--text-dim);font-weight:500">
            <span>${a.open_count}\u6b21\u6253\u5f00</span><span>${a.percentage}%</span>${isActive?'<span>'+a.current_session_formatted+'</span>':''}
          </div>
          <div class="app-bar-bg"><div class="app-bar-fill ${isActive?'live':''}" style="width:${pct}%"></div></div>
          <div class="app-actions">
            <button class="app-toggle-btn" onclick="event.stopPropagation();toggleApp('${a.app.replace(/'/g,"\\'")}','start');">\u5f00\u542f</button>
            <button class="app-toggle-btn stop" onclick="event.stopPropagation();toggleApp('${a.app.replace(/'/g,"\\'")}','stop');">\u5173\u95ed</button>
          </div>
        </div>
        <div class="app-right">
          <div class="app-time">
            <div class="app-time-value">${a.total_formatted}</div>
            <div class="app-time-pct">${a.total_minutes}\u5206\u949f</div>
          </div>
        </div>
      </div>`;
    }).join('')||'<div style="text-align:center;padding:40px;color:var(--text-dim);font-weight:500">\u4eca\u5929\u8fd8\u6ca1\u6709\u6d3b\u52a8\u54e6\uff5e</div>';

    // Longest session
    const lc=document.getElementById('longestCard');
    if(longest.found){
      lc.classList.add('show');
      document.getElementById('longestValue').textContent=longest.duration_formatted;
      document.getElementById('longestApp').textContent=longest.app;
      document.getElementById('longestTime').textContent=longest.started+' \u2192 '+longest.ended;
    }else{lc.classList.remove('show')}

    // Sync toggles + status pills from /api/screentime/status
    try{
      const statusRes=await fetch(API+'/api/screentime/status');
      const status=await statusRes.json();

      // Sync settings page toggles
      chargingOn = status.charging;
      locationOn = status.at_home;
      document.getElementById('chargingToggle').classList.toggle('on', chargingOn);
      document.getElementById('locationToggle').classList.toggle('on', locationOn);

      // Sync home page status pills
      const cPill=document.getElementById('chargingPill');
      const lPill=document.getElementById('locationPill');
      if(status.charging){
        cPill.className='status-pill charging-on';
        document.getElementById('chargingPillText').textContent='\u5145\u7535\u4e2d';
      } else {
        cPill.className='status-pill charging-off';
        document.getElementById('chargingPillText').textContent='\u672a\u5145\u7535';
      }
      if(status.at_home){
        lPill.className='status-pill loc-home';
        document.getElementById('locationPillText').textContent='\u5728\u5bb6';
      } else {
        lPill.className='status-pill loc-away';
        document.getElementById('locationPillText').textContent='\u5916\u51fa';
      }
    }catch(e){}

    // Load data tab content if visible
    if(currentPage===2){loadCalendar();loadHeatmap();loadWeekly();}
    if(currentPage===3) loadSessions();
  }catch(e){
    console.error(e);
  }
}

// ============ Weekly Chart ============
async function loadWeekly(){
  try{
    const res=await fetch(API+'/api/screentime/weekly');
    const data=await res.json();
    const days=Object.entries(data.days).sort((a,b)=>a[0].localeCompare(b[0]));
    const maxSec=Math.max(...days.map(([_,d])=>d.total_seconds),1);
    const todayStr=new Date().toISOString().slice(0,10);
    document.getElementById('weeklyChart').innerHTML=days.map(([date,d])=>{
      const h=Math.max(4,d.total_seconds/maxSec*160);
      const isToday=date===todayStr;
      const dayOfWeek=new Date(date+'T00:00:00').getDay();
      const cnDay=WEEKDAY_CN[dayOfWeek]||d.weekday;
      return `<div class="week-col">
        <div class="week-bar-val">${d.total_formatted}</div>
        <div class="week-bar ${isToday?'today':''}" style="--bar-h:${h}px;height:${h}px" title="${date}: ${d.total_formatted}"></div>
        <div class="week-bar-label ${isToday?'today':''}">${cnDay}</div>
      </div>`;
    }).join('');
  }catch(e){}
}

// ============ Heatmap ============
async function loadHeatmap(){
  try{
    const res=await fetch(API+'/api/screentime/hourly');
    const data=await res.json();
    const hours=data.hours;
    const maxSec=Math.max(...Object.values(hours).map(h=>h.total_seconds),1);
    let html='';
    for(let h=0;h<24;h++){
      const info=hours[h]||{total_seconds:0,session_count:0,total_formatted:'0\u5206'};
      const ratio=info.total_seconds/maxSec;
      let level='';
      if(ratio>0.75) level='l4';
      else if(ratio>0.5) level='l3';
      else if(ratio>0.25) level='l2';
      else if(ratio>0) level='l1';
      const label=h.toString().padStart(2,'0');
      html+=`<div class="heatmap-cell ${level}" title="${label}:00 - ${info.total_formatted} (${info.session_count}\u6b21\u4f1a\u8bdd)">${label}</div>`;
    }
    document.getElementById('heatmap').innerHTML=html;
  }catch(e){}
}

// ============ Sessions ============
async function loadSessions(){
  try{
    // Fetch sessions and hourly data in parallel
    const [res, hourlyRes]=await Promise.all([
      fetch(API+'/api/screentime/sessions'),
      fetch(API+'/api/screentime/hourly')
    ]);
    const data=await res.json();

    // Render hourly stacked bar chart with per-app colors
    try{
      const hourlyData=await hourlyRes.json();
      const hours=hourlyData.hours;
      const maxSec=Math.max(...Object.values(hours).map(h=>{
        const apps=h.apps||{};
        return Object.values(apps).reduce((a,b)=>a+b,0);
      }),1);
      const nowHour=new Date().getHours();
      let chartHtml='';
      // Store hourly data for tooltip
      window._hourlyApps={};
      for(let h=0;h<24;h++){
        const info=hours[h]||{total_seconds:0,apps:{}};
        const apps=info.apps||{};
        const totalSec=Object.values(apps).reduce((a,b)=>a+b,0);
        const barH=maxSec>0?Math.max(0,totalSec/maxSec*200):0;
        const totalMin=Math.round(totalSec/60);
        window._hourlyApps[h]={apps,totalMin};
        let segsHtml='';
        if(totalSec>0){
          const entries=Object.entries(apps).sort((a,b)=>b[1]-a[1]);
          for(const [app,secs] of entries){
            const segH=Math.max(1,secs/totalSec*barH);
            const color=appColor(app);
            segsHtml+=`<div class="hourly-seg" style="height:${segH}px;background:${color}"></div>`;
          }
        }
        chartHtml+=`<div class="hourly-col" data-hour="${h}" onmouseenter="showHourlyTip(event,${h})" onmouseleave="hideHourlyTip()" ontouchstart="showHourlyTip(event,${h})" ontouchend="hideHourlyTip()">
          <div class="hourly-bar-val">${totalMin>0?totalMin:''}</div>
          <div class="hourly-bar" style="height:${barH}px">${segsHtml}</div>
          <div class="hourly-label">${h}</div>
        </div>`;
      }
      // Red line for current hour
      const lineLeft=((nowHour+0.5)/24*100).toFixed(1);
      chartHtml+=`<div class="hourly-now-line" style="left:${lineLeft}%"></div>`;
      document.getElementById('hourlyChart').innerHTML=chartHtml;
    }catch(e){}

    trackApps(data.sessions.map(s=>s.app));
    document.getElementById('sessionList').innerHTML=data.sessions.map((s,i)=>{
      const endStr=s.end?s.end.split(' ').pop():'\u8fdb\u884c\u4e2d';
      const startStr=s.start.split(' ').pop();
      const dc=appColor(s.app);
      const endVal=s.end||'';
      const startVal=s.start||'';
      return `<div class="session-item" onclick="toggleSessionEdit(this)" data-sid="${s.id}">
        <div class="session-summary">
          <div class="session-dot" style="background:${dc}"></div>
          <span class="session-app">${s.app}</span>
          <span class="session-time">${startStr} \u2192 ${endStr}</span>
          <span class="session-dur">${s.duration_formatted}</span>
        </div>
        <div class="session-edit">
          <div class="session-edit-inner">
            <div>
              <label>\u5e94\u7528\u540d\u79f0</label>
              <input type="text" class="se-app" value="${s.app.replace(/"/g,'&quot;')}" onclick="event.stopPropagation()">
            </div>
            <div>
              <label>\u5f00\u59cb\u65f6\u95f4</label>
              <input type="text" class="se-start" value="${startVal}" onclick="event.stopPropagation()" placeholder="YYYY-MM-DD HH:MM:SS">
            </div>
            <div>
              <label>\u7ed3\u675f\u65f6\u95f4</label>
              <input type="text" class="se-end" value="${endVal}" onclick="event.stopPropagation()" placeholder="YYYY-MM-DD HH:MM:SS">
            </div>
            <div class="session-edit-actions">
              <button class="se-btn delete" onclick="event.stopPropagation();deleteSession(${s.id});">\u5220\u9664</button>
              <button class="se-btn" onclick="event.stopPropagation();toggleSessionEdit(this.closest('.session-item'));">\u53d6\u6d88</button>
              <button class="se-btn save" onclick="event.stopPropagation();saveSession(this.closest('.session-item'));">\u4fdd\u5b58</button>
            </div>
          </div>
        </div>
      </div>`;
    }).join('')||'<div style="text-align:center;padding:30px;color:var(--text-dim);font-weight:500">\u6682\u65e0\u4f1a\u8bdd\u8bb0\u5f55\uff5e</div>';
  }catch(e){}
}

function toggleSessionEdit(el){
  if(el.classList.contains('expanded')){
    el.classList.remove('expanded');
  } else {
    document.querySelectorAll('.session-item.expanded').forEach(e=>e.classList.remove('expanded'));
    el.classList.add('expanded');
  }
}

async function saveSession(el){
  const id=el.dataset.sid;
  const endTime=el.querySelector('.se-end').value;
  const startTime=el.querySelector('.se-start').value;
  const body={};
  if(endTime) body.end_ts=endTime;
  if(startTime) body.start_ts=startTime;
  try{
    await fetch(API+'/api/screentime/correct/'+id,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(body)
    });
    showToast('(>_<) \u5df2\u4fdd\u5b58\u4fee\u6539\uff5e');
    refreshAll();
  }catch(e){
    showToast('(>_<) \u4fdd\u5b58\u5931\u8d25...');
  }
}

async function deleteSession(id){
  if(!confirm('\u786e\u5b9a\u8981\u5220\u9664\u8fd9\u4e2a\u4f1a\u8bdd\u5417\uff1f')) return;
  await fetch(API+'/api/screentime/session/'+id,{method:'DELETE'});
  showToast('(-_-)zzz \u5df2\u5220\u9664\uff5e');
  refreshAll();
}

// ============ Toggle App ============
async function toggleApp(app, action){
  try{
    await fetch(API+'/api/screentime/toggle/'+encodeURIComponent(app),{method:'GET'});
    if(action==='start'){
      showToast('(*^-^*) \u5df2\u5f00\u542f\u8bb0\u5f55\uff5e');
    } else {
      showToast('(-_-)zzz \u5df2\u5173\u95ed\uff5e');
    }
    setTimeout(()=>refreshAll(), 500);
  }catch(e){
    showToast('(>_<) \u64cd\u4f5c\u5931\u8d25...');
  }
}

// ============ Charging Toggle ============
async function toggleCharging(){
  chargingOn = !chargingOn;
  const ct=document.getElementById('chargingToggle');
  ct.classList.toggle('on', chargingOn);
  try{
    if(chargingOn){
      await fetch(API+'/api/event/charging_start');
      showToast('(^o^)/ \u5f00\u59cb\u5145\u7535\uff5e');
    } else {
      await fetch(API+'/api/event/charging_stop');
      showToast('(-_-) \u505c\u6b62\u5145\u7535\uff5e');
    }
  }catch(e){}
}

// ============ Location Toggle ============
async function toggleLocation(){
  locationOn = !locationOn;
  const lt=document.getElementById('locationToggle');
  lt.classList.toggle('on', locationOn);
  try{
    if(locationOn){
      await fetch(API+'/api/event/arrived_home');
      showToast('(=^-^=) \u5df2\u5230\u5bb6\uff5e');
    } else {
      await fetch(API+'/api/event/left_home');
      showToast('(^_^)/ \u5df2\u51fa\u95e8\uff5e');
    }
  }catch(e){}
}

// ============ Refresh Button ============
function doRefresh(){
  refreshAll();
  showToast('(*^_^*) \u6570\u636e\u5df2\u5237\u65b0\uff5e');
}

// ============ Reset All ============
async function resetAll(){
  if(!confirm('\u786e\u5b9a\u8981\u91cd\u7f6e\u6240\u6709\u6570\u636e\u5417\uff1f')) return;
  await fetch(API+'/api/screentime/reset_all');
  showToast('(*^_^*) \u5df2\u91cd\u7f6e\uff5e');
  refreshAll();
}

// ============ Collapsible Hourly Chart ============
function toggleHourlyChart(){
  const wrap=document.getElementById('hourlyWrap');
  const btn=document.getElementById('hourlyToggleBtn');
  if(wrap.classList.contains('expanded')){
    wrap.classList.remove('expanded');
    btn.textContent='\u67e5\u770b\u65f6\u95f4\u5206\u5e03';
  }else{
    wrap.classList.add('expanded');
    btn.textContent='\u6536\u8d77\u65f6\u95f4\u5206\u5e03';
  }
}

// ============ History Panels ============
async function toggleHistory(type){
  const wrapId = type==='charging' ? 'chargingWrap' : 'locationWrap';
  const panelId = type==='charging' ? 'chargingHistory' : 'locationHistory';
  const wrap = document.getElementById(wrapId);
  if(wrap.classList.contains('expanded')){
    wrap.classList.remove('expanded');
    return;
  }
  wrap.classList.add('expanded');
  await loadHistory(type);
}

async function loadHistory(type){
  const panelId = type==='charging' ? 'chargingHistory' : 'locationHistory';
  const endpoint = type==='charging' ? '/api/history/charging' : '/api/history/location';
  const panel = document.getElementById(panelId);
  panel.innerHTML='<div class="history-empty">loading...</div>';
  try{
    const res=await fetch(API+endpoint);
    const data=await res.json();

    // Paired display with by_day grouping
    const byDay=data.by_day||{};
    const dayKeys=Object.keys(byDay).sort().reverse();

    if(dayKeys.length===0){
      // Fallback to events array
      const events=data.events||[];
      if(events.length===0){
        panel.innerHTML='<div class="history-empty">(*^_^*) \u8fd8\u6ca1\u6709\u8bb0\u5f55\u54e6\uff5e</div>';
        return;
      }
      // Render old-style events as fallback
      const typeLabels = type==='charging'
        ? {charging_start:'\u5f00\u59cb\u5145\u7535',charging_stop:'\u505c\u6b62\u5145\u7535'}
        : {arrived_home:'\u5230\u5bb6',left_home:'\u51fa\u95e8'};
      panel.innerHTML=events.map(ev=>{
        const label=typeLabels[ev.type]||ev.type;
        const ts=ev.timestamp||ev.ts||'';
        return `<div class="history-event">
          <div class="history-event-info">
            <span class="history-event-type">${label}</span>
            <span class="history-event-time">${ts}</span>
          </div>
          <button class="history-del-btn" onclick="event.stopPropagation();deleteEvent(${ev.id},'${type}')">\u5220\u9664</button>
        </div>`;
      }).join('');
      return;
    }

    let html='';
    for(const day of dayKeys){
      const pairs=byDay[day]||[];
      // Day header: e.g. "3\u670827\u65e5"
      const parts=day.split('-');
      const dayLabel=parseInt(parts[1])+'\u6708'+parseInt(parts[2])+'\u65e5';
      html+=`<div class="history-event" style="background:rgba(126,200,227,0.05);font-weight:700;font-size:0.85em;color:var(--text)">${dayLabel}</div>`;

      for(const pair of pairs){
        if(type==='location'&&pair.status==='home_all_day'){
          html+=`<div class="history-event">
            <div class="history-event-info">
              <span class="history-event-type">\u4eca\u65e5\u4e00\u76f4\u5728\u5bb6</span>
            </div>
          </div>`;
          continue;
        }

        const startTime=pair.start_time||'';
        const endTime=pair.end_time||'';
        const startShort=startTime?startTime.split(' ').pop().slice(0,5):'?';
        let endShort='';
        let durText='';
        const pairId=pair.start_id||pair.id||0;

        if(pair.ongoing){
          // Calculate ongoing duration
          const startMs=startTime?new Date(startTime).getTime():0;
          const nowMs=Date.now();
          const diffMin=startMs?Math.round((nowMs-startMs)/60000):0;
          if(type==='charging'){
            endShort='\u5145\u7535\u4e2d';
            durText='\u5df2\u5145'+diffMin+'\u5206\u949f';
          }else{
            endShort='\u5916\u51fa\u4e2d';
            durText='\u5df2\u51fa\u95e8'+diffMin+'\u5206\u949f';
          }
        }else{
          endShort=endTime?endTime.split(' ').pop().slice(0,5):'?';
          const durMin=pair.duration_minutes||0;
          durText=durMin+'\u5206\u949f';
        }

        html+=`<div class="history-event">
          <div class="history-event-info">
            <span class="history-event-type">${startShort} ~ ${endShort}</span>
            <span class="history-event-time">${durText}</span>
          </div>
          ${pairId?`<button class="history-del-btn" onclick="event.stopPropagation();deleteEvent(${pairId},'${type}')">\u5220\u9664</button>`:''}
        </div>`;
      }
    }
    panel.innerHTML=html;
  }catch(e){
    panel.innerHTML='<div class="history-empty">(>_<) \u52a0\u8f7d\u5931\u8d25...</div>';
  }
}

async function deleteEvent(id, type){
  try{
    await fetch(API+'/api/history/delete/'+id,{method:'DELETE'});
    showToast('(*^-^*) \u5df2\u5220\u9664\uff5e');
    await loadHistory(type);
  }catch(e){
    showToast('(>_<) \u5220\u9664\u5931\u8d25...');
  }
}

// ============ App Color Settings ============
let knownApps = new Set();

function updateAppColorList(){
  const list=document.getElementById('appColorList');
  if(!list||knownApps.size===0) return;
  list.innerHTML=[...knownApps].sort().map(app=>{
    const color=appColor(app);
    return `<div class="app-color-row">
      <div class="app-color-dot" style="background:${color}" id="dot_${btoa(encodeURIComponent(app))}"></div>
      <span class="app-color-name">${app}</span>
      <input type="color" class="app-color-input" value="${color}" onchange="onAppColorChange('${app.replace(/'/g,"\\'")}',this.value,this)">
    </div>`;
  }).join('');
}

function onAppColorChange(app, color, input){
  setAppColor(app, color);
  const dotId='dot_'+btoa(encodeURIComponent(app));
  const dot=document.getElementById(dotId);
  if(dot) dot.style.background=color;
}

function trackApps(apps){
  let changed=false;
  for(const a of apps){
    if(!knownApps.has(a)){knownApps.add(a);changed=true;}
  }
  if(changed) updateAppColorList();
}

// ============ Hourly Tooltip ============
function showHourlyTip(ev,hour){
  const tip=document.getElementById('hourlyTooltip');
  const d=window._hourlyApps&&window._hourlyApps[hour];
  if(!d||d.totalMin===0){tip.style.display='none';return;}
  let html=`<div class="ht-hour">${hour}:00 ~ ${hour}:59</div>`;
  const entries=Object.entries(d.apps).sort((a,b)=>b[1]-a[1]);
  for(const [app,secs] of entries){
    const mins=Math.round(secs/60);
    if(mins<1) continue;
    html+=`<div class="ht-app"><span class="ht-dot" style="background:${appColor(app)}"></span>${app}: ${mins}\u5206\u949f</div>`;
  }
  tip.innerHTML=html;
  tip.style.display='block';
  const rect=ev.currentTarget.getBoundingClientRect();
  let left=rect.left+rect.width/2-60;
  let top=rect.top-tip.offsetHeight-6;
  if(top<4) top=rect.bottom+6;
  if(left<4) left=4;
  if(left+120>window.innerWidth) left=window.innerWidth-124;
  tip.style.left=left+'px';
  tip.style.top=top+'px';
}
function hideHourlyTip(){
  document.getElementById('hourlyTooltip').style.display='none';
}

// ============ Calendar ============
let calYear=2026, calMonth=3;
let calMonthData=null;

function calendarPrevMonth(){
  calMonth--;
  if(calMonth<1){calMonth=12;calYear--;}
  loadCalendar();
}
function calendarNextMonth(){
  calMonth++;
  if(calMonth>12){calMonth=1;calYear++;}
  loadCalendar();
}

async function loadCalendar(){
  const monthEl=document.getElementById('calMonth');
  monthEl.textContent=calYear+'\u5e74'+calMonth+'\u6708';
  const grid=document.getElementById('calendarGrid');
  grid.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-dim)">loading...</div>';
  try{
    const res=await fetch(API+'/api/screentime/month/'+calYear+'/'+calMonth);
    calMonthData=await res.json();
  }catch(e){
    calMonthData={days:{}};
  }
  renderCalendarGrid();
}

function renderCalendarGrid(){
  const grid=document.getElementById('calendarGrid');
  const firstDay=new Date(calYear,calMonth-1,1);
  const lastDay=new Date(calYear,calMonth,0);
  const daysInMonth=lastDay.getDate();
  // Monday=0 ... Sunday=6
  let startDow=firstDay.getDay()-1;
  if(startDow<0) startDow=6;

  const now=new Date();
  const todayStr=now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0');
  const days=calMonthData&&calMonthData.days?calMonthData.days:{};

  // Find max seconds for color scaling
  const allSecs=Object.values(days).map(d=>d.total_seconds||0);
  const maxSec=Math.max(...allSecs,1);

  let html='';
  // Empty cells before first day
  for(let i=0;i<startDow;i++){
    html+=`<div class="calendar-cell empty animated" style="animation-delay:${i*0.02}s"></div>`;
  }
  for(let d=1;d<=daysInMonth;d++){
    const dateStr=calYear+'-'+String(calMonth).padStart(2,'0')+'-'+String(d).padStart(2,'0');
    const dayData=days[dateStr]||days[String(d)];
    const isToday=dateStr===todayStr;
    const sec=dayData?dayData.total_seconds||0:0;
    // Use non-linear scaling: 0.2 + 0.8 * ratio, so any data is clearly visible
    const rawRatio=sec/maxSec;
    const ratio=sec>0?(0.2+0.8*rawRatio):0;
    let level='';
    if(ratio>0.75) level='cl4';
    else if(ratio>0.5) level='cl3';
    else if(ratio>0.25) level='cl2';
    else if(ratio>0) level='cl1';
    const hasData=sec>0;
    const cellIdx=startDow+d-1;
    const onClick=hasData?`onclick="showDayReport('${dateStr}')"`:''
    html+=`<div class="calendar-cell animated ${level} ${isToday?'today':''} ${hasData?'has-data':''}" style="animation-delay:${cellIdx*0.02}s" ${onClick}>
      ${d}${isToday?'<div class="cal-today-dot"></div>':''}
    </div>`;
  }
  grid.innerHTML=html;
}

async function showDayReport(dateStr){
  document.getElementById('calendarView').style.display='none';
  document.getElementById('dayReportView').style.display='block';
  const content=document.getElementById('dayReportContent');
  content.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-dim)">loading...</div>';
  try{
    const res=await fetch(API+'/api/screentime/day/'+dateStr);
    const data=await res.json();
    const totalFmt=data.total_formatted||fmt(data.total_seconds||0);
    const apps=data.apps||[];
    const totalSec=data.total_seconds||1;

    let appsHtml=apps.map(a=>{
      const pct=Math.round((a.total_seconds||0)/totalSec*100);
      const color=appColor(a.app);
      return `<div class="day-report-app">
        <span class="dr-dot" style="background:${color}"></span>
        <span class="dr-name">${a.app}</span>
        <span class="dr-time">${a.total_formatted||fmt(a.total_seconds||0)}</span>
        <span class="dr-pct">${pct}%</span>
      </div>`;
    }).join('');

    // Build heatmap for this day
    const hours=data.hourly||{};
    const maxH=Math.max(...Object.values(hours).map(h=>h.total_seconds||0),1);
    let heatHtml='';
    for(let h=0;h<24;h++){
      const info=hours[h]||{total_seconds:0,session_count:0,total_formatted:'0\u5206',apps:{}};
      const ratio=info.total_seconds/maxH;
      let level='';
      if(ratio>0.75) level='l4';
      else if(ratio>0.5) level='l3';
      else if(ratio>0.25) level='l2';
      else if(ratio>0) level='l1';
      const label=String(h).padStart(2,'0');
      const appInfo=info.apps||{};
      let tipParts=[label+':00'];
      for(const [app,secs] of Object.entries(appInfo).sort((a,b)=>b[1]-a[1])){
        tipParts.push(app+': '+Math.round(secs/60)+'\u5206');
      }
      heatHtml+=`<div class="heatmap-cell ${level}" title="${tipParts.join('\n')}">${label}</div>`;
    }

    content.innerHTML=`
      <div class="day-report-header">${dateStr}</div>
      <div class="day-report-total">${totalFmt}</div>
      <div class="data-card" style="margin-bottom:16px">
        <div class="data-card-title">\u5e94\u7528\u4f7f\u7528\u660e\u7ec6</div>
        <div class="day-report-apps">${appsHtml||'<div style="text-align:center;color:var(--text-dim)">\u65e0\u6570\u636e</div>'}</div>
      </div>
      <div class="data-card">
        <div class="data-card-title">24\u5c0f\u65f6\u6d3b\u52a8\u70ed\u529b\u56fe</div>
        <div class="heatmap">${heatHtml}</div>
      </div>`;
  }catch(e){
    content.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-dim)">(>_<) \u52a0\u8f7d\u5931\u8d25...</div>';
  }
}

function backToCalendar(){
  document.getElementById('dayReportView').style.display='none';
  document.getElementById('calendarView').style.display='block';
}

// ============ Background Color Settings ============
function onBgChange(){
  const c1=document.getElementById('bgColor1').value;
  const c2=document.getElementById('bgColor2').value;
  const c3=document.getElementById('bgColor3').value;
  localStorage.setItem('bg_color1',c1);
  localStorage.setItem('bg_color2',c2);
  localStorage.setItem('bg_color3',c3);
  applyBgSettings();
}
function applyBgSettings(){
  const c1=localStorage.getItem('bg_color1')||'#d4e8f5';
  const c2=localStorage.getItem('bg_color2')||'#b8d8ee';
  const c3=localStorage.getItem('bg_color3')||'#a8d0e0';
  document.body.style.background=`linear-gradient(135deg,${c1},${c2},${c3},${c1})`;
  document.body.style.backgroundSize='400% 400%';
  const el1=document.getElementById('bgColor1');
  const el2=document.getElementById('bgColor2');
  const el3=document.getElementById('bgColor3');
  if(el1) el1.value=c1;
  if(el2) el2.value=c2;
  if(el3) el3.value=c3;
}

// ============ Watermark Settings ============
function onWatermarkChange(){
  const color=document.getElementById('wmColor').value;
  const opacity=document.getElementById('wmOpacity').value;
  const size=document.getElementById('wmSize').value;
  const content=(document.getElementById('wmContent')||{}).value||'';
  localStorage.setItem('watermark_color',color);
  localStorage.setItem('watermark_opacity',opacity);
  localStorage.setItem('watermark_size',size);
  localStorage.setItem('watermark_content',content);
  applyWatermarkSettings();
}

function applyWatermarkSettings(){
  const color=localStorage.getItem('watermark_color')||'#3a5068';
  const opacity=parseInt(localStorage.getItem('watermark_opacity')||'100',10);
  const size=parseInt(localStorage.getItem('watermark_size')||'100',10);
  const content=localStorage.getItem('watermark_content')||'';
  const spans=document.querySelectorAll('.kaomoji-bg span');
  const kaomojiList=content?content.split(',').map(s=>s.trim()).filter(Boolean):[];
  spans.forEach((sp,idx)=>{
    sp.style.color=color;
    sp.style.opacity=(opacity/100).toString();
    // Store original font-size on first run
    if(!sp.getAttribute('data-orig-fontsize')){
      const fs=parseFloat(sp.style.fontSize)||16;
      sp.setAttribute('data-orig-fontsize', fs);
    }
    const origFs=parseFloat(sp.getAttribute('data-orig-fontsize'));
    sp.style.fontSize=Math.round(origFs*(size/100))+'px';
    // Preserve original rotation only (no scale needed, font-size handles sizing)
    const origRotate=sp.getAttribute('data-orig-rotate');
    if(!origRotate){
      const m=sp.style.transform.match(/rotate\([^)]*\)/);
      sp.setAttribute('data-orig-rotate', m?m[0]:'');
    }
    sp.style.transform=sp.getAttribute('data-orig-rotate')||'';
    // Update content if custom kaomoji set
    if(kaomojiList.length>0){
      sp.textContent=kaomojiList[idx%kaomojiList.length];
    }
  });
  // Sync inputs if they exist
  const cEl=document.getElementById('wmColor');
  const oEl=document.getElementById('wmOpacity');
  const sEl=document.getElementById('wmSize');
  const tEl=document.getElementById('wmContent');
  if(cEl) cEl.value=color;
  if(oEl){oEl.value=opacity;const ov=document.getElementById('wmOpacityVal');if(ov)ov.textContent=opacity+'%';}
  if(sEl){sEl.value=size;const sv=document.getElementById('wmSizeVal');if(sv)sv.textContent=size+'%';}
  if(tEl&&content) tEl.value=content;
}

// ============ Timezone Settings ============
async function loadTimezone(){
  try{
    const res=await fetch(API+'/api/settings/timezone');
    const data=await res.json();
    const el=document.getElementById('tzCurrent');
    const inp=document.getElementById('tzOffsetInput');
    if(el) el.textContent='\u5f53\u524d\u65f6\u533a\uff1a'+data.label+' ('+data.timezone_name+')';
    if(inp) inp.value=data.timezone_offset;
  }catch(e){}
}

async function saveTimezone(){
  const offset=parseFloat(document.getElementById('tzOffsetInput').value);
  if(isNaN(offset)||offset<-12||offset>14){
    showToast('(>_<) \u65e0\u6548\u7684UTC\u504f\u79fb\u503c...');
    return;
  }
  try{
    const res=await fetch(API+'/api/settings/timezone',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({offset:offset})
    });
    const data=await res.json();
    if(data.error){
      showToast('(>_<) '+data.error);
    }else{
      showToast('(*^_^*) \u65f6\u533a\u5df2\u66f4\u65b0\uff5e');
      loadTimezone();
      refreshAll();
    }
  }catch(e){
    showToast('(>_<) \u4fdd\u5b58\u5931\u8d25...');
  }
}

// ============ Init ============
applyBgSettings();
applyWatermarkSettings();
loadCalendar();
loadTimezone();
refreshAll();
setInterval(refreshAll, 30000);
</script>
</body>
</html>"""
