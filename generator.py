#!/usr/bin/env python3
"""
Unique Web Art Page Generator
Har baar alag canvas animation with different physics, logic, colors.
"""

import os
import random

OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

# ─── COLOR HELPERS ────────────────────────────────────────────────

def hex_to_rgb_tuple(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def rgb_str(h):
    r, g, b = hex_to_rgb_tuple(h)
    return f"{r},{g},{b}"

# ─── COLOR PALETTES ──────────────────────────────────────────────
# Each palette: name, bg1, bg2, accent1, accent2, accent3, bg1_rgb, bg2_rgb, a1_rgb, a2_rgb, a3_rgb
def make_palette(name, bg1, bg2, a1, a2, a3):
    return (name, bg1, bg2, a1, a2, a3,
            rgb_str(bg1), rgb_str(bg2), rgb_str(a1), rgb_str(a2), rgb_str(a3))

PALETTES = [
    make_palette("Neon Dream",  "#0a0015", "#15002a", "#ff3366", "#00e5ff", "#ffcc00"),
    make_palette("Forest Myst", "#00120a", "#0a1a0a", "#00ff88", "#7cff5e", "#ffd700"),
    make_palette("Ocean Deep",  "#000d1a", "#001a33", "#00b4ff", "#00ffe1", "#ff6b9d"),
    make_palette("Fire Realm",  "#1a0500", "#2a0a00", "#ff4400", "#ff8800", "#ffdd00"),
    make_palette("Galaxy Void", "#000011", "#110022", "#c084fc", "#ec4899", "#fbbf24"),
    make_palette("Matrix Code", "#000a00", "#001a00", "#00ff41", "#00cc33", "#ffffff"),
    make_palette("Sunset Vibe", "#1a0020", "#2a1020", "#ff6b9d", "#ffa94d", "#ffd93d"),
    make_palette("Ice Crystal", "#000a14", "#0a1a2a", "#80d0ff", "#c8f0ff", "#ff77e9"),
    make_palette("Blood Moon",  "#0a0000", "#1a0505", "#ff0022", "#cc0033", "#ff6600"),
    make_palette("Cyber Punk",  "#000514", "#0a0a1a", "#ff00ff", "#00ffff", "#ffff00"),
    make_palette("Lavender",    "#0a0014", "#1a0a2a", "#d4a0ff", "#ff8dc7", "#ffe066"),
    make_palette("Midnight",    "#000510", "#0a0a20", "#6688ff", "#44ddff", "#ff8866"),
    make_palette("Candy",       "#1a0010", "#2a0a20", "#ff66aa", "#ffcc00", "#66ffcc"),
    make_palette("Toxic",       "#000a00", "#001a10", "#44ff44", "#00ff88", "#ffff44"),
    make_palette("Warm Glow",   "#1a0800", "#2a1200", "#ff6633", "#ffaa00", "#ffdd88"),
]

# Fields in palette tuple:
name_f = 0
bg1_f = 1; bg2_f = 2
a1_f = 3; a2_f = 4; a3_f = 5
bg1r_f = 6; bg2r_f = 7
a1r_f = 8; a2r_f = 9; a3r_f = 10

# ─── TEMPLATES ────────────────────────────────────────────────────

TEMPLATES = []

def template(name):
    def dec(fn):
        TEMPLATES.append((name, fn))
        return fn
    return dec

@template("Cloth Physics")
def gen_cloth(c):
    """Verlet cloth simulation — strings.html style"""
    grid_w = random.choice([40, 50, 60, 80])
    grid_h = random.choice([30, 40, 50, 60])
    gravity = round(random.uniform(0.05, 0.4), 3)
    damping = round(random.uniform(0.97, 0.995), 3)
    iterations = random.randint(3, 8)
    bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Cloth</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;display:flex;align-items:center;justify-content:center;height:100vh;}}
