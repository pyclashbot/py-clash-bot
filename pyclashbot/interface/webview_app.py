from __future__ import annotations

import json
import threading
import time
from typing import Any, cast

import webview  # type: ignore[import-not-found]

from pyclashbot.__main__ import (
    exit_button_event,
    handle_thread_finished,
    open_logs_folder,
    open_recordings_folder,
    save_current_settings,
    start_button_event,
    stop_button_event,
    update_layout,
)
from pyclashbot.interface.config import (
    BLUESTACKS_SETTINGS,
    GOOGLE_PLAY_SETTINGS,
    JOBS,
    MEMU_SETTINGS,
)
from pyclashbot.interface.enums import DerivedStatField, StatField, UIField
from pyclashbot.utils.caching import USER_SETTINGS_CACHE
from pyclashbot.utils.logger import Logger

HTML = r"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>py-clash-bot</title>
    <style>
      :root{
        --bg:#060910; --panel:#0a0f16; --muted:#8b95a6; --text:#f5f9ff; --line:#1c2435;
        --brand:#a78bfa; --brand2:#22d3ee; --success:#34d399; --danger:#f87171; --info:#60a5fa;
        --radius:20px; --shadow:0 25px 70px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.08);
        --shadow-lg:0 40px 100px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.1);
        --glow:0 0 60px rgba(167,139,250,.4);
        --glow-lg:0 0 100px rgba(167,139,250,.3);
      }
      *{box-sizing:border-box;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
      body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',Roboto,Inter,system-ui,sans-serif;color:var(--text);background:#060910;min-height:100vh;position:relative;overflow-x:hidden}
      body::before{content:'';position:fixed;top:0;left:0;right:0;bottom:0;background:url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(255,255,255,.02)" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grid)"/></svg>');opacity:.3;pointer-events:none;z-index:0}
      .layout{display:grid;grid-template-columns:260px 1fr;min-height:100vh;position:relative;z-index:1}
      .sidebar{padding:20px 18px;border-right:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg,rgba(167,139,250,.12),rgba(0,0,0,0));backdrop-filter:blur(30px) saturate(200%);position:sticky;top:0;height:100vh;overflow-y:auto;box-shadow:4px 0 30px rgba(0,0,0,.3)}
      .sidebar::-webkit-scrollbar{width:6px}
      .sidebar::-webkit-scrollbar-thumb{background:rgba(167,139,250,.3);border-radius:3px}
      .sidebar::-webkit-scrollbar-track{background:transparent}

      /* General Scrollbar Styles */
      ::-webkit-scrollbar{width:8px;height:8px}
      ::-webkit-scrollbar-track{background:rgba(8,12,20,.6);border-radius:4px}
      ::-webkit-scrollbar-thumb{background:linear-gradient(135deg,rgba(167,139,250,.85),rgba(34,211,238,.85));border-radius:4px;box-shadow:inset 0 1px 2px rgba(255,255,255,.25)}
      ::-webkit-scrollbar-thumb:hover{background:linear-gradient(135deg,rgba(167,139,250,1),rgba(34,211,238,1));box-shadow:0 0 10px rgba(167,139,250,.6)}

      .brand{display:flex;align-items:center;gap:10px;font-weight:900;letter-spacing:.8px;font-size:16px;margin-bottom:28px;padding:12px 14px;border-radius:12px;background:linear-gradient(135deg,rgba(167,139,250,.2),rgba(34,211,238,.15));border:1px solid rgba(167,139,250,.3);box-shadow:0 6px 24px rgba(167,139,250,.2),inset 0 1px 0 rgba(255,255,255,.1);position:relative;overflow:hidden}
      .brand::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle,rgba(255,255,255,.1),transparent);animation:shimmer 3s ease-in-out infinite}
      @keyframes shimmer{0%,100%{transform:translate(-50%,-50%) rotate(0deg)}50%{transform:translate(-50%,-50%) rotate(180deg)}}
      .brand .dot{width:12px;height:12px;border-radius:50%;background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 0 20px rgba(167,139,250,.8),inset 0 1px 2px rgba(255,255,255,.3);animation:pulse 2s ease-in-out infinite;position:relative;z-index:1}
      @keyframes pulse{0%,100%{opacity:1;transform:scale(1);box-shadow:0 0 30px rgba(167,139,250,.8)}50%{opacity:.8;transform:scale(1.15);box-shadow:0 0 50px rgba(167,139,250,1)}}
      .nav{margin-top:8px;display:grid;gap:4px}
      .nav a{padding:10px 12px;border-radius:10px;color:var(--text);text-decoration:none;display:flex;align-items:center;gap:10px;transition:all .3s cubic-bezier(0.34,1.56,0.64,1);position:relative;font-weight:600;font-size:13px;backdrop-filter:blur(10px)}
      .nav a::before{content:'';position:absolute;left:0;top:50%;transform:translateY(-50%);width:3px;height:0;background:linear-gradient(180deg,var(--brand),var(--brand2));border-radius:0 3px 3px 0;transition:height .3s ease}
      .nav a .ic{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);font-size:14px;transition:all .3s cubic-bezier(0.34,1.56,0.64,1);position:relative;z-index:1}
      .nav a:hover:not(.active){background:rgba(255,255,255,.06);transform:translateX(6px);box-shadow:0 4px 16px rgba(0,0,0,.2)}
      .nav a:hover:not(.active)::before{height:60%}
      .nav a:hover:not(.active) .ic{background:rgba(167,139,250,.2);border-color:rgba(167,139,250,.4);transform:scale(1.15) rotate(5deg);box-shadow:0 4px 12px rgba(167,139,250,.3)}
      .nav a.active{background:linear-gradient(135deg,rgba(167,139,250,.25),rgba(34,211,238,.2));border:1px solid rgba(167,139,250,.5);box-shadow:0 8px 32px rgba(167,139,250,.3),inset 0 1px 0 rgba(255,255,255,.15);transform:translateX(4px)}
      .nav a.active::before{height:80%}
      .nav a.active .ic{background:linear-gradient(135deg,var(--brand),var(--brand2));border-color:transparent;box-shadow:0 6px 20px rgba(167,139,250,.5),inset 0 1px 0 rgba(255,255,255,.2);transform:scale(1.1)}

      .main{display:grid;grid-template-rows:auto 1fr;overflow:hidden;position:relative;z-index:1}
      .top{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-bottom:1px solid rgba(255,255,255,.1);background:linear-gradient(180deg,rgba(167,139,250,.15),rgba(0,0,0,0));backdrop-filter:blur(30px) saturate(200%);position:sticky;top:0;z-index:100;box-shadow:0 6px 24px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.1)}
      .top-left{display:flex;align-items:center;gap:20px}
      .top-brand{display:flex;align-items:center;gap:10px;font-weight:900;font-size:16px;letter-spacing:.6px;position:relative}
      .top-brand .logo{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,var(--brand),var(--brand2));display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 8px 24px rgba(167,139,250,.5),inset 0 1px 2px rgba(255,255,255,.3),inset 0 -1px 2px rgba(0,0,0,.2);transition:all .4s cubic-bezier(0.34,1.56,0.64,1);position:relative;overflow:hidden}
      .top-brand .logo::before{content:'';position:absolute;inset:0;background:linear-gradient(45deg,transparent 30%,rgba(255,255,255,.3),transparent 70%);transform:translateX(-100%);transition:transform .6s}
      .top-brand .logo:hover{transform:scale(1.1) rotate(10deg);box-shadow:0 16px 50px rgba(167,139,250,.6),inset 0 2px 4px rgba(255,255,255,.4)}
      .top-brand .logo:hover::before{transform:translateX(100%)}
      .search{display:flex;align-items:center;gap:10px;background:rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:8px 14px;min-width:280px;color:var(--muted);transition:all .4s cubic-bezier(0.4,0,0.2,1);backdrop-filter:blur(15px);position:relative;overflow:hidden;font-size:12px}
      .search::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(167,139,250,.1),rgba(34,211,238,.05));opacity:0;transition:opacity .3s}
      .search:hover{border-color:rgba(167,139,250,.4);background:rgba(0,0,0,.5);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.3)}
      .search:hover::before{opacity:1}
      .search:focus-within{border-color:var(--brand);box-shadow:0 0 0 4px rgba(167,139,250,.2),var(--glow-lg);background:rgba(0,0,0,.6);transform:translateY(-2px) scale(1.02)}
      .search:focus-within::before{opacity:1}
      .search input::placeholder{color:var(--muted);opacity:.5;font-weight:500}
      .actions{display:flex;gap:12px;align-items:center}
      .top-right{display:flex;align-items:center;gap:14px;position:relative}
      .btn{padding:10px 16px;border:0;border-radius:10px;color:white;cursor:pointer;box-shadow:var(--shadow);transition:all .4s cubic-bezier(0.34,1.56,0.64,1);font-weight:700;position:relative;overflow:hidden;backdrop-filter:blur(15px);text-transform:uppercase;font-size:11px;letter-spacing:.8px}
      .btn::before{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);transition:left .6s}
      .btn:hover::before{left:100%}
      .btn::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at var(--mouse-x,50%) var(--mouse-y,50%),rgba(255,255,255,.2),transparent);opacity:0;transition:opacity .3s;pointer-events:none}
      .btn:hover::after{opacity:1}
      .btn.primary{background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 12px 32px rgba(167,139,250,.5),inset 0 2px 4px rgba(255,255,255,.25),inset 0 -2px 4px rgba(0,0,0,.2);position:relative}
      .btn.primary::before{background:linear-gradient(90deg,transparent,rgba(255,255,255,.5),transparent)}
      .btn.primary:hover:not(:disabled){transform:translateY(-4px) scale(1.05);box-shadow:0 20px 50px rgba(167,139,250,.6),inset 0 2px 4px rgba(255,255,255,.35),var(--glow);filter:brightness(1.15) saturate(1.1)}
      .btn.primary:active:not(:disabled){transform:translateY(-2px) scale(1.02)}
      .btn.danger{background:linear-gradient(135deg,var(--danger),#dc2626);box-shadow:0 12px 32px rgba(248,113,113,.5),inset 0 2px 4px rgba(255,255,255,.25),inset 0 -2px 4px rgba(0,0,0,.2)}
      .btn.danger:hover:not(:disabled){transform:translateY(-4px) scale(1.05);box-shadow:0 20px 50px rgba(248,113,113,.6),inset 0 2px 4px rgba(255,255,255,.35);filter:brightness(1.15)}
      #forceStop{background:linear-gradient(135deg,#dc2626,#991b1b)!important;opacity:.9;box-shadow:0 12px 32px rgba(220,38,38,.5),inset 0 2px 4px rgba(255,255,255,.2)}
      #forceStop:hover:not(:disabled){opacity:1!important;transform:translateY(-4px) scale(1.05);box-shadow:0 20px 50px rgba(220,38,38,.7),inset 0 2px 4px rgba(255,255,255,.3);filter:brightness(1.2)}
      .btn.ghost{background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.15);color:var(--text);backdrop-filter:blur(15px);font-weight:600}
      .btn.ghost:hover:not(:disabled){background:rgba(167,139,250,.15);border-color:rgba(167,139,250,.4);transform:translateY(-3px) scale(1.03);box-shadow:0 12px 28px rgba(0,0,0,.3),0 0 20px rgba(167,139,250,.2)}
      .btn:disabled{opacity:.4;cursor:not-allowed;filter:grayscale(.7);transform:none!important}

      .nav a{transition:all .2s ease;cursor:pointer}
      .nav a:hover:not(.active){background:rgba(255,255,255,.03);transform:translateX(2px)}
      .nav a.active{cursor:default}

      .content{padding:20px 24px;display:grid;grid-template-columns:1fr;gap:24px;overflow-y:auto;height:calc(100vh - 70px);min-height:calc(100vh - 70px);animation:fadeIn .6s cubic-bezier(0.4,0,0.2,1)}
      @keyframes fadeIn{from{opacity:0;transform:translateY(20px) scale(.98)}to{opacity:1;transform:translateY(0) scale(1)}}
      .content.dashboard{grid-template-columns:1fr}
      .content.dashboard #dashboard{display:grid;grid-template-rows:minmax(0,1fr) auto;height:100%;gap:24px;align-content:stretch}
      .content.single{grid-template-columns:1fr}
      .dashboard-main{display:flex;flex-direction:column;min-height:0;height:100%}
      .dashboard-main .bd{flex:1;display:flex;flex-direction:column;min-height:0;overflow:hidden}
      #dashboard > .panel:first-child{height:calc(100vh - 114px)!important;min-height:calc(100vh - 114px)!important}
      .panel{background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));border:1px solid rgba(255,255,255,.12);border-radius:14px;box-shadow:var(--shadow-lg);backdrop-filter:blur(30px) saturate(200%);transition:all .4s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden;animation:slideUp .5s ease backwards}
      @keyframes slideUp{from{opacity:0;transform:translateY(30px)}}
      .panel::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,rgba(167,139,250,.6),rgba(34,211,238,.6),transparent);opacity:0;transition:opacity .4s}
      .panel::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at var(--mouse-x,50%) var(--mouse-y,50%),rgba(167,139,250,.1),transparent);opacity:0;transition:opacity .3s;pointer-events:none}
      .panel:hover{transform:translateY(-2px) scale(1.005);box-shadow:var(--shadow-lg),var(--glow-lg);border-color:rgba(167,139,250,.3)}
      .panel:hover::before{opacity:1}
      .panel:hover::after{opacity:1}
      .panel .hd{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid rgba(255,255,255,.08);background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.02));font-weight:800;font-size:13px;letter-spacing:.6px;text-transform:uppercase;position:relative;z-index:1}
      .panel .hd::after{content:'';position:absolute;bottom:0;left:18px;right:18px;height:1px;background:linear-gradient(90deg,transparent,rgba(167,139,250,.4),transparent)}
      .panel .bd{padding:18px}

      .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
      .card{padding:14px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(255,255,255,.03));backdrop-filter:blur(15px);transition:all .4s cubic-bezier(0.34,1.56,0.64,1);position:relative;overflow:hidden;animation:cardSlide .5s ease backwards}
      @keyframes cardSlide{from{opacity:0;transform:translateY(20px) scale(.95)}}
      .card:nth-child(1){animation-delay:.1s}
      .card:nth-child(2){animation-delay:.2s}
      .card:nth-child(3){animation-delay:.3s}
      .card:nth-child(4){animation-delay:.4s}
      .card::before{content:'';position:absolute;top:0;left:0;width:100%;height:2px;background:linear-gradient(90deg,var(--brand),var(--brand2));opacity:0;transition:opacity .4s;box-shadow:0 0 15px rgba(167,139,250,.6)}
      .card::after{content:'';position:absolute;inset:0;background:radial-gradient(circle at var(--mouse-x,50%) var(--mouse-y,50%),rgba(167,139,250,.15),transparent);opacity:0;transition:opacity .3s;pointer-events:none}
      .card:hover{transform:translateY(-3px) scale(1.01);border-color:rgba(167,139,250,.4);box-shadow:0 12px 32px rgba(0,0,0,.4),0 0 24px rgba(167,139,250,.25),inset 0 1px 0 rgba(255,255,255,.1)}
      .card:hover::before{opacity:1}
      .card:hover::after{opacity:1}
      .card .t{font-size:9px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;opacity:.8}
      .card .v{margin-top:4px;font-size:24px;font-weight:900;background:linear-gradient(135deg,var(--text),rgba(255,255,255,.9));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-shadow:0 2px 15px rgba(167,139,250,.3);line-height:1.2}

      .gauge{display:flex;align-items:center;gap:20px;padding:16px;background:linear-gradient(135deg,rgba(167,139,250,.15),rgba(34,211,238,.08));border-radius:14px;border:1px solid rgba(167,139,250,.3);box-shadow:0 8px 28px rgba(0,0,0,.3),inset 0 1px 2px rgba(255,255,255,.1),inset 0 -1px 2px rgba(0,0,0,.2),var(--glow);position:relative;overflow:hidden;animation:gaugeAppear .6s ease backwards;animation-delay:.4s}
      @keyframes gaugeAppear{from{opacity:0;transform:scale(.8) rotate(-10deg)}}
      .gauge::before{content:'';position:absolute;inset:-50%;background:conic-gradient(from 0deg,transparent,rgba(167,139,250,.1),transparent);animation:rotate 10s linear infinite}
      @keyframes rotate{to{transform:rotate(360deg)}}
      .gauge svg{width:80px;height:80px;filter:drop-shadow(0 6px 18px rgba(167,139,250,.5));transition:all .4s cubic-bezier(0.34,1.56,0.64,1);position:relative;z-index:1}
      .gauge:hover svg{transform:scale(1.08) rotate(8deg);filter:drop-shadow(0 10px 24px rgba(167,139,250,.7))}
      .legend{display:grid;gap:8px;color:var(--muted);font-size:12px;font-weight:600;position:relative;z-index:1}
      .legend .row{display:flex;align-items:center;gap:8px;padding:6px 10px;transition:all .3s cubic-bezier(0.34,1.56,0.64,1);border-radius:8px;padding-left:10px;background:rgba(0,0,0,.2);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.05)}
      .legend .row:hover{background:rgba(255,255,255,.08);transform:translateX(4px) scale(1.01);border-color:rgba(167,139,250,.3);box-shadow:0 3px 12px rgba(0,0,0,.2)}
      .legend .dot{width:10px;height:10px;border-radius:50%;box-shadow:0 0 12px currentColor,inset 0 1px 2px rgba(255,255,255,.3);transition:all .3s ease;position:relative}
      .legend .dot::after{content:'';position:absolute;inset:-3px;border-radius:50%;border:2px solid currentColor;opacity:0;transition:opacity .3s}
      .legend .row:hover .dot{transform:scale(1.2);box-shadow:0 0 18px currentColor}
      .legend .row:hover .dot::after{opacity:.5}

      .statusline{display:flex;align-items:center;gap:8px;font-weight:600;font-size:13px}
      .status-dot{width:10px;height:10px;border-radius:50%;background:#8b949e;box-shadow:0 0 8px currentColor;transition:all .3s ease;position:relative}
      .status-dot::after{content:'';position:absolute;inset:-4px;border-radius:50%;border:2px solid currentColor;opacity:0;animation:pulse-ring 2s ease-out infinite}
      @keyframes pulse-ring{0%{transform:scale(.8);opacity:1}100%{transform:scale(1.4);opacity:0}}
      .status-dot.running{background:var(--success);animation:pulse-dot 2s ease-in-out infinite}
      @keyframes pulse-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.8;transform:scale(1.1)}}
      .status-dot.error{background:var(--danger)}
      .status-dot.info{background:var(--info)}

      #log{height:200px;overflow:auto;white-space:pre-wrap;background:linear-gradient(180deg,rgba(0,0,0,.5),rgba(0,0,0,.7));border:1px solid rgba(167,139,250,.3);border-radius:12px;padding:12px;color:#b3d9ff;font-family:'SF Mono',Monaco,'Cascadia Code','Roboto Mono',monospace;font-size:11px;line-height:1.6;box-shadow:inset 0 3px 12px rgba(0,0,0,.5),0 0 24px rgba(167,139,250,.2);position:relative;backdrop-filter:blur(10px)}
      #log::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(167,139,250,.5),transparent)}
      .tab-content{display:none}
      .tab-content.active{display:block}

      .setting-group{margin-bottom:14px;padding:12px;background:rgba(255,255,255,.02);border-radius:10px;border:1px solid rgba(255,255,255,.05);transition:all .3s ease}
      .setting-group:hover{border-color:rgba(139,92,246,.2);background:rgba(255,255,255,.03)}
      .setting-group label{display:block;margin-bottom:8px;color:var(--text);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px}
      .setting-group select,.setting-group input[type="number"]{width:100%;padding:8px 10px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.1);border-radius:8px;color:var(--text);font-size:12px;transition:all .3s ease;backdrop-filter:blur(10px);font-weight:500}
      .setting-group select:hover,.setting-group input[type="number"]:hover{border-color:rgba(167,139,250,.4);background:rgba(0,0,0,.4);transform:translateY(-1px)}
      .setting-group select:focus,.setting-group input[type="number"]:focus{outline:none;border-color:var(--brand);box-shadow:0 0 0 4px rgba(167,139,250,.15);background:rgba(0,0,0,.5)}
      .setting-group select option{background:#0f1419;color:var(--text);padding:8px}
      .setting-group input[type="range"]{width:100%;height:8px;background:rgba(255,255,255,.1);border-radius:4px;outline:none;cursor:pointer;transition:all .3s ease}
      .setting-group input[type="range"]::-webkit-slider-thumb{appearance:none;width:20px;height:20px;background:linear-gradient(135deg,var(--brand),var(--brand2));border-radius:50%;cursor:pointer;box-shadow:0 4px 12px rgba(167,139,250,.5),inset 0 1px 0 rgba(255,255,255,.3);transition:all .3s ease}
      .setting-group input[type="range"]::-webkit-slider-thumb:hover{transform:scale(1.2);box-shadow:0 6px 16px rgba(167,139,250,.7)}
      .setting-group input[type="range"]::-moz-range-thumb{width:20px;height:20px;background:linear-gradient(135deg,var(--brand),var(--brand2));border:none;border-radius:50%;cursor:pointer;box-shadow:0 4px 12px rgba(167,139,250,.5);transition:all .3s ease}
      .setting-group input[type="range"]::-moz-range-thumb:hover{transform:scale(1.2)}
      .setting-group input[type="range"]::-moz-range-track{background:rgba(255,255,255,.1);border-radius:4px;height:8px}

      .checkbox-group{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:6px;transition:all .2s ease;cursor:pointer}
      .checkbox-group:hover{background:rgba(255,255,255,.03);transform:translateX(3px)}
      .checkbox-group input[type="checkbox"]{width:16px;height:16px;cursor:pointer;accent-color:var(--brand);transition:transform .2s}
      .checkbox-group:hover input[type="checkbox"]{transform:scale(1.1)}
      .checkbox-group label{margin:0;cursor:pointer;font-weight:500;font-size:12px;user-select:none}

      .file-list{max-height:400px;overflow-y:auto;border-radius:12px;background:rgba(0,0,0,.2);padding:8px}
      .file-item{padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.05);display:flex;justify-content:space-between;align-items:center;border-radius:8px;transition:all .2s ease;margin-bottom:4px}
      .file-item:hover{background:rgba(255,255,255,.05);transform:translateX(4px);border-color:rgba(139,92,246,.2)}
      .file-item:last-child{border-bottom:none;margin-bottom:0}

      .sidebar, .content, #log{scrollbar-width:none;-ms-overflow-style:none}
      .sidebar::-webkit-scrollbar,
      .content::-webkit-scrollbar,
      #log::-webkit-scrollbar{width:0;height:0}
      .sidebar::-webkit-scrollbar-track,
      .content::-webkit-scrollbar-track,
      #log::-webkit-scrollbar-track{background:transparent}
      .sidebar::-webkit-scrollbar-thumb,
      .content::-webkit-scrollbar-thumb,
      #log::-webkit-scrollbar-thumb{background:transparent;border-radius:0}
    </style>
  </head>
  <body>
    <div class="layout">
      <aside class="sidebar">
        <div class="brand"><span class="dot"></span> py-clash-bot</div>
        <div class="nav">
          <a class="nav-link active" data-tab="dashboard"><span class="ic">🏠</span> Dashboard</a>
          <a class="nav-link" data-tab="settings"><span class="ic">⚙️</span> Settings</a>
          <a class="nav-link" data-tab="experiments"><span class="ic">🧪</span> Experiments</a>
        </div>
      </aside>
      <section class="main">
        <div class="top">
          <div class="top-left">
            <div class="search">
              <span>🔎</span>
              <input type="text" placeholder="Quick search…" style="border:none;background:transparent;outline:none;color:var(--text);width:100%;font-size:13px" />
            </div>
          </div>
          <div class="top-right">
            <div class="actions">
              <button id="start" class="btn primary">▶ Start</button>
              <button id="stop" class="btn danger" disabled>⏹ Stop</button>
              <button id="forceStop" class="btn danger" disabled style="opacity:.7;background:linear-gradient(45deg,#ff4444,#cc0000)" title="Force Stop (Kill immediately)">⚠ Force Stop</button>
            </div>
          </div>
        </div>

        <div class="content">
          <div id="dashboard" class="tab-content active">
            <div class="panel dashboard-main">
              <div class="hd">
                <div class="statusline"><span id="dot" class="status-dot"></span><div id="status">Idle</div></div>
                <div style="color:var(--muted);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;display:flex;align-items:center;gap:6px">
                  <span style="width:6px;height:6px;border-radius:50%;background:var(--success);animation:pulse-badge 2s ease-in-out infinite"></span>
                  Real-time
                </div>
              </div>
              <div class="bd">
                <div class="stats">
                  <div class="card"><div class="t">Wins</div><div id="wins" class="v">0</div></div>
                  <div class="card"><div class="t">Losses</div><div id="losses" class="v">0</div></div>
                  <div class="card"><div class="t">Win Rate</div><div id="winrate" class="v">0%</div></div>
                  <div class="card"><div class="t">Runtime</div><div id="runtime" class="v">0:00</div></div>
                </div>
                <div style="height:12px"></div>
                <div class="gauge">
                  <div style="position:relative">
                    <svg viewBox="0 0 36 36" style="filter:drop-shadow(0 3px 12px rgba(139,92,246,.4))">
                      <defs>
                        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stop-color="#8b5cf6"/>
                          <stop offset="100%" stop-color="#06b6d4"/>
                        </linearGradient>
                        <filter id="glow">
                          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                          <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                          </feMerge>
                        </filter>
                      </defs>
                      <path d="M18 2 a 16 16 0 0 1 0 32 a 16 16 0 0 1 0 -32" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="4"/>
                      <path id="arc" d="M18 2 a 16 16 0 0 1 0 32 a 16 16 0 0 1 0 -32" fill="none" stroke="url(#grad)" stroke-linecap="round" stroke-width="4" stroke-dasharray="0 100" filter="url(#glow)"/>
                      <text id="arcLabel" x="18" y="20" text-anchor="middle" alignment-baseline="middle" fill="#f0f4f8" font-size="7" font-weight="800">0%</text>
                    </svg>
                  </div>
                  <div class="legend">
                    <div class="row"><span class="dot" style="background:var(--success);box-shadow:0 0 10px rgba(16,185,129,.6)"></span><span style="font-weight:600">Wins</span></div>
                    <div class="row"><span class="dot" style="background:var(--danger);box-shadow:0 0 10px rgba(239,68,68,.6)"></span><span style="font-weight:600">Losses</span></div>
                    <div class="row"><span class="dot" style="background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 0 10px rgba(139,92,246,.6)"></span><span style="font-weight:600">Win Rate</span></div>
                  </div>
                </div>
                <div style="height:12px"></div>
                <div id="log" style="flex:1;min-height:0"></div>
              </div>
            </div>

            <div class="panel" style="margin-top:24px">
              <div class="hd"><div>💡 Quick Tips</div></div>
              <div class="bd" style="color:var(--muted);font-size:14px;line-height:1.8">
                <div style="padding:12px;background:rgba(139,92,246,.08);border-left:3px solid var(--brand);border-radius:6px;margin-bottom:10px">
                  <strong style="color:var(--text)">Start/Stop:</strong> Use Start to begin automation and Stop for graceful shutdown. Force Stop kills immediately.
                </div>
                <div style="padding:12px;background:rgba(6,182,212,.08);border-left:3px solid var(--brand2);border-radius:6px;margin-bottom:10px">
                  <strong style="color:var(--text)">Troubleshooting:</strong> Open Logs for detailed information and error messages.
                </div>
                <div style="padding:12px;background:rgba(16,185,129,.08);border-left:3px solid var(--success);border-radius:6px">
                  <strong style="color:var(--text)">Best Practice:</strong> Keep emulator settings configured as recommended for optimal performance.
                </div>
              </div>
            </div>
          </div>

          <div id="settings" class="tab-content">
            <div class="panel">
              <div class="hd"><div>⚙️ Bot Settings</div></div>
              <div class="bd">
                <div class="setting-group">
                  <label>Emulator Type</label>
                  <select id="emulatorType">
                    <option value="MEmu">MEmu</option>
                    <option value="Google Play">Google Play</option>
                    <option value="BlueStacks 5">BlueStacks 5</option>
                  </select>
                </div>
                <div class="setting-group">
                  <label>Render Mode</label>
                  <select id="renderMode">
                    <option value="DirectX">DirectX</option>
                    <option value="OpenGL">OpenGL</option>
                    <option value="Vulkan">Vulkan</option>
                  </select>
                </div>
                <div class="setting-group">
                  <label>Jobs</label>
                  <div class="checkbox-group">
                    <input type="checkbox" id="job1v1" checked>
                    <label for="job1v1">Classic 1v1 battles</label>
                  </div>
                  <div class="checkbox-group">
                    <input type="checkbox" id="job2v2">
                    <label for="job2v2">Classic 2v2 battles</label>
                  </div>
                  <div class="checkbox-group">
                    <input type="checkbox" id="jobTrophyRoad" checked>
                    <label for="jobTrophyRoad">Trophy Road battles</label>
                  </div>
                  <div class="checkbox-group">
                    <input type="checkbox" id="jobRandomDecks">
                    <label for="jobRandomDecks">Random decks</label>
                  </div>
                  <div class="checkbox-group">
                    <input type="checkbox" id="jobCardMastery">
                    <label for="jobCardMastery">Card Masteries</label>
                  </div>
                  <div class="checkbox-group">
                    <input type="checkbox" id="jobUpgrade">
                    <label for="jobUpgrade">Upgrade Cards</label>
                  </div>
                </div>
                <div class="setting-group">
                  <label>Deck Selection</label>
                  <input type="number" id="deckNumber" value="2" min="1" max="5">
                </div>
                <div class="setting-group">
                  <div class="checkbox-group">
                    <input type="checkbox" id="recordFights">
                    <label for="recordFights">Record fights</label>
                  </div>
                </div>
                <div class="setting-group">
                  <label>Advanced Settings</label>
                  <div class="checkbox-group">
                    <input type="checkbox" id="autoRestart">
                    <label for="autoRestart">Auto-restart on failure</label>
                  </div>
                  <div class="checkbox-group">
                    <input type="checkbox" id="saveScreenshots">
                    <label for="saveScreenshots">Save screenshots for debugging</label>
                  </div>
                  <div class="checkbox-group">
                    <input type="checkbox" id="verboseLogging">
                    <label for="verboseLogging">Verbose logging</label>
                  </div>
                  <div style="margin-top:16px">
                    <label style="display:block;margin-bottom:8px;font-size:12px;color:var(--muted)">UI Mode</label>
                    <select id="uiMode" style="width:100%;padding:8px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;color:var(--text);font-size:13px">
                      <option value="web">Web UI (Modern)</option>
                      <option value="regular">Regular UI (Classic)</option>
                    </select>
                    <div style="font-size:11px;color:var(--muted);margin-top:6px">Restart required to apply changes</div>
                  </div>
                  <div style="margin-top:16px">
                    <label style="display:block;margin-bottom:8px;font-size:12px;color:var(--muted)">Battle Timeout (minutes)</label>
                    <input type="number" id="battleTimeout" value="4" min="2" max="10" step="1" style="width:100%;padding:8px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;color:var(--text);font-size:13px">
                  </div>
                  <div style="margin-top:16px">
                    <label style="display:block;margin-bottom:8px;font-size:12px;color:var(--muted)">Max Restarts</label>
                    <input type="number" id="maxRestarts" value="5" min="1" max="20" step="1" style="width:100%;padding:8px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;color:var(--text);font-size:13px">
                  </div>
                </div>
                <div class="setting-group">
                  <label>Performance</label>
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px">
                    <div>
                      <label style="display:block;margin-bottom:8px;font-size:12px;color:var(--muted)">Screenshot Interval (ms)</label>
                      <input type="number" id="screenshotInterval" value="100" min="50" max="1000" step="50" style="width:100%">
                    </div>
                    <div>
                      <label style="display:block;margin-bottom:8px;font-size:12px;color:var(--muted)">Action Delay (ms)</label>
                      <input type="number" id="actionDelay" value="100" min="0" max="500" step="10" style="width:100%">
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div id="experiments" class="tab-content">
            <div class="panel">
              <div class="hd"><div>🧪 Experiments</div></div>
              <div class="bd" style="color:var(--muted);font-size:14px;line-height:1.8">
                <div style="padding:16px;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);border-radius:12px;margin-bottom:20px">
                  <strong style="color:var(--danger);display:flex;align-items:center;gap:8px;margin-bottom:8px">
                    ⚠️ Warning
                  </strong>
                  <p style="margin:0;color:var(--text)">Experimental features may be unstable. Use with caution.</p>
                </div>
                <div style="margin-top:20px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
                  <div class="checkbox-group" style="padding:14px;background:rgba(255,255,255,.02);border-radius:10px;margin-bottom:12px">
                    <input type="checkbox" id="expRandomPlays">
                    <div style="flex:1">
                      <label for="expRandomPlays" style="font-weight:600;color:var(--text);display:block;margin-bottom:4px">Random Plays</label>
                      <div style="font-size:12px;color:var(--muted)">Adds random delays and variations to make automation less predictable</div>
                    </div>
                  </div>
                  <div class="checkbox-group" style="padding:14px;background:rgba(255,255,255,.02);border-radius:10px;margin-bottom:12px">
                    <input type="checkbox" id="expSkipWinTrack">
                    <div style="flex:1">
                      <label for="expSkipWinTrack" style="font-weight:600;color:var(--text);display:block;margin-bottom:4px">Skip Win/Loss Check</label>
                      <div style="font-size:12px;color:var(--muted)">Skips win/loss detection to speed up battles (may reduce accuracy)</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <script>
      const statusEl = document.getElementById('status');
      const dotEl = document.getElementById('dot');
      const logEl = document.getElementById('log');
      const startBtn = document.getElementById('start');
      const stopBtn = document.getElementById('stop');
      const arc = document.getElementById('arc');
      const arcLabel = document.getElementById('arcLabel');

      function setGauge(percent){
        const p = Math.max(0, Math.min(100, Number(percent)||0));
        arc.setAttribute('stroke-dasharray', `${p} ${100-p}`);
        arcLabel.textContent = `${p.toFixed(0)}%`;
      }

      const forceStopBtn = document.getElementById('forceStop');
      let isRunning = false;
      let lastStatusMessage = '';

      function pushNotification(message, level = 'info') {
        // Notifications disabled
      }

      function setState(running) {
        const isActive = !!running;
        startBtn.disabled = isActive;
        stopBtn.disabled = !isActive;
        forceStopBtn.disabled = !isActive;
        if (isActive !== isRunning) {
          pushNotification(isActive ? 'Bot started running.' : 'Bot stopped.', isActive ? 'success' : 'info');
          isRunning = isActive;
        }
      }

      function setStatus(text, kind) {
        statusEl.textContent = text || '';
        dotEl.className = 'status-dot ' + (kind || '');
        if (text && text !== lastStatusMessage) {
          const lower = text.toLowerCase();
          if (kind === 'error' || lower.includes('error') || lower.includes('failed')) {
            pushNotification(text, 'error');
          } else if (lower.includes('force stopped') || lower.includes('completed') || lower.includes('success')) {
            pushNotification(text, 'success');
          }
          lastStatusMessage = text;
        }
      }

      function appendLog(text) {
        if (!text) return;
        logEl.textContent = text;
        logEl.scrollTop = logEl.scrollHeight;
        // infer a winrate percentage if the log contains Winrate: XX%
        const m = /win\s*rate\s*[:=]\s*(\d+\.?\d*)%/i.exec(text);
        if(m){ setGauge(parseFloat(m[1])); }
      }

      // Tab switching
      function switchTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        const tab = document.getElementById(tabName);
        const link = document.querySelector(`[data-tab="${tabName}"]`);
        const content = document.querySelector('.content');
        if (tab) tab.classList.add('active');
        if (link) link.classList.add('active');
        // Layout adjustments
        if (content) {
          content.classList.remove('dashboard', 'single');
          if (tabName === 'dashboard') {
            content.classList.add('dashboard');
          } else {
            content.classList.add('single');
          }
        }
      }

      // Settings form handlers
      function saveSettings() {
        const emulator = document.getElementById('emulatorType').value;
        const render = document.getElementById('renderMode').value;
        const deckNum = parseInt(document.getElementById('deckNumber').value) || 2;
        const recordFights = document.getElementById('recordFights').checked;
        const jobs = {
          classic_1v1: document.getElementById('job1v1').checked,
          classic_2v2: document.getElementById('job2v2').checked,
          trophy_road: document.getElementById('jobTrophyRoad').checked,
          random_decks: document.getElementById('jobRandomDecks').checked,
          card_mastery: document.getElementById('jobCardMastery').checked,
          upgrade: document.getElementById('jobUpgrade').checked,
        };
        const advanced = {
          autoRestart: document.getElementById('autoRestart')?.checked || false,
          saveScreenshots: document.getElementById('saveScreenshots')?.checked || false,
          verboseLogging: document.getElementById('verboseLogging')?.checked || false,
          screenshotInterval: parseInt(document.getElementById('screenshotInterval')?.value || 100),
          actionDelay: parseInt(document.getElementById('actionDelay')?.value || 100),
          battleTimeout: parseInt(document.getElementById('battleTimeout')?.value || 4),
          maxRestarts: parseInt(document.getElementById('maxRestarts')?.value || 5),
          uiMode: document.getElementById('uiMode')?.value || 'web',
        };
        const experiments = {
          randomPlays: document.getElementById('expRandomPlays')?.checked || false,
          skipWinTrack: document.getElementById('expSkipWinTrack')?.checked || false,
        };
        window.pywebview.api.save_settings({emulator, render, deckNum, recordFights, jobs, advanced, experiments});
      }

      // Auto-save settings when changed
      ['emulatorType', 'renderMode', 'deckNumber', 'recordFights',
       'job1v1', 'job2v2', 'jobTrophyRoad', 'jobRandomDecks', 'jobCardMastery', 'jobUpgrade',
       'autoRestart', 'saveScreenshots', 'verboseLogging', 'screenshotInterval', 'actionDelay',
       'battleTimeout', 'maxRestarts', 'uiMode', 'expRandomPlays', 'expSkipWinTrack'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
          el.addEventListener('change', saveSettings);
        }
      });

      document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const tab = link.getAttribute('data-tab');
          if (tab) switchTab(tab);
        });
      });

      startBtn.addEventListener('click', () => window.pywebview.api.start());
      stopBtn.addEventListener('click', () => window.pywebview.api.stop());
      forceStopBtn.addEventListener('click', () => {
        if (confirm('Force stop will immediately kill the bot process. Continue?')) {
          window.pywebview.api.force_stop();
        }
      });
      document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') window.pywebview.api.start();
        if (e.ctrlKey && (e.key === 'q' || e.key === 'Q')) window.pywebview.api.stop();
      });

      window.setState = setState;
      window.setStatus = setStatus;
      window.appendLog = appendLog;
      window.pushNotification = pushNotification;
      renderNotifications();
      updateBadge();
      setGauge(0);
    </script>
  </body>
  </html>
