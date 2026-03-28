"""Dashboard — returns a complete HTML string for a multi-page screen time dashboard.
Theme: macaron day — Cinnamoroll-inspired Glassmorphism with swipeable pages.
"""


def render_dashboard() -> str:
    return r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>macaron day</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700;900&family=ZCOOL+XiaoWei&display=swap');

*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}

:root{
  --bg-start:#f8fcff;
  --bg-mid:#e8f4fd;
  --bg-end:#e0f5f0;
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
  color:var(--text-light);
  font-family:'Zen Maru Gothic',sans-serif;
  animation:kaomojiFade 30s ease-in-out infinite;
}
@keyframes kaomojiFade{
  0%,100%{transform:translateY(0);opacity:var(--kao-op)}
  50%{transform:translateY(-12px);opacity:calc(var(--kao-op) * 0.6)}
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

/* ============ PAGE 4: Sessions ============ */
.session-list{display:flex;flex-direction:column;gap:8px;max-height:calc(100vh - 200px);overflow-y:auto}
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

.settings-footer{
  text-align:center;color:var(--text-dim);
  font-size:0.75em;margin-top:32px;padding-bottom:20px;
  font-weight:500;
}

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
  <span style="top:5%;left:8%;font-size:18px;--kao-op:0.04;animation-delay:0s;transform:rotate(-8deg)">&#x2768;&#x1d22;&#x2027;&#x203b;&#x2027;&#x1d22;&#x2769;</span>
  <span style="top:12%;right:12%;font-size:24px;--kao-op:0.035;animation-delay:-4s;transform:rotate(5deg)">&#x17b7;&gt;&#x1d17;&lt;&#x17b7;</span>
  <span style="top:22%;left:20%;font-size:16px;--kao-op:0.045;animation-delay:-8s;transform:rotate(-3deg)">&#x10ae;&#x2082;&#x207d;&#x5e;&#x02f6;&#x2a01;&#x0337;&#x035d;&#x2a01;&#x02f6;&#x5e;&#x2082;&#x29;&#x25de;</span>
  <span style="top:30%;right:6%;font-size:20px;--kao-op:0.04;animation-delay:-2s;transform:rotate(10deg)">&#x2cb;&#x207e;&#x2310;&#x2019;&#x0348;&#x0020;&#x0245;&#x0020;&#x2010;&#x0348;&#x207e;&#x2cb;</span>
  <span style="top:40%;left:5%;font-size:30px;--kao-op:0.03;animation-delay:-6s;transform:rotate(-12deg)">/&#x1d20; - &#x02d5; -&#x30de;</span>
  <span style="top:48%;right:18%;font-size:14px;--kao-op:0.05;animation-delay:-10s;transform:rotate(7deg)">&#x2cb6;&#x2461;&#xff65;-&#xff65;&#x2461;&#x10d0;</span>
  <span style="top:55%;left:25%;font-size:22px;--kao-op:0.035;animation-delay:-14s;transform:rotate(-5deg)">&#x2036; &#x1dbb; &#x1d97; &#x1d17;</span>
  <span style="top:62%;right:8%;font-size:28px;--kao-op:0.04;animation-delay:-3s;transform:rotate(15deg)">&#x2cb;&#x207e;&#x2310;&#x2019;&#x0348;&#x0020;&#x0245;&#x0020;&#x2010;&#x0348;&#x207e;&#x2cb;</span>
  <span style="top:70%;left:12%;font-size:16px;--kao-op:0.045;animation-delay:-7s;transform:rotate(-10deg)">&#x17b7;&gt;&#x1d17;&lt;&#x17b7;</span>
  <span style="top:78%;right:22%;font-size:18px;--kao-op:0.03;animation-delay:-11s;transform:rotate(3deg)">/&#x1d20; - &#x02d5; -&#x30de;</span>
  <span style="top:85%;left:6%;font-size:40px;--kao-op:0.03;animation-delay:-5s;transform:rotate(8deg)">&#x2768;&#x1d22;&#x2027;&#x203b;&#x2027;&#x1d22;&#x2769;</span>
  <span style="top:90%;right:10%;font-size:15px;--kao-op:0.04;animation-delay:-9s;transform:rotate(-6deg)">&#x2cb6;&#x2461;&#xff65;-&#xff65;&#x2461;&#x10d0;</span>
  <span style="top:18%;left:55%;font-size:20px;--kao-op:0.035;animation-delay:-13s;transform:rotate(12deg)">&#x2036; &#x1dbb; &#x1d97; &#x1d17;</span>
  <span style="top:35%;left:45%;font-size:16px;--kao-op:0.04;animation-delay:-1s;transform:rotate(-15deg)">&#x10ae;&#x2082;&#x207d;&#x5e;&#x02f6;&#x2a01;&#x0337;&#x035d;&#x2a01;&#x02f6;&#x5e;&#x2082;&#x29;&#x25de;</span>
  <span style="top:52%;left:60%;font-size:24px;--kao-op:0.03;animation-delay:-12s;transform:rotate(6deg)">/&#x1d20; - &#x02d5; -&#x30de;</span>
  <span style="top:68%;left:50%;font-size:18px;--kao-op:0.045;animation-delay:-15s;transform:rotate(-4deg)">&#x17b7;&gt;&#x1d17;&lt;&#x17b7;</span>
  <span style="top:82%;left:40%;font-size:22px;--kao-op:0.035;animation-delay:-8s;transform:rotate(9deg)">&#x2cb6;&#x2461;&#xff65;-&#xff65;&#x2461;&#x10d0;</span>
  <span style="top:8%;left:70%;font-size:14px;--kao-op:0.05;animation-delay:-16s;transform:rotate(-7deg)">&#x2768;&#x1d22;&#x2027;&#x203b;&#x2027;&#x1d22;&#x2769;</span>
  <span style="top:44%;left:80%;font-size:26px;--kao-op:0.03;animation-delay:-6s;transform:rotate(11deg)">&#x2036; &#x1dbb; &#x1d97; &#x1d17;</span>
  <span style="top:75%;left:70%;font-size:17px;--kao-op:0.04;animation-delay:-10s;transform:rotate(-13deg)">/&#x1d20; - &#x02d5; -&#x30de;</span>
  <span style="top:95%;left:55%;font-size:20px;--kao-op:0.035;animation-delay:-4s;transform:rotate(4deg)">&#x17b7;&gt;&#x1d17;&lt;&#x17b7;</span>
  <span style="top:3%;left:40%;font-size:15px;--kao-op:0.04;animation-delay:-7s;transform:rotate(-9deg)">&#x2cb6;&#x2461;&#xff65;-&#xff65;&#x2461;&#x10d0;</span>
  <span style="top:58%;left:3%;font-size:19px;--kao-op:0.035;animation-delay:-2s;transform:rotate(14deg)">&#x10ae;&#x2082;&#x207d;&#x5e;&#x02f6;&#x2a01;&#x0337;&#x035d;&#x2a01;&#x02f6;&#x5e;&#x2082;&#x29;&#x25de;</span>
  <span style="top:25%;right:3%;font-size:32px;--kao-op:0.03;animation-delay:-11s;transform:rotate(-2deg)">&#x2768;&#x1d22;&#x2027;&#x203b;&#x2027;&#x1d22;&#x2769;</span>
  <span style="top:15%;left:35%;font-size:14px;--kao-op:0.045;animation-delay:-14s;transform:rotate(8deg)">&#x2036; &#x1dbb; &#x1d97; &#x1d17;</span>
  <span style="top:65%;right:30%;font-size:20px;--kao-op:0.04;animation-delay:-3s;transform:rotate(-11deg)">/&#x1d20; - &#x02d5; -&#x30de;</span>
  <span style="top:88%;left:22%;font-size:16px;--kao-op:0.035;animation-delay:-9s;transform:rotate(6deg)">&#x17b7;&gt;&#x1d17;&lt;&#x17b7;</span>
  <span style="top:38%;right:35%;font-size:18px;--kao-op:0.04;animation-delay:-5s;transform:rotate(-8deg)">&#x2cb6;&#x2461;&#xff65;-&#xff65;&#x2461;&#x10d0;</span>
  <span style="top:73%;left:85%;font-size:14px;--kao-op:0.05;animation-delay:-12s;transform:rotate(3deg)">&#x2036; &#x1dbb; &#x1d97; &#x1d17;</span>
  <span style="top:50%;left:92%;font-size:22px;--kao-op:0.03;animation-delay:-1s;transform:rotate(-6deg)">&#x10ae;&#x2082;&#x207d;&#x5e;&#x02f6;&#x2a01;&#x0337;&#x035d;&#x2a01;&#x02f6;&#x5e;&#x2082;&#x29;&#x25de;</span>
</div>

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

      <div class="idle-message" id="idleMessage">&#x6ca1;&#x6709;&#x5728;&#x4f7f;&#x7528;&#x624b;&#x673a;&#x5462; &#x2768;&#x1d22;&#x2027;&#x203b;&#x2027;&#x1d22;&#x2769;</div>

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
      <div class="page-title">&#x6570;&#x636e;&#x5206;&#x6790;</div>
      <div class="page-subtitle">&#x6d3b;&#x52a8;&#x70ed;&#x529b;&#x56fe;&#x4e0e;&#x5468;&#x8d8b;&#x52bf;&#xff5e;</div>

      <div class="data-card">
        <div class="data-card-title">24&#x5c0f;&#x65f6;&#x6d3b;&#x52a8;&#x70ed;&#x529b;&#x56fe;&#xff08;&#x8fd1;7&#x5929;&#xff09;</div>
        <div class="heatmap" id="heatmap"></div>
        <div class="heatmap-legend">
          <span>&#x5c11;</span>
          <div class="heatmap-legend-cell" style="background:rgba(126,200,227,0.04)"></div>
          <div class="heatmap-legend-cell" style="background:rgba(126,200,227,0.12)"></div>
          <div class="heatmap-legend-cell" style="background:rgba(126,200,227,0.28)"></div>
          <div class="heatmap-legend-cell" style="background:rgba(126,200,227,0.48)"></div>
          <div class="heatmap-legend-cell" style="background:rgba(126,200,227,0.72)"></div>
          <span>&#x591a;</span>
        </div>
      </div>

      <div class="data-card">
        <div class="data-card-title">&#x6bcf;&#x5468;&#x5c4f;&#x5e55;&#x65f6;&#x95f4;&#x8d8b;&#x52bf;</div>
        <div class="weekly-chart" id="weeklyChart"></div>
      </div>
    </div>
  </div>

  <!-- PAGE 4: Sessions -->
  <div class="page" id="page-sessions">
    <div class="page-inner">
      <div class="page-title">&#x4eca;&#x65e5;&#x4f1a;&#x8bdd;</div>
      <div class="page-subtitle">&#x70b9;&#x51fb;&#x4f1a;&#x8bdd;&#x53ef;&#x4ee5;&#x7f16;&#x8f91;&#xff5e;</div>
      <div class="session-list" id="sessionList"><div class="loading" style="height:150px"></div></div>
    </div>
  </div>

  <!-- PAGE 5: Settings -->
  <div class="page" id="page-settings">
    <div class="page-inner">
      <div class="page-title">&#x8bbe;&#x7f6e;</div>
      <div class="page-subtitle">&#x529f;&#x80fd;&#x63a7;&#x5236;&#xff5e;</div>

      <div class="setting-row">
        <div class="setting-label">
          <svg viewBox="0 0 24 24"><path d="M6.7 17.3l-3.4 1.2 1.2-3.4L17.3 2.3a1.4 1.4 0 0 1 2 0l1.4 1.4a1.4 1.4 0 0 1 0 2z"/><line x1="13" y1="6" x2="18" y2="11"/></svg>
          &#x5145;&#x7535;&#x72b6;&#x6001;
        </div>
        <button class="toggle" id="chargingToggle" onclick="toggleCharging()">
          <div class="toggle-thumb"></div>
        </button>
      </div>

      <div class="setting-row">
        <div class="setting-label">
          <svg viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          &#x5728;&#x5bb6;
        </div>
        <button class="toggle" id="locationToggle" onclick="toggleLocation()">
          <div class="toggle-thumb"></div>
        </button>
      </div>

      <button class="setting-btn" onclick="doRefresh()">&#x5237;&#x65b0;&#x6570;&#x636e;</button>
      <button class="setting-btn danger-btn" onclick="resetAll()">&#x91cd;&#x7f6e;&#x6240;&#x6709;</button>

      <div class="settings-footer">&#x5c4f;&#x5e55;&#x65f6;&#x95f4;&#x8ffd;&#x8e2a;&#x5668; v3.0 &#x2661; &#x6bcf;30&#x79d2;&#x81ea;&#x52a8;&#x5237;&#x65b0;</div>
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
const API = window.location.origin;

const DOT_COLORS = ['#7ec8e3','#a8e6cf','#ffc0cb','#ffe4a0','#8ee4af','#b8e4f0','#ffd6e0','#c8e6ff'];
function dotColor(i){ return DOT_COLORS[i % DOT_COLORS.length]; }

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
  if(idx===2){loadHeatmap();loadWeekly();}
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
      if(idx===2){loadHeatmap();loadWeekly();}
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

    // App list (Page 2)
    const maxSec=data.apps.length>0?data.apps[0].total_seconds:1;
    document.getElementById('appList').innerHTML=data.apps.map((a,i)=>{
      const isActive=a.status==='active';
      const pct=Math.max(2,a.total_seconds/maxSec*100);
      const dc=dotColor(i);
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

    // Charging & Location status (for Settings toggles)
    try{
      const chargeRes=await fetch(API+'/api/event/charging_history');
      const chargeData=await chargeRes.json();
      if(chargeData.events&&chargeData.events.length>0){
        const last=chargeData.events[0];
        chargingOn = last.type==='charging_start';
        const ct=document.getElementById('chargingToggle');
        ct.classList.toggle('on', chargingOn);
      }
    }catch(e){}
    try{
      const locRes=await fetch(API+'/api/event/location_history');
      const locData=await locRes.json();
      if(locData.events&&locData.events.length>0){
        const last=locData.events[0];
        locationOn = last.type==='arrived_home';
        const lt=document.getElementById('locationToggle');
        lt.classList.toggle('on', locationOn);
      }
    }catch(e){}

    // Load data tab content if visible
    if(currentPage===2){loadHeatmap();loadWeekly();}
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
      const h=Math.max(4,d.total_seconds/maxSec*140);
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
    const res=await fetch(API+'/api/screentime/sessions');
    const data=await res.json();
    document.getElementById('sessionList').innerHTML=data.sessions.map((s,i)=>{
      const endStr=s.end?s.end.split(' ').pop():'\u8fdb\u884c\u4e2d';
      const startStr=s.start.split(' ').pop();
      const dc=dotColor(i);
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
    showToast('\u17b7>\u1d17<\u17b7 \u5df2\u4fdd\u5b58\u4fee\u6539\uff5e');
    refreshAll();
  }catch(e){
    showToast('\u4fdd\u5b58\u5931\u8d25...');
  }
}

async function deleteSession(id){
  if(!confirm('\u786e\u5b9a\u8981\u5220\u9664\u8fd9\u4e2a\u4f1a\u8bdd\u5417\uff1f')) return;
  await fetch(API+'/api/screentime/session/'+id,{method:'DELETE'});
  showToast('\u0eb6\u2461\uff65-\uff65\u2461\u10d0 \u5df2\u5220\u9664\uff5e');
  refreshAll();
}

// ============ Toggle App ============
async function toggleApp(app, action){
  try{
    await fetch(API+'/api/screentime/toggle/'+encodeURIComponent(app),{method:'GET'});
    if(action==='start'){
      showToast('\u2768\u1d22\u2027\u203b\u2027\u1d22\u2769\u2661 \u5df2\u5f00\u542f\u8bb0\u5f55\uff5e');
    } else {
      showToast('\ua7a8\u2082\u207d\u5e\u02f6\u2a01\u0337\u035d\u2a01\u02f6\u5e\u2082)\u25de \u5df2\u5173\u95ed\uff5e');
    }
    setTimeout(()=>refreshAll(), 500);
  }catch(e){
    showToast('\u64cd\u4f5c\u5931\u8d25...');
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
      showToast('\ua7a8\u2461\uff65-\uff65\u2461\u10d0 \u5f00\u59cb\u5145\u7535\uff5e');
    } else {
      await fetch(API+'/api/event/charging_stop');
      showToast('\ua7a8\u2461\uff65-\uff65\u2461\u10d0 \u505c\u6b62\u5145\u7535\uff5e');
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
      showToast('/\u1d20 - \u02d5 -\u30de \u5df2\u5230\u5bb6\uff5e');
    } else {
      await fetch(API+'/api/event/left_home');
      showToast('/\u1d20 - \u02d5 -\u30de \u5df2\u51fa\u95e8\uff5e');
    }
  }catch(e){}
}

// ============ Refresh Button ============
function doRefresh(){
  refreshAll();
  showToast('/\u1d20 - \u02d5 -\u30de \u6570\u636e\u5df2\u5237\u65b0\uff5e');
}

// ============ Reset All ============
async function resetAll(){
  if(!confirm('\u786e\u5b9a\u8981\u91cd\u7f6e\u6240\u6709\u6570\u636e\u5417\uff1f')) return;
  await fetch(API+'/api/screentime/reset_all');
  showToast('\u10ae\u2082\u207d\u5e\u02f6\u2a01\u0337\u035d\u2a01\u02f6\u5e\u2082)\u25de \u5df2\u91cd\u7f6e\uff5e');
  refreshAll();
}

// ============ Init ============
refreshAll();
setInterval(refreshAll, 30000);
</script>
</body>
</html>"""