</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;
canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');
const GW={grid_w},GH={grid_h},G={gravity},D={damping},IT={iterations};
const pw=W/(GW-1),ph=H/(GH-1);
const pts=[];
for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){{pts.push({{x:i*pw,y:j*ph,ox:i*pw,oy:j*ph,pinned:j===0}});}}
const cons=[];
for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){{
  const id=j*GW+i;
  if(j<GH-1)cons.push({{a:id,b:(j+1)*GW+i,len:ph}});
  if(i<GW-1)cons.push({{a:id,b:j*GW+i+1,len:pw}});
}}
function solve(){{for(let n=0;n<IT;n++)for(const co of cons){{
  const p1=pts[co.a],p2=pts[co.b];const dx=p2.x-p1.x,dy=p2.y-p1.y,dist=Math.hypot(dx,dy);
  if(!dist)continue;const diff=co.len-dist,per=diff/dist/2;
  if(!p1.pinned){{p1.x-=dx*per;p1.y-=dy*per;}}if(!p2.pinned){{p2.x+=dx*per;p2.y+=dy*per;}}
}}}}
for(let s=0;s<30;s++){{pts.forEach(p=>{{if(!p.pinned){{const vx=(p.x-p.ox)*D,vy=(p.y-p.oy)*D+0.1;p.ox=p.x;p.oy=p.y;p.x+=vx;p.y+=vy;}}}});solve();}}
function loop(){{requestAnimationFrame(loop);
  ctx.fillStyle='{bg1}';ctx.fillRect(0,0,W,H);
  pts.forEach(p=>{{if(!p.pinned){{const vx=(p.x-p.ox)*D,vy=(p.y-p.oy)*D+G;p.ox=p.x;p.oy=p.y;p.x+=vx;p.y+=vy;}}}});
  solve();
  ctx.strokeStyle='{a2}80';ctx.lineWidth=0.6;
  for(const co of cons){{ctx.beginPath();ctx.moveTo(pts[co.a].x,pts[co.a].y);ctx.lineTo(pts[co.b].x,pts[co.b].y);ctx.stroke();}}
  ctx.fillStyle='{a3}';ctx.font='10px sans';
  pts.forEach(p=>ctx.fillRect(p.x-1,p.y-1,2,2));
}}
loop();
</script></body></html>'''

@template("Particle Galaxy")
def gen_galaxy(c):
    count = random.randint(500, 2000)
    arms = random.randint(2, 5)
    bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Galaxy</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;
canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');
const N={count},ARMS={arms};
const pts=[];
for(let i=0;i<N;i++){{const arm=(i%ARMS)/ARMS*Math.PI*2+Math.random()*0.3;const dist=Math.random()*Math.min(W,H)*0.45;
pts.push({{x:W/2+Math.cos(arm)*dist,y:H/2+Math.sin(arm)*dist,vx:0,vy:0,arm,dist,off:Math.random()*Math.PI*2,size:Math.random()*2+0.5,speed:Math.random()*0.5+0.5}});}}
function loop(){{requestAnimationFrame(loop);
  ctx.fillStyle='{bg1}';ctx.fillRect(0,0,W,H);
  for(const p of pts){{const angle=p.arm+p.off+Date.now()*0.0001*p.speed;
  const tx=W/2+Math.cos(angle)*p.dist,ty=H/2+Math.sin(angle)*p.dist;
  p.x+=((tx+Math.sin(p.off)*5)-p.x)*0.02;p.y+=((ty+Math.cos(p.off)*5)-p.y)*0.02;
  ctx.fillStyle='{a2}60';ctx.beginPath();ctx.arc(p.x,p.y,p.size,0,Math.PI*2);ctx.fill();}}
  for(let i=0;i<30;i++){{const a=pts[Math.floor(Math.random()*N)],b=pts[Math.floor(Math.random()*N)];
  const dx=a.x-b.x,dy=a.y-b.y,ds=Math.hypot(dx,dy);
  if(ds<80){{ctx.strokeStyle='{a3}30';ctx.lineWidth=0.3;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}}}
}}
loop();
</script></body></html>'''