"""


class StopButtonShim:
    def __init__(self, app: WebViewApp) -> None:
        self.app = app

    def configure(self, **kwargs: Any) -> None:
        state = kwargs.get("state")
        if state is not None:
            self.app._set_running(state != "disabled")


class NotebookShim:
    def select(self, _tab: object) -> None:
        return


class WebViewUIShim:
    def __init__(self, app: WebViewApp) -> None:
        self.app = app
        self.notebook = NotebookShim()
        self.stats_tab = object()
        self.stop_btn = StopButtonShim(app)

    def set_running_state(self, running: bool) -> None:
        self.app._set_running(running)

    def show_action_button(self, _text: str, _callback) -> None:
        return

    def hide_action_button(self) -> None:
        return

    def update_stats(self, stats: dict[str, object] | None) -> None:
        if not stats:
            return
        wins_raw = stats.get(StatField.WINS.value, 0)
        losses_raw = stats.get(StatField.LOSSES.value, 0)
        try:
            wins = int(cast("Any", wins_raw) or 0)
        except Exception:
            wins = 0
        try:
            losses = int(cast("Any", losses_raw) or 0)
        except Exception:
            losses = 0
        winrate_raw = stats.get(DerivedStatField.WINRATE.value)
        try:
            if isinstance(winrate_raw, str) and winrate_raw.endswith("%"):
                winrate = float(winrate_raw[:-1])
            else:
                winrate = float(cast("Any", winrate_raw)) if winrate_raw is not None else 0.0
        except Exception:
            total = wins + losses
            winrate = (wins / total * 100.0) if total > 0 else 0.0
        runtime_raw = stats.get("time_since_start", "")
        runtime_display = "0:00"
        if runtime_raw:
            try:
                runtime_str = str(runtime_raw)
                if ":" in runtime_str:
                    runtime_display = runtime_str
                else:
                    total_seconds = int(float(runtime_str.split()[0]) if " " in runtime_str else runtime_str)
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    runtime_display = f"{minutes}:{seconds:02d}"
            except Exception:
                runtime_display = str(runtime_raw)[:10]
        script = (
            f"document.getElementById('wins').textContent='{wins}';"
            f"document.getElementById('losses').textContent='{losses}';"
            f"document.getElementById('winrate').textContent='{winrate:.0f}%';"
            f"document.getElementById('runtime').textContent='{runtime_display}';"
            f"setGauge({winrate:.2f});"
        )
        self.app._eval(script)

    def set_status(self, text: str) -> None:
        self.app._set_status(text)

    def append_log(self, message: str) -> None:
        self.app._append_log(message)


def build_default_values() -> dict[str, object]:
    values: dict[str, object] = {}
    for job in JOBS:
        values[job.key.value] = bool(job.default)

    # Defaults matching tkinter UI
    values[UIField.DECK_NUMBER_SELECTION.value] = 2
    values[UIField.MAX_DECK_SELECTION.value] = 2
    values[UIField.CYCLE_DECKS_USER_TOGGLE.value] = False
    values[UIField.RECORD_FIGHTS_TOGGLE.value] = False

    # Emulator selection defaults: MEmu + DirectX
    values[UIField.MEMU_EMULATOR_TOGGLE.value] = True
    values[UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value] = False
    values[UIField.BLUESTACKS_EMULATOR_TOGGLE.value] = False

    # Render modes
    # MEmu
    for cfg in MEMU_SETTINGS:
        values[cfg.key.value] = bool(cfg.default)
    # BlueStacks
    for cfg in BLUESTACKS_SETTINGS:
        values[cfg.key.value] = bool(cfg.default)

    # Google Play comboboxes - choose first option
    for cfg in GOOGLE_PLAY_SETTINGS:
        values[cfg.key.value] = str(cfg.values[0]) if cfg.values else ""

    values[UIField.THEME_NAME.value] = "darkly"
    return values


class WebViewApp:
    def __init__(self) -> None:
        self.window: webview.Window | None = None
        self.ui_shim = WebViewUIShim(self)
        self.logger = Logger(timed=False)
        self.thread = None
        self._polling = False
        self._lock = threading.Lock()
        self._settings: dict[str, object] = {}
        # Load saved settings or use defaults
        self._settings = self.load_settings()

    # JS calls into this API
    class API:
        def __init__(self, app: WebViewApp) -> None:
            self.app = app

        def start(self) -> None:
            self.app.start()

        def stop(self) -> None:
            self.app.stop()

        def force_stop(self) -> None:
            """Force stop - kill thread immediately."""
            self.app.force_stop()

        def open_recordings(self) -> None:
            open_recordings_folder()

        def open_logs(self) -> None:
            open_logs_folder()

        def get_settings(self) -> dict[str, Any]:
            """Get current settings from the UI."""
            return self.app.get_settings()

        def save_settings(self, settings: dict[str, Any]) -> None:
            """Save settings from the UI."""
            self.app.save_settings(settings)

        def load_settings(self) -> dict[str, Any]:
            """Load saved settings."""
            return self.app.load_settings()

    def _eval(self, script: str) -> None:
        if self.window is not None:
            try:
                self.window.evaluate_js(script)
            except Exception:
                pass

    def _set_running(self, running: bool) -> None:
        self._eval(f"window.setState({json.dumps(bool(running))})")

    def _push_notification(self, message: str, level: str = "info") -> None:
        self._eval(f"window.pushNotification({json.dumps(message)}, {json.dumps(level)})")

    def _set_status(self, text: str) -> None:
        kind = "info"
        low = (text or "").lower()
        if any(k in low for k in ["error", "failed", "fail"]):
            kind = "error"
        elif any(k in low for k in ["running", "started"]):
            kind = "running"
        elif any(k in low for k in ["idle", "stopped"]):
            kind = ""
        self._eval(f"window.setStatus({json.dumps(text)}, {json.dumps(kind)})")

    def _append_log(self, text: str) -> None:
        self._eval(f"window.appendLog({json.dumps(text)})")

    def get_settings(self) -> dict[str, object]:
        """Get current settings from UI form."""
        script = """
        (function() {
            const emulator = document.getElementById('emulatorType').value;
            const render = document.getElementById('renderMode').value;
            const deckNum = parseInt(document.getElementById('deckNumber').value) || 2;
            const recordFights = document.getElementById('recordFights').checked;
            const jobs = {
                classic_1v1: document.getElementById('job1v1').checked,
                classic_2v2: document.getElementById('job2v2').checked,
                trophy_road: document.getElementById('jobTrophyRoad').checked,
                random_decks: document.getElementById('jobRandomDecks').checked,
                card_mastery: document.getElementById('jobCardMastery').checked,
                upgrade: document.getElementById('jobUpgrade').checked,
            };
            const advanced = {
                autoRestart: document.getElementById('autoRestart')?.checked || false,
                saveScreenshots: document.getElementById('saveScreenshots')?.checked || false,
                verboseLogging: document.getElementById('verboseLogging')?.checked || false,
                screenshotInterval: parseInt(document.getElementById('screenshotInterval')?.value || 100),
                actionDelay: parseInt(document.getElementById('actionDelay')?.value || 100),
                battleTimeout: parseInt(document.getElementById('battleTimeout')?.value || 4),
                maxRestarts: parseInt(document.getElementById('maxRestarts')?.value || 5),
                uiMode: document.getElementById('uiMode')?.value || 'web',
            };
            const experiments = {
                randomPlays: document.getElementById('expRandomPlays')?.checked || false,
                skipWinTrack: document.getElementById('expSkipWinTrack')?.checked || false,
            };
            return JSON.stringify({emulator, render, deckNum, recordFights, jobs, advanced, experiments});
        })()
        """
        try:
            if self.window is not None:
                result = self.window.evaluate_js(script)
                if result:
                    data = json.loads(result)
                    return self._ui_to_values(data)
        except Exception:
            pass
        return self._settings.copy()

    def _ui_to_values(self, ui_data: dict[str, Any]) -> dict[str, object]:
        """Convert UI form data to internal values format."""
        values: dict[str, object] = {}

        # Jobs
        jobs = ui_data.get("jobs", {})
        values[UIField.CLASSIC_1V1_USER_TOGGLE.value] = bool(jobs.get("classic_1v1", False))
        values[UIField.CLASSIC_2V2_USER_TOGGLE.value] = bool(jobs.get("classic_2v2", False))
        values[UIField.TROPHY_ROAD_USER_TOGGLE.value] = bool(jobs.get("trophy_road", False))
        values[UIField.RANDOM_DECKS_USER_TOGGLE.value] = bool(jobs.get("random_decks", False))
        values[UIField.CARD_MASTERY_USER_TOGGLE.value] = bool(jobs.get("card_mastery", False))
        values[UIField.CARD_UPGRADE_USER_TOGGLE.value] = bool(jobs.get("upgrade", False))

        # Deck selection
        values[UIField.DECK_NUMBER_SELECTION.value] = int(ui_data.get("deckNum", 2))
        values[UIField.MAX_DECK_SELECTION.value] = 2
        values[UIField.CYCLE_DECKS_USER_TOGGLE.value] = False
        values[UIField.RANDOM_PLAYS_USER_TOGGLE.value] = False
        values[UIField.DISABLE_WIN_TRACK_TOGGLE.value] = False

        # Record fights
        values[UIField.RECORD_FIGHTS_TOGGLE.value] = bool(ui_data.get("recordFights", False))

        # Advanced settings (stored for future use)
        advanced = ui_data.get("advanced", {})
        values["auto_restart"] = bool(advanced.get("autoRestart", False))
        values["save_screenshots"] = bool(advanced.get("saveScreenshots", False))
        values["verbose_logging"] = bool(advanced.get("verboseLogging", False))
        values["screenshot_interval"] = int(advanced.get("screenshotInterval", 100))
        values["action_delay"] = int(advanced.get("actionDelay", 100))
        values["battle_timeout"] = int(advanced.get("battleTimeout", 4))
        values["max_restarts"] = int(advanced.get("maxRestarts", 5))
        values["ui_mode"] = str(advanced.get("uiMode", "web"))

        # Experimental settings (stored for future use)
        experiments = ui_data.get("experiments", {})
        values[UIField.RANDOM_PLAYS_USER_TOGGLE.value] = bool(experiments.get("randomPlays", False))
        values[UIField.DISABLE_WIN_TRACK_TOGGLE.value] = bool(experiments.get("skipWinTrack", False))

        # Emulator selection
        emulator = ui_data.get("emulator", "MEmu")
        values[UIField.MEMU_EMULATOR_TOGGLE.value] = emulator == "MEmu"
        values[UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value] = emulator == "Google Play"
        values[UIField.BLUESTACKS_EMULATOR_TOGGLE.value] = emulator == "BlueStacks 5"

        # Render mode
        render = ui_data.get("render", "DirectX")
        if emulator == "MEmu":
            values[UIField.DIRECTX_TOGGLE.value] = render == "DirectX"
            values[UIField.OPENGL_TOGGLE.value] = render == "OpenGL"
        elif emulator == "BlueStacks 5":
            values[UIField.BS_RENDERER_DX.value] = render == "DirectX"
            values[UIField.BS_RENDERER_GL.value] = render == "OpenGL"
            values[UIField.BS_RENDERER_VK.value] = render == "Vulkan"

        # Defaults for other fields
        for job in JOBS:
            if job.key.value not in values:
                values[job.key.value] = bool(job.default)

        for cfg in MEMU_SETTINGS:
            if cfg.key.value not in values:
                values[cfg.key.value] = bool(cfg.default)

        for cfg in BLUESTACKS_SETTINGS:
            if cfg.key.value not in values:
                values[cfg.key.value] = bool(cfg.default)

        for cfg in GOOGLE_PLAY_SETTINGS:
            if cfg.key.value not in values:
                values[cfg.key.value] = str(cfg.values[0]) if cfg.values else ""

        values[UIField.THEME_NAME.value] = "darkly"
        return values

    def save_settings(self, settings: dict[str, Any]) -> None:
        """Save settings and update UI."""
        self._settings = self._ui_to_values(settings)
        save_current_settings(self._settings)
        self._update_ui_from_settings()

    def load_settings(self) -> dict[str, object]:
        """Load settings from cache or return defaults."""
        if USER_SETTINGS_CACHE.exists():
            try:
                cached = USER_SETTINGS_CACHE.load_data()
                if cached:
                    return cached
            except Exception:
                pass
        return build_default_values()

    def _update_ui_from_settings(self) -> None:
        """Update UI form fields from current settings."""
        settings = self._settings

        # Emulator
        if settings.get(UIField.GOOGLE_PLAY_EMULATOR_TOGGLE.value):
            emulator = "Google Play"
        elif settings.get(UIField.BLUESTACKS_EMULATOR_TOGGLE.value):
            emulator = "BlueStacks 5"
        else:
            emulator = "MEmu"

        # Render mode
        render = "DirectX"
        if emulator == "MEmu":
            if settings.get(UIField.OPENGL_TOGGLE.value):
                render = "OpenGL"
        elif emulator == "BlueStacks 5":
            if settings.get(UIField.BS_RENDERER_VK.value):
                render = "Vulkan"
            elif settings.get(UIField.BS_RENDERER_GL.value):
                render = "OpenGL"

        script = f"""
        document.getElementById('emulatorType').value = {json.dumps(emulator)};
        document.getElementById('renderMode').value = {json.dumps(render)};
        document.getElementById('deckNumber').value = {json.dumps(settings.get(UIField.DECK_NUMBER_SELECTION.value, 2))};
        document.getElementById('recordFights').checked = {json.dumps(bool(settings.get(UIField.RECORD_FIGHTS_TOGGLE.value, False)))};
        document.getElementById('job1v1').checked = {json.dumps(bool(settings.get(UIField.CLASSIC_1V1_USER_TOGGLE.value, False)))};
        document.getElementById('job2v2').checked = {json.dumps(bool(settings.get(UIField.CLASSIC_2V2_USER_TOGGLE.value, False)))};
        document.getElementById('jobTrophyRoad').checked = {json.dumps(bool(settings.get(UIField.TROPHY_ROAD_USER_TOGGLE.value, False)))};
        document.getElementById('jobRandomDecks').checked = {json.dumps(bool(settings.get(UIField.RANDOM_DECKS_USER_TOGGLE.value, False)))};
        document.getElementById('jobCardMastery').checked = {json.dumps(bool(settings.get(UIField.CARD_MASTERY_USER_TOGGLE.value, False)))};
        document.getElementById('jobUpgrade').checked = {json.dumps(bool(settings.get(UIField.CARD_UPGRADE_USER_TOGGLE.value, False)))};
        if (document.getElementById('autoRestart')) document.getElementById('autoRestart').checked = {json.dumps(bool(settings.get("auto_restart", False)))};
        if (document.getElementById('saveScreenshots')) document.getElementById('saveScreenshots').checked = {json.dumps(bool(settings.get("save_screenshots", False)))};
        if (document.getElementById('verboseLogging')) document.getElementById('verboseLogging').checked = {json.dumps(bool(settings.get("verbose_logging", False)))};
        if (document.getElementById('screenshotInterval')) document.getElementById('screenshotInterval').value = {json.dumps(settings.get("screenshot_interval", 100))};
        if (document.getElementById('actionDelay')) document.getElementById('actionDelay').value = {json.dumps(settings.get("action_delay", 100))};
        if (document.getElementById('battleTimeout')) document.getElementById('battleTimeout').value = {json.dumps(settings.get("battle_timeout", 4))};
        if (document.getElementById('maxRestarts')) document.getElementById('maxRestarts').value = {json.dumps(settings.get("max_restarts", 5))};
        if (document.getElementById('uiMode')) document.getElementById('uiMode').value = {json.dumps(settings.get("ui_mode", "web"))};
        if (document.getElementById('expRandomPlays')) document.getElementById('expRandomPlays').checked = {json.dumps(bool(settings.get(UIField.RANDOM_PLAYS_USER_TOGGLE.value, False)))};
        if (document.getElementById('expSkipWinTrack')) document.getElementById('expSkipWinTrack').checked = {json.dumps(bool(settings.get(UIField.DISABLE_WIN_TRACK_TOGGLE.value, False)))};
        """
        self._eval(script)

    def start(self) -> None:
        with self._lock:
            if self.thread is not None and getattr(self.thread, "is_alive", lambda: False)():
                return
            # Get current settings from UI
            values = self.get_settings()
            new_logger = Logger(timed=True)
            thread = start_button_event(new_logger, cast("Any", self.ui_shim), values)
            if thread is None:
                return
            self.logger = new_logger
            self.thread = thread
            if not self._polling:
                self._polling = True
                threading.Thread(target=self._poll_loop, daemon=True).start()

    def stop(self) -> None:
        with self._lock:
            if self.thread is not None:
                stop_button_event(self.logger, cast("Any", self.ui_shim), self.thread)

    def force_stop(self) -> None:
        """Force stop - kill thread immediately without graceful shutdown."""
        with self._lock:
            if self.thread is not None:
                # Kill the thread immediately
                try:
                    if hasattr(self.thread, "shutdown"):
                        self.thread.shutdown(kill=True)
                    # Force set running state to false
                    self._set_running(False)
                    self._set_status("Force stopped")
                    self._append_log("Bot force stopped - process killed immediately")
                    self.thread = None
                    self._polling = False
                except Exception as e:
                    self._append_log(f"Error force stopping: {e}")
                    self._set_running(False)
                    self.thread = None
                    self._polling = False

    def _poll_loop(self) -> None:
        while True:
            with self._lock:
                thread = self.thread
                logger = self.logger
            update_layout(cast("Any", self.ui_shim), logger)
            with self._lock:
                self.thread, self.logger = handle_thread_finished(cast("Any", self.ui_shim), thread, logger)
                alive = self.thread is not None and self.thread.is_alive()
                if not alive:
                    self._polling = False
                    break
            time.sleep(0.1)

    def run(self) -> None:
        api = WebViewApp.API(self)
        self.window = webview.create_window(
            "py-clash-bot",
            html=HTML,
            width=1000,
            height=600,
            resizable=False,
            js_api=api,
        )

        # Wait a bit for window to be ready, then load settings
        def load_settings_after_init():
            time.sleep(0.3)
            self._update_ui_from_settings()

        threading.Thread(target=load_settings_after_init, daemon=True).start()
        try:
            webview.start(debug=False, http_server=False)
        finally:
            exit_button_event(self.thread)


def run_webview() -> None:
    """Run the main webview application."""
    app = WebViewApp()
    app.run()
