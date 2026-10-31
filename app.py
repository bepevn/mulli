import json
import random
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="물리엔진 시뮬레이터", page_icon="⚙️", layout="wide")
st.title("⚙️ 물리엔진 시뮬레이터")

W, H = 900, 560  # 캔버스 크기(px), 1 m = 50 px

if "objects" not in st.session_state:
    st.session_state.objects = []
if "nid" not in st.session_state:
    st.session_state.nid = 0


def new_id():
    st.session_state.nid += 1
    return st.session_state.nid


def balls():
    return [o for o in st.session_state.objects if o["type"] in ("ball", "pin")]


def label(o):
    names = {"ball": "공", "pin": "고정 핀", "wall": "벽/경사판", "rod": "막대", "spring": "스프링"}
    return f"#{o['id']} {names[o['type']]}"


# ---------------- 사이드바: 환경 ----------------
with st.sidebar:
    st.header("🌍 환경 설정")
    g = st.slider("중력 g (m/s²)", 0.0, 30.0, 9.8, 0.1)
    e = st.slider("반발계수 e", 0.0, 1.0, 0.8, 0.01)
    drag = st.slider("공기저항", 0.0, 2.0, 0.0, 0.01)
    fric = st.slider("벽 마찰", 0.0, 1.0, 0.1, 0.01)
    speed = st.slider("시간 배속", 0.1, 3.0, 1.0, 0.1)

    st.header("🎬 예제 장면")
    c1, c2 = st.columns(2)
    if c1.button("공 20개"):
        for _ in range(20):
            st.session_state.objects.append(dict(id=new_id(), type="ball", x=random.uniform(60, W - 60),
                y=random.uniform(30, 150), r=random.uniform(8, 30), vx=random.uniform(-150, 150), vy=0.0,
                mass=0.0, color=f"#{random.randint(0, 0xFFFFFF):06x}"))
    if c2.button("경사면"):
        st.session_state.objects += [
            dict(id=new_id(), type="wall", x1=50, y1=150, x2=500, y2=400, color="#8888aa"),
            dict(id=new_id(), type="ball", x=80, y=100, r=20, vx=0.0, vy=0.0, mass=0.0, color="#ff7043")]
    c3, c4 = st.columns(2)
    if c3.button("진자"):
        p = dict(id=new_id(), type="pin", x=W / 2, y=60, r=6, color="#777777")
        b = dict(id=new_id(), type="ball", x=W / 2 + 200, y=60, r=18, vx=0.0, vy=0.0, mass=0.0, color="#42a5f5")
        st.session_state.objects += [p, b, dict(id=new_id(), type="rod", a=p["id"], b=b["id"], length=200)]
    if c4.button("스프링"):
        p = dict(id=new_id(), type="pin", x=W / 2, y=40, r=6, color="#777777")
        b = dict(id=new_id(), type="ball", x=W / 2, y=150, r=20, vx=0.0, vy=0.0, mass=0.0, color="#66bb6a")
        st.session_state.objects += [p, b, dict(id=new_id(), type="spring", a=p["id"], b=b["id"],
                                                length=120, k=30.0, damping=0.3)]
    if st.button("🗑 전체 초기화", use_container_width=True):
        st.session_state.objects = []