@template("Fire Particles")
def gen_fire(c):
    count = random.randint(200, 800)
    bg1 = c[bg1_f]; a2 = c[a2_f]; a2r = c[a2r_f]

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Fire</title>
<style>body{{margin:0;background:#000;overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;
canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');
const N={count};
const pts=[];
for(let i=0;i<N;i++){{pts.push({{x:W/2+(Math.random()-0.5)*W*0.3,y:H,vy:-(Math.random()*3+1),vx:(Math.random()-0.5)*0.5,life:Math.random()*100+50,max:Math.random()*100+50,size:Math.random()*4+1}});}}
function loop(){{requestAnimationFrame(loop);
  ctx.fillStyle='rgba(0,0,0,0.08)';ctx.fillRect(0,0,W,H);
  for(const p of pts){{p.x+=p.vx;p.y+=p.vy;p.life--;p.vy-=0.01;p.vx+=(Math.random()-0.5)*0.2;
  const t=1-p.life/p.max;if(p.life<=0||p.y<0){{p.x=W/2+(Math.random()-0.5)*W*0.3;p.y=H;p.vy=-(Math.random()*3+1);p.life=p.max;p.vx=(Math.random()-0.5)*0.5;}}
  ctx.fillStyle='rgba({a2r},'+(1-t)*0.8+')';ctx.beginPath();ctx.arc(p.x,p.y,p.size*(1-t),0,Math.PI*2);ctx.fill();}}
  ctx.fillStyle='{bg1}60';ctx.beginPath();ctx.arc(W/2,H,150,0,Math.PI*2);ctx.fill();
}}
loop();
</script></body></html>'''

@template("Wave Grid")
def gen_wave(c):
    cols = random.randint(40, 80)
    rows = random.randint(30, 60)
    bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]

    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Wave</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;
canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');
const COLS={cols},ROWS={rows};
const pw=W/COLS,ph=H/ROWS;
let t=0;
function loop(){{requestAnimationFrame(loop);t+=0.05;
  ctx.fillStyle='{bg1}';ctx.fillRect(0,0,W,H);
  for(let i=0;i<=COLS;i++)for(let j=0;j<=ROWS;j++){{const y=j*ph+Math.sin(i*0.2+t*2)*20*Math.sin(j*0.16+t*1.5)+Math.sin(i*0.1+j*0.06+t)*15;
  ctx.fillStyle='{a2}60';ctx.beginPath();ctx.arc(i*pw,y,1.5,0,Math.PI*2);ctx.fill();}}
  for(let i=0;i<COLS;i++)for(let j=0;j<ROWS;j++){{const y1=j*ph+Math.sin(i*0.2+t*2)*20*Math.sin(j*0.16+t*1.5)+Math.sin(i*0.1+j*0.06+t)*15;
  const y2=j*ph+Math.sin((i+1)*0.2+t*2)*20*Math.sin(j*0.16+t*1.5)+Math.sin((i+1)*0.1+j*0.06+t)*15;
  ctx.strokeStyle='{a3}30';ctx.lineWidth=0.3;ctx.beginPath();ctx.moveTo(i*pw,y1);ctx.lineTo((i+1)*pw,y2);ctx.stroke();}}
}}
loop();
</script></body></html>'''

@template("Pendulum Wave")
def gen_pendulum(c):
    count = random.randint(20, 50)
    bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Pendulum</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;display:flex;align-items:center;justify-content:center;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;
canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');
const N={count};const gap=W/(N+1),len=Math.min(W,H)*0.35;let t=0;
function loop(){{requestAnimationFrame(loop);t+=0.02;
  ctx.fillStyle='{bg1}';ctx.fillRect(0,0,W,H);
  for(let i=0;i<N;i++){{const x=(i+1)*gap;const phase=Math.sin(i*0.1+t)*Math.PI*0.3;
  const px=x+Math.sin(phase)*len,py=H/2+Math.cos(phase)*len;
  ctx.strokeStyle='{a2}60';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(x,H/2);ctx.lineTo(px,py);ctx.stroke();
  ctx.fillStyle='{a3}';ctx.beginPath();ctx.arc(px,py,5+8*(i/N),0,Math.PI*2);ctx.fill();
  ctx.fillStyle='{a2}40';ctx.beginPath();ctx.arc(px,py,10+12*(i/N),0,Math.PI*2);ctx.fill();}}
}}
loop();
</script></body></html>'''

@template("Fractal Tree")
def gen_tree(c):
    branches = random.randint(3, 7)
    depth = random.randint(6, 10)
    bg1r = c[bg1r_f]; bg2 = c[bg2_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Tree</title>
<style>body{{margin:0;background:{bg2};overflow:hidden;display:flex;align-items:center;justify-content:center;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const B={branches},D={depth};let t=0;
function branch(x,y,len,angle,depth){{
  if(depth===0)return;const ex=x+Math.cos(angle)*len,ey=y+Math.sin(angle)*len;
  ctx.strokeStyle='{a2}'+Math.floor(60+40*(depth/D)).toString(16).padStart(2,'0');
  ctx.lineWidth=depth*1.2;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(ex,ey);ctx.stroke();
  const spread=Math.PI*0.4;const tilt=Math.sin(t+depth*0.5)*0.08;
  for(let i=0;i<B;i++)branch(ex,ey,len*0.7,angle-spread/2+spread*i/(B-1)+tilt,depth-1);
}}
function loop(){{requestAnimationFrame(loop);t+=0.01;
  ctx.fillStyle='rgba({bg1r},0.03)';ctx.fillRect(0,0,W,H);
  branch(W/2,H,Math.min(W,H)*0.15,-Math.PI/2+t*0.03,D);
}}
loop();
</script></body></html>'''

@template("Orbit System")
def gen_orbit(c):
    planets = random.randint(5, 12)
    bg1r = c[bg1r_f]; bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Orbit</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;display:flex;align-items:center;justify-content:center;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const N={planets};
const orbits=[];
for(let i=0;i<N;i++){{const r=Math.min(W,H)*0.05+(i/N)*Math.min(W,H)*0.4;
orbits.push({{r,ang:Math.random()*Math.PI*2,speed:(0.3+Math.random()*0.7)/(r*0.02+1),sz:2+Math.random()*6}});}}
function loop(){{requestAnimationFrame(loop);
  ctx.fillStyle='rgba({bg1r},0.03)';ctx.fillRect(0,0,W,H);
  for(const o of orbits){{o.ang+=o.speed*0.02;
  const x=W/2+Math.cos(o.ang)*o.r,y=H/2+Math.sin(o.ang)*o.r;
  ctx.fillStyle='{a3}10';ctx.beginPath();ctx.arc(W/2,H/2,o.r,0,Math.PI*2);ctx.strokeStyle='{a3}20';ctx.lineWidth=0.5;ctx.stroke();
  ctx.fillStyle='{a2}';ctx.beginPath();ctx.arc(x,y,o.sz,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='{a3}30';ctx.beginPath();ctx.arc(x,y,o.sz*2,0,Math.PI*2);ctx.fill();}}
  ctx.fillStyle='{a2}40';ctx.beginPath();ctx.arc(W/2,H/2,8,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='{a3}20';ctx.beginPath();ctx.arc(W/2,H/2,20,0,Math.PI*2);ctx.fill();
}}
loop();
</script></body></html>'''

@template("Flow Field")
def gen_flowfield(c):
    count = random.randint(300, 1500)
    bg1r = c[bg1r_f]; bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Flow Field</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const N={count};
const pts=[];for(let i=0;i<N;i++)pts.push({{x:Math.random()*W,y:Math.random()*H}});
function n(x,y){{return Math.sin(x*0.005)*Math.cos(y*0.005)+Math.sin(y*0.008+x*0.003);}}
let t=0;
function loop(){{requestAnimationFrame(loop);t+=0.003;
  ctx.fillStyle='rgba({bg1r},0.03)';ctx.fillRect(0,0,W,H);
  for(const p of pts){{const a=n(p.x+t*10,p.y+t*10)*Math.PI*4;
  p.x+=Math.cos(a)*1.5;p.y+=Math.sin(a)*1.5;
  if(p.x<0||p.x>W||p.y<0||p.y>H){{p.x=Math.random()*W;p.y=Math.random()*H;}}
  ctx.fillStyle='{a2}60';ctx.beginPath();ctx.arc(p.x,p.y,1,0,Math.PI*2);ctx.fill();}}
  for(let i=0;i<30;i++){{const a=pts[Math.floor(Math.random()*N)],b=pts[Math.floor(Math.random()*N)];
  const dx=a.x-b.x,dy=a.y-b.y,ds=Math.hypot(dx,dy);
  if(ds<50){{ctx.strokeStyle='{a3}20';ctx.lineWidth=0.3;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}}}
}}
loop();
</script></body></html>'''

@template("Bubbles")
def gen_bubbles(c):
    count = random.randint(30, 80)
    bg1r = c[bg1r_f]; bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Bubbles</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const N={count};
const b=[];for(let i=0;i<N;i++)b.push({{x:Math.random()*W,y:Math.random()*H,vy:-(Math.random()*0.5+0.1),vx:(Math.random()-0.5)*0.3,r:Math.random()*30+5,ph:Math.random()*Math.PI*2}});
function loop(){{requestAnimationFrame(loop);
  ctx.fillStyle='rgba({bg1r},0.02)';ctx.fillRect(0,0,W,H);
  for(const p of b){{p.x+=p.vx+Math.sin(Date.now()*0.001+p.ph)*0.2;p.y+=p.vy;
  if(p.y+p.r<0){{p.y=H+p.r;p.x=Math.random()*W;}}
  const g=ctx.createRadialGradient(p.x-p.r*0.3,p.y-p.r*0.3,0,p.x,p.y,p.r);
  g.addColorStop(0,'{a2}50');g.addColorStop(0.5,'{a3}20');g.addColorStop(1,'{a3}05');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle='{a2}30';ctx.lineWidth=0.5;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.stroke();}}
  const g=ctx.createRadialGradient(W*0.2,H*0.3,0,W*0.2,H*0.3,W*0.4);
  g.addColorStop(0,'{a2}15');g.addColorStop(1,'transparent');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
}}
loop();
</script></body></html>'''

@template("Cellular Automata")
def gen_cellular(c):
    bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Cellular</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const SZ=Math.min(W,H)/120|0;
const COLS=Math.ceil(W/SZ)+1,ROWS=Math.ceil(H/SZ)+1;
let grid=Array(COLS*ROWS).fill(0);for(let i=0;i<grid.length;i++)grid[i]=Math.random()<0.4?1:0;
let t=0;
function loop(){{requestAnimationFrame(loop);t++;
  const ng=Array(COLS*ROWS).fill(0);
  for(let j=0;j<ROWS;j++)for(let i=0;i<COLS;i++){{let n=0;
  for(let dj=-1;dj<=1;dj++)for(let di=-1;di<=1;di++){{if(!di&&!dj)continue;const ni=i+di,nj=j+dj;if(ni>=0&&ni<COLS&&nj>=0&&nj<ROWS)n+=grid[nj*COLS+ni];}}
  const idx=j*COLS+i;ng[idx]=grid[idx]===1?(n===2||n===3?1:0):(n===3?1:0);}}
  grid=ng;ctx.fillStyle='{bg1}';ctx.fillRect(0,0,W,H);
  for(let j=0;j<ROWS;j++)for(let i=0;i<COLS;i++){{if(grid[j*COLS+i]){{ctx.fillStyle='{a2}'+Math.floor(Math.sin(t+i*0.1+j*0.1)*30+50).toString(16).padStart(2,'0');ctx.fillRect(i*SZ,j*SZ,SZ,SZ);}}}}
}}
loop();
</script></body></html>'''

@template("Rain")
def gen_rain(c):
    count = random.randint(200, 600)
    bg1r = c[bg1r_f]; bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Rain</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const N={count};
const drops=[];for(let i=0;i<N;i++)drops.push({{x:Math.random()*W,y:Math.random()*H,vy:Math.random()*8+4,vx:(Math.random()-0.5)*0.5,len:Math.random()*20+10}});
function loop(){{requestAnimationFrame(loop);
  ctx.fillStyle='rgba({bg1r},0.05)';ctx.fillRect(0,0,W,H);
  for(const d of drops){{d.x+=d.vx;d.y+=d.vy;
  if(d.y-d.len>H){{d.y=-d.len;d.x=Math.random()*W;d.vy=Math.random()*8+4;}}
  ctx.strokeStyle='{a2}60';ctx.lineWidth=0.5+Math.random()*0.5;ctx.beginPath();ctx.moveTo(d.x,d.y);ctx.lineTo(d.x+d.vx,d.y-d.len);ctx.stroke();}}
  for(let i=0;i<5;i++){{const sx=Math.random()*W,sy=Math.random()*H;const r=Math.random()*50+5;
  const g=ctx.createRadialGradient(sx,sy,0,sx,sy,r);
  g.addColorStop(0,'{a3}20');g.addColorStop(1,'transparent');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);ctx.fill();}}
}}
loop();
</script></body></html>'''

@template("Maze")
def gen_maze(c):
    bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Maze</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const SZ=Math.min(W,H)/80|0;
const COLS=Math.ceil(W/SZ),ROWS=Math.ceil(H/SZ);
const grid=Array(COLS*ROWS).fill(15);const visited=Array(COLS*ROWS).fill(false);
const stack=[0];visited[0]=true;
function carve(x,y,nx,ny){{if(nx>x)grid[y*COLS+x]&=~1;if(nx<x)grid[y*COLS+nx]&=~1;if(ny>y)grid[y*COLS+x]&=~4;if(ny<y)grid[ny*COLS+x]&=~4;}}
function loop(){{requestAnimationFrame(loop);
  for(let s=0;s<100&&stack.length>0;s++){{const idx=stack[stack.length-1];const x=idx%COLS,y=Math.floor(idx/COLS);
  const dirs=[];const d=[[1,0],[0,1],[-1,0],[0,-1]];for(const[dx,dy]of d){{const nx=x+dx,ny=y+dy;
  if(nx>=0&&nx<COLS&&ny>=0&&ny<ROWS&&!visited[ny*COLS+nx])dirs.push([dx,dy,nx,ny]);}}
  if(dirs.length>0){{const[dx,dy,nx,ny]=dirs[Math.floor(Math.random()*dirs.length)];carve(x,y,nx,ny);visited[ny*COLS+nx]=true;stack.push(ny*COLS+nx);}}else stack.pop();}}
  ctx.fillStyle='{bg1}';ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='{a2}80';ctx.lineWidth=0.5;
  for(let j=0;j<ROWS;j++)for(let i=0;i<COLS;i++){{const w=grid[j*COLS+i];const x=i*SZ,y=j*SZ;
  if(w&1){{ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+SZ,y);ctx.stroke();}}
  if(w&4){{ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+SZ);ctx.stroke();}}
  if(j===ROWS-1){{ctx.beginPath();ctx.moveTo(x+SZ,y+SZ);ctx.lineTo(x,y+SZ);ctx.stroke();}}
  if(i===COLS-1){{ctx.beginPath();ctx.moveTo(x+SZ,y);ctx.lineTo(x+SZ,y+SZ);ctx.stroke();}}}}
  if(stack.length>0){{const p=stack[stack.length-1];ctx.fillStyle='{a3}40';ctx.fillRect((p%COLS)*SZ,Math.floor(p/COLS)*SZ,SZ,SZ);}}
  ctx.fillStyle='{a2}60';ctx.fillRect(0,0,SZ,SZ);
  ctx.fillStyle='{a3}60';ctx.fillRect((COLS-1)*SZ,(ROWS-1)*SZ,SZ,SZ);
}}
loop();
</script></body></html>'''

@template("Particle Text")
def gen_text_particles(c):
    count = random.randint(200, 800)
    txt = random.choice(["CODE","LIFE","DREAM","HACK","PLAY","MINE","ZERO","VOID","PIXEL","NOVA","WAVE","FIRE","MOON","STAR","MELT","GRID"])
    bg1 = c[bg1_f]; a2 = c[a2_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Particle Text</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;display:flex;align-items:center;justify-content:center;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const TXT="{txt}";
ctx.font='bold '+Math.min(W,H)*0.2+'px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
const m=ctx.measureText(TXT);const img=document.createElement('canvas');
img.width=Math.ceil(m.tw||m.width);img.height=parseInt(ctx.font);
const ictx=img.getContext('2d');
ictx.fillStyle='#fff';ictx.font=ctx.font;ictx.textAlign='center';ictx.textBaseline='middle';
ictx.fillText(TXT,img.width/2,img.height/2);
const data=ictx.getImageData(0,0,img.width,img.height);
const offX=W/2-img.width/2,offY=H/2-img.height/2;const N={count};
const pts=[];const targets=[];
for(let i=0;i<N;i++){{let tx=offX,ty=offY;
for(let a=0;a<50;a++){{const px=Math.floor(Math.random()*img.width),py=Math.floor(Math.random()*img.height);
if(data.data[(py*img.width+px)*4]>128){{tx=offX+px;ty=offY+py;break;}}}}
targets.push({{x:tx,y:ty}});pts.push({{x:Math.random()*W,y:Math.random()*H,vx:0,vy:0}});}}
function loop(){{requestAnimationFrame(loop);
  ctx.fillStyle='{bg1}';ctx.fillRect(0,0,W,H);
  for(let i=0;i<pts.length;i++){{const p=pts[i],t=targets[i];
  p.vx+=(t.x-p.x)*0.02;p.vy+=(t.y-p.y)*0.02;p.vx*=0.95;p.vy*=0.95;p.x+=p.vx;p.y+=p.vy;
  ctx.fillStyle='{a2}60';ctx.beginPath();ctx.arc(p.x,p.y,1.5,0,Math.PI*2);ctx.fill();}}
}}
loop();
</script></body></html>'''

@template("Snake")
def gen_snake(c):
    bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]; bg1r = c[bg1r_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Snake</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');const SZ=20;
const COLS=Math.floor(W/SZ),ROWS=Math.floor(H/SZ);
let snake=[Math.floor(COLS/2)+Math.floor(ROWS/2)*COLS];let food=0;let dir=0;let nextDir=0;
function loop(){{requestAnimationFrame(loop);dir=nextDir;
  const head=snake[snake.length-1],x=head%COLS,y=Math.floor(head/COLS);
  let nx=x+[1,0,-1,0][dir],ny=y+[0,1,0,-1][dir];
  if(nx<0||nx>=COLS||ny<0||ny>=ROWS){{nx=Math.floor(Math.random()*COLS);ny=Math.floor(Math.random()*ROWS);}}
  const ni=ny*COLS+nx;let grow=ni===food;
  snake.push(ni);if(!grow)snake.shift();
  if(grow){{food=-1;for(let i=0;i<COLS*ROWS;i++){{if(!snake.includes(i)){{food=i;break;}}}}if(food===-1)food=Math.floor(Math.random()*COLS*ROWS);}}
  ctx.fillStyle='rgba({bg1r},0.02)';ctx.fillRect(0,0,W,H);
  for(let i=0;i<snake.length;i++){{const s=snake[i];
  ctx.fillStyle='{a2}'+Math.floor((i/snake.length)*80+20).toString(16).padStart(2,'0');
  ctx.fillRect((s%COLS)*SZ,Math.floor(s/COLS)*SZ,SZ-1,SZ-1);}}
  ctx.fillStyle='{a3}80';ctx.fillRect((food%COLS)*SZ,Math.floor(food/COLS)*SZ,SZ-1,SZ-1);
}}
loop();
</script></body></html>'''

@template("Aurora")
def gen_aurora(c):
    bg1r = c[bg1r_f]; bg1 = c[bg1_f]; a2 = c[a2_f]; a3 = c[a3_f]
    return f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Aurora</title>
<style>body{{margin:0;background:{bg1};overflow:hidden;}}</style></head><body><canvas id="c"></canvas>
<script>
const W=innerWidth,H=innerHeight;canvas.width=W;canvas.height=H;
const ctx=canvas.getContext('2d');let t=0;
const L=Array.from({{length:5}},(_,i)=>({{y:H*0.1+Math.random()*H*0.6,speed:0.1+Math.random()*0.3,amp:30+Math.random()*80,freq:0.002+Math.random()*0.005,color:['{a2}','{a3}','{bg1}','{a2}','{a3}'][i],w:100+Math.random()*200}}));
function loop(){{requestAnimationFrame(loop);t+=0.5;
  ctx.fillStyle='rgba({bg1r},0.01)';ctx.fillRect(0,0,W,H);
  for(const l of L){{ctx.beginPath();
  for(let x=0;x<=W;x+=2){{const y=l.y+Math.sin(x*l.freq+t*l.speed)*l.amp+Math.sin(x*l.freq*2+t*l.speed*0.7)*l.amp*0.5;if(x===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}}
  for(let x=W;x>=0;x-=2){{const y=l.y+10+Math.sin(x*l.freq+t*l.speed+1)*l.amp*0.3;ctx.lineTo(x,y);}}
  ctx.closePath();const g=ctx.createLinearGradient(0,l.y-l.amp,0,l.y+l.w);
  g.addColorStop(0,'transparent');g.addColorStop(0.3,l.color+'60');g.addColorStop(0.7,l.color+'30');g.addColorStop(1,'transparent');
  ctx.fillStyle=g;ctx.fill();}}
  for(let i=0;i<80;i++){{ctx.fillStyle='rgba(255,255,255,'+Math.random()*0.5+')';ctx.beginPath();ctx.arc(Math.random()*W,Math.random()*H,Math.random()*1.5,0,Math.PI*2);ctx.fill();}}
}}
loop();
</script></body></html>'''


# ─── GENERATOR ────────────────────────────────────────────────────

def generate_page(seed=None):
    global random
    import random as _mod_random
    if seed is None:
        seed = _mod_random.randint(0, 999999)

    # Use seed for deterministic randomness
    rng = _mod_random.Random(seed)
    old_random = random
    random = rng

    name, fn = rng.choice(TEMPLATES)
    colors = rng.choice(PALETTES)

    html = fn(colors)

    # Restore global random
    random = old_random

    filename = f"webart_{seed}.html"
    filepath = os.path.join(OUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return {
        "seed": seed,
        "template": name,
        "palette": colors[0],
        "file": filename,
    }


def generate_batch(count=5):
    results = []
    for _ in range(count):
        info = generate_page()
        results.append(info)
        print(f"  [{info['template']:20s}] [{info['palette']:15s}] → {info['file']}")
    return results


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"Generating {n} unique pages...\n")
    results = generate_batch(n)
    print(f"\nDone! {len(results)} pages in output/")