# ---------------- 객체 추가 ----------------
left, right = st.columns([1, 2.4])
with left:
    st.subheader("➕ 객체 추가")
    kind = st.selectbox("종류", ["공", "고정 핀", "벽/경사판", "막대(거리 고정)", "스프링"])
    with st.form("add", clear_on_submit=False):
        if kind in ("공", "고정 핀"):
            x = st.number_input("x 위치 (px)", 0, W, W // 2)
            y = st.number_input("y 위치 (px, 아래로 +)", 0, H, 100)
            r = st.slider("반지름 (px)", 4, 60, 20 if kind == "공" else 6)
            color = st.color_picker("색", "#ff7043" if kind == "공" else "#777777")
            if kind == "공":
                vx = st.number_input("초속도 vx (m/s)", -30.0, 30.0, 0.0)
                vy = st.number_input("초속도 vy (m/s, 위로 +)", -30.0, 30.0, 0.0)
                mass = st.number_input("질량 (kg, 0 = 크기로 자동)", 0.0, 100.0, 0.0)
        elif kind == "벽/경사판":
            a1, a2 = st.columns(2)
            x1 = a1.number_input("시작 x", 0, W, 100); y1 = a2.number_input("시작 y", 0, H, 300)
            x2 = a1.number_input("끝 x", 0, W, 500); y2 = a2.number_input("끝 y", 0, H, 450)
            color = st.color_picker("색", "#8888aa")
        else:
            bl = balls()
            if len(bl) < 2:
                st.info("공 또는 고정 핀이 2개 이상 있어야 연결할 수 있어요.")
            opts = {label(o): o["id"] for o in bl}
            ka = st.selectbox("물체 A", list(opts) or ["-"])
            kb = st.selectbox("물체 B", list(opts)[1:] + list(opts)[:1] if opts else ["-"])
            length = st.number_input("자연 길이 (px, 0 = 현재 거리)", 0, 1000, 0)
            if kind == "스프링":
                k = st.slider("탄성계수 k (N/m)", 1.0, 200.0, 30.0)
                damp = st.slider("감쇠", 0.0, 5.0, 0.3)
        ok = st.form_submit_button("추가", use_container_width=True)

    if ok:
        o = None
        if kind == "공":
            o = dict(type="ball", x=x, y=y, r=r, vx=vx * 50, vy=-vy * 50, mass=mass, color=color)
        elif kind == "고정 핀":
            o = dict(type="pin", x=x, y=y, r=r, color=color)
        elif kind == "벽/경사판":
            if (x1, y1) == (x2, y2):
                st.error("시작점과 끝점이 같아요.")
            else:
                o = dict(type="wall", x1=x1, y1=y1, x2=x2, y2=y2, color=color)
        elif opts and ka != kb:
            o = dict(type="rod" if kind.startswith("막대") else "spring", a=opts[ka], b=opts[kb], length=length)
            if kind == "스프링":
                o.update(k=k, damping=damp)
        else:
            st.error("서로 다른 두 물체를 골라주세요.")
        if o:
            o["id"] = new_id()
            st.session_state.objects.append(o)
            st.success(f"{label(o)} 추가됨")

    st.subheader("📋 객체 목록")
    for o in list(st.session_state.objects):
        a, b = st.columns([4, 1])
        a.write(label(o))
        if b.button("✕", key=f"del{o['id']}"):
            rid = o["id"]
            st.session_state.objects = [p for p in st.session_state.objects
                                        if p["id"] != rid and p.get("a") != rid and p.get("b") != rid]
            st.rerun()

# ---------------- 시뮬레이션 (브라우저 JS) ----------------
HTML = r"""
<div style="font-family:sans-serif;color:#ddd">
<div style="margin-bottom:6px">
 <button id="pause">⏸ 일시정지</button> <button id="reset">↺ 처음 상태로</button>
 <button id="vec">➡ 속도벡터</button> <button id="trail">〰 궤적</button>
 <span id="stats" style="font-size:13px;margin-left:10px"></span>
</div>
<div style="margin-bottom:6px;font-size:13px">도구:
 <button class="tool" data-t="select">✋ 선택 [1]</button>
 <button class="tool" data-t="wall">▬ 벽 [2]</button>
 <button class="tool" data-t="spring">〰 스프링 [3]</button>
 <button class="tool" data-t="rod">┃ 막대 [4]</button>
 <span id="mode" style="margin-left:8px;color:#ffd54f"></span>
</div>
<canvas id="c" tabindex="0" width="__W__" height="__H__" style="background:#0b0e14;border-radius:8px;cursor:crosshair;outline:none"></canvas>
<div style="font-size:12px;color:#888;line-height:1.6">
<b>키보드</b> (캔버스 위에 마우스를 올린 상태): <b>B</b> 마우스 위치에 공 · <b>P</b> 고정 핀 · <b>1~4</b> 도구 전환 · <b>Space</b> 일시정지 · <b>Del/X</b> 마우스 아래 물체 삭제 · <b>Esc</b> 그리기 취소<br>
<b>벽</b>: 시작점에서 끝점까지 드래그 · <b>스프링/막대</b>: 물체에서 다른 물체로 드래그 (빈 곳에 놓으면 그 자리에 고정 핀 생성)<br>
선택 도구: 드래그로 공 던지기 · 우클릭 삭제 (캔버스에서 한 변경은 화면 안에서만 유지돼요)</div>
</div>
<script>
const S=__SCENE__, PPM=50, cv=document.getElementById('c'), ctx=cv.getContext('2d'), W=cv.width, H=cv.height;
let bodies, walls, links, paused=false, vec=false, trail=false, drag=null, mouse={x:0,y:0};
function load(){
  bodies=[];walls=[];links=[];const map={};
  for(const o of S.objects){
    if(o.type==='ball'||o.type==='pin'){const b={x:o.x,y:o.y,r:o.r,vx:o.vx||0,vy:o.vy||0,fixed:o.type==='pin',color:o.color,path:[]};
      b.m=o.mass>0?o.mass:o.r*o.r/400;map[o.id]=b;bodies.push(b)}
    else if(o.type==='wall')walls.push(o);
  }
  for(const o of S.objects) if((o.type==='rod'||o.type==='spring')&&map[o.a]&&map[o.b]){
    const a=map[o.a],b=map[o.b];links.push({...o,a,b,L:o.length>0?o.length:Math.hypot(a.x-b.x,a.y-b.y)})}
}
load();
const $=id=>document.getElementById(id);
$('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'▶ 재생':'⏸ 일시정지'};
$('reset').onclick=load; $('vec').onclick=()=>vec=!vec; $('trail').onclick=()=>{trail=!trail;bodies.forEach(b=>b.path=[])};
const hit=(x,y)=>bodies.find(b=>Math.hypot(b.x-x,b.y-y)<b.r);
let tool='select', draft=null; // draft: 드래그로 그리는 중인 벽/스프링/막대
const TN={select:'선택',wall:'벽 그리기',spring:'스프링 연결',rod:'막대 연결'};
function setTool(t){tool=t;draft=null;document.querySelectorAll('.tool').forEach(b=>b.style.background=b.dataset.t===t?'#ffd54f':'');$('mode').textContent='현재: '+TN[t]}
document.querySelectorAll('.tool').forEach(b=>b.onclick=()=>{setTool(b.dataset.t);cv.focus()});
setTool('select');
const rc=()=>`hsl(${Math.random()*360|0},70%,60%)`;
function addBall(x,y){bodies.push({x,y,r:20,m:1,vx:0,vy:0,color:rc(),path:[]})}
function addPin(x,y){const p={x,y,r:6,m:1,vx:0,vy:0,fixed:true,color:'#777',path:[]};bodies.push(p);return p}
function remove(b){bodies=bodies.filter(x=>x!==b);links=links.filter(l=>l.a!==b&&l.b!==b)}
cv.onmouseenter=()=>cv.focus();
cv.onmousedown=e=>{if(e.button)return;cv.focus();const x=e.offsetX,y=e.offsetY,b=hit(x,y);
  if(tool==='select'){if(b&&!b.fixed)drag=b}
  else if(tool==='wall')draft={x1:x,y1:y};
  else draft={a:b||addPin(x,y)}};
cv.onmousemove=e=>{mouse.x=e.offsetX;mouse.y=e.offsetY};
addEventListener('mouseup',()=>{drag=null;if(!draft)return;const x=mouse.x,y=mouse.y;
  if(tool==='wall'){if(Math.hypot(x-draft.x1,y-draft.y1)>10)walls.push({x1:draft.x1,y1:draft.y1,x2:x,y2:y,color:'#8888aa'})}
  else{let b=hit(x,y);if(b!==draft.a){b=b||addPin(x,y);const L=Math.hypot(b.x-draft.a.x,b.y-draft.a.y);
    if(L>5)links.push(tool==='spring'?{type:'spring',a:draft.a,b,L,k:30,damping:0.3}:{type:'rod',a:draft.a,b,L})}}
  draft=null});
cv.oncontextmenu=e=>{e.preventDefault();const b=hit(e.offsetX,e.offsetY);if(b)remove(b);else{const w=nearWall(e.offsetX,e.offsetY);if(w)walls=walls.filter(v=>v!==w)}};
function nearWall(x,y){return walls.find(w=>{const ex=w.x2-w.x1,ey=w.y2-w.y1,t=Math.max(0,Math.min(1,((x-w.x1)*ex+(y-w.y1)*ey)/(ex*ex+ey*ey)));return Math.hypot(x-w.x1-ex*t,y-w.y1-ey*t)<8})}
cv.onkeydown=e=>{const k=e.key.toLowerCase();
  if(k==='b')addBall(mouse.x,mouse.y);
  else if(k==='p')addPin(mouse.x,mouse.y);
  else if(k>='1'&&k<='4')setTool(['select','wall','spring','rod'][+k-1]);
  else if(k===' '){$('pause').click()}
  else if(k==='delete'||k==='x'||k==='backspace'){const b=hit(mouse.x,mouse.y);if(b)remove(b);else{const w=nearWall(mouse.x,mouse.y);if(w)walls=walls.filter(v=>v!==w)}}
  else if(k==='escape')draft=null;
  else return;
  e.preventDefault()};
function bounce(b,nx,ny,o){ // 법선 n 방향으로 o만큼 밀어내고 반사
  b.x+=nx*o;b.y+=ny*o;const vn=b.vx*nx+b.vy*ny;
  if(vn<0){const tx=-ny,ty=nx,vt=(b.vx*tx+b.vy*ty)*(1-S.fric*0.1);const nvn=-vn*S.e;b.vx=nx*nvn+tx*vt;b.vy=ny*nvn+ty*vt}}
function step(dt){
  const g=S.g*PPM;
  for(const l of links) if(l.type==='spring'){ // 훅의 법칙 + 감쇠
    const{a,b}=l;let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1e-6,nx=dx/d,ny=dy/d;
    const rel=(b.vx-a.vx)*nx+(b.vy-a.vy)*ny, F=l.k*(d-l.L)+l.damping*rel; // px 단위 근사
    if(!a.fixed){a.vx+=F*nx/a.m*dt;a.vy+=F*ny/a.m*dt} if(!b.fixed){b.vx-=F*nx/b.m*dt;b.vy-=F*ny/b.m*dt}}
  for(const b of bodies){if(b.fixed)continue;
    if(b===drag){b.vx=(mouse.x-b.x)/dt*.5;b.vy=(mouse.y-b.y)/dt*.5}
    else{b.vy+=g*dt;const k=Math.exp(-S.drag*dt);b.vx*=k;b.vy*=k}
    b.x+=b.vx*dt;b.y+=b.vy*dt;
    if(b.y+b.r>H)bounce(b,0,-1,b.y+b.r-H); if(b.y-b.r<0)bounce(b,0,1,b.r-b.y);
    if(b.x-b.r<0)bounce(b,1,0,b.r-b.x); if(b.x+b.r>W)bounce(b,-1,0,b.x+b.r-W);
    for(const w of walls){ // 원-선분 충돌
      const ex=w.x2-w.x1,ey=w.y2-w.y1,t=Math.max(0,Math.min(1,((b.x-w.x1)*ex+(b.y-w.y1)*ey)/(ex*ex+ey*ey)));
      const px=w.x1+ex*t,py=w.y1+ey*t,dx=b.x-px,dy=b.y-py,d=Math.hypot(dx,dy),R=b.r+3;
      if(d<R&&d>0)bounce(b,dx/d,dy/d,R-d)}
  }
  for(let i=0;i<bodies.length;i++)for(let j=i+1;j<bodies.length;j++){ // 공-공 충격량 충돌
    const a=bodies[i],b=bodies[j];if(a.fixed&&b.fixed)continue;
    if(links.some(l=>(l.a===a&&l.b===b)||(l.a===b&&l.b===a)))continue;
    let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy),o=a.r+b.r-d;
    if(o>0&&d>0){const nx=dx/d,ny=dy/d,ia=a.fixed?0:1/a.m,ib=b.fixed?0:1/b.m,s=ia+ib;
      a.x-=nx*o*ia/s;a.y-=ny*o*ia/s;b.x+=nx*o*ib/s;b.y+=ny*o*ib/s;
      const vn=(b.vx-a.vx)*nx+(b.vy-a.vy)*ny;
      if(vn<0){const J=-(1+S.e)*vn/s;a.vx-=J*nx*ia;a.vy-=J*ny*ia;b.vx+=J*nx*ib;b.vy+=J*ny*ib}}}
  for(let it=0;it<4;it++)for(const l of links){if(l.type!=='rod')continue; // 막대: 거리 제약
    const{a,b,L}=l;let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1e-6,diff=(d-L)/d,ia=a.fixed?0:1/a.m,ib=b.fixed?0:1/b.m,s=ia+ib;if(!s)continue;
    const nx=dx/d,ny=dy/d;a.x+=dx*diff*ia/s;a.y+=dy*diff*ia/s;b.x-=dx*diff*ib/s;b.y-=dy*diff*ib/s;
    const vn=(b.vx-a.vx)*nx+(b.vy-a.vy)*ny;a.vx+=vn*nx*ia/s;a.vy+=vn*ny*ia/s;b.vx-=vn*nx*ib/s;b.vy-=vn*ny*ib/s}
}
function drawSpring(a,b){const n=12,dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1,px=-dy/d*7,py=dx/d*7;
  ctx.beginPath();ctx.moveTo(a.x,a.y);for(let i=1;i<n;i++){const s=i%2?1:-1;ctx.lineTo(a.x+dx*i/n+px*s,a.y+dy*i/n+py*s)}ctx.lineTo(b.x,b.y);ctx.stroke()}
function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.lineCap='round';for(const w of walls){ctx.strokeStyle=w.color;ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(w.x1,w.y1);ctx.lineTo(w.x2,w.y2);ctx.stroke()}
  ctx.lineWidth=2;for(const l of links){ctx.strokeStyle=l.type==='spring'?'#e0c060':'#999';
    if(l.type==='spring')drawSpring(l.a,l.b);else{ctx.beginPath();ctx.moveTo(l.a.x,l.a.y);ctx.lineTo(l.b.x,l.b.y);ctx.stroke()}}
  for(const b of bodies){
    if(trail&&b.path.length>1){ctx.strokeStyle=b.color+'';ctx.globalAlpha=.4;ctx.beginPath();b.path.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.stroke();ctx.globalAlpha=1}
    ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,7);ctx.fillStyle=b.fixed?'#555':b.color;ctx.fill();
    if(vec&&!b.fixed){ctx.strokeStyle='#ff0';ctx.beginPath();ctx.moveTo(b.x,b.y);ctx.lineTo(b.x+b.vx*.1,b.y+b.vy*.1);ctx.stroke()}}
  if(draft){ctx.setLineDash([6,5]);ctx.lineWidth=tool==='wall'?6:2;ctx.strokeStyle='#ffd54f';ctx.globalAlpha=.7;
    const m={x:mouse.x,y:mouse.y};if(tool==='wall'){ctx.beginPath();ctx.moveTo(draft.x1,draft.y1);ctx.lineTo(m.x,m.y);ctx.stroke()}
    else if(tool==='spring')drawSpring(draft.a,m);else{ctx.beginPath();ctx.moveTo(draft.a.x,draft.a.y);ctx.lineTo(m.x,m.y);ctx.stroke()}
    ctx.setLineDash([]);ctx.globalAlpha=1;ctx.lineWidth=2}
  let KE=0,PE=0;for(const b of bodies)if(!b.fixed){KE+=.5*b.m*((b.vx/PPM)**2+(b.vy/PPM)**2);PE+=b.m*S.g*(H-b.y)/PPM}
  $('stats').textContent=`물체 ${bodies.length}개 · KE ${KE.toFixed(1)} J · PE ${PE.toFixed(1)} J · 합 ${(KE+PE).toFixed(1)} J`;
}
let last=performance.now(),frame=0;
function loop(now){const dt=Math.min((now-last)/1000,1/30);last=now;
  if(!paused){for(let i=0;i<8;i++)step(dt*S.speed/8);
    if(trail&&++frame%3==0)bodies.forEach(b=>{b.path.push([b.x,b.y]);if(b.path.length>200)b.path.shift()})}
  draw();requestAnimationFrame(loop)}
requestAnimationFrame(loop);
</script>
"""

scene = dict(g=g, e=e, drag=drag, fric=fric, speed=speed, objects=st.session_state.objects)
with right:
    components.html(HTML.replace("__SCENE__", json.dumps(scene)).replace("__W__", str(W)).replace("__H__", str(H)),
                    height=H + 80)
