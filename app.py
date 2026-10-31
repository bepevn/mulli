import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="알까기의 달인", page_icon="⚫", layout="centered")
st.markdown("<style>.block-container{padding-top:1rem;padding-bottom:0} header{visibility:hidden}</style>",
            unsafe_allow_html=True)

# 게임 전체(메뉴·AI 대전·오프라인 대전·상점·결과 화면)는 브라우저에서 동작합니다.
# 알포인트와 스킨은 브라우저 localStorage에 저장됩니다.
GAME_HTML = r'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><title>알까기의 달인</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#1b1410;font-family:'Malgun Gothic',sans-serif;color:#fff;display:flex;justify-content:center}
#wrap{position:relative;width:640px;height:740px}
.screen{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 30%,#4a3020,#1b1410)}
.screen.on{display:flex}
h1{font-size:54px;margin:0 0 6px;color:#ffd36b;text-shadow:3px 3px 0 #7a3b00,0 0 20px #ff9d00}
.sub{color:#d8b98a;margin-bottom:30px}
.btn{width:260px;padding:14px;margin:7px;font-size:20px;font-weight:bold;border:0;border-radius:12px;cursor:pointer;background:linear-gradient(#ffcf5a,#e09000);color:#3a1d00;box-shadow:0 5px 0 #8a5200}
.btn:active{transform:translateY(3px);box-shadow:0 2px 0 #8a5200}.btn.gray{background:linear-gradient(#bbb,#888);box-shadow:0 5px 0 #555;color:#222}
.btn.sm{width:auto;padding:8px 14px;font-size:15px}
.pts{position:absolute;top:14px;right:18px;font-size:18px;color:#ffd36b}
.opt{display:flex;gap:8px;margin:6px 0 16px}.opt button{padding:10px 18px;font-size:16px;border-radius:10px;border:2px solid #ffd36b;background:transparent;color:#ffd36b;cursor:pointer}
.opt button.sel{background:#ffd36b;color:#3a1d00}
#game{background:#1b1410;justify-content:flex-start}
#hud{width:640px;height:90px;display:flex;align-items:center;justify-content:space-between;padding:0 16px}
#turn{font-size:22px;font-weight:bold}.cnt{display:flex;align-items:center;gap:6px;font-size:18px}
canvas{display:block}
#shopGrid{display:grid;grid-template-columns:repeat(3,180px);gap:12px;margin:14px 0}
.card{background:#2c1e14;border:2px solid #6b4a2a;border-radius:12px;padding:10px;text-align:center}
.card.eq{border-color:#ffd36b;box-shadow:0 0 12px #ffb300}.card .nm{font-weight:bold;margin:4px 0}.card .pr{color:#ffd36b;font-size:14px;margin-bottom:6px}
#result h1.lose{color:#9aa4b8;text-shadow:3px 3px 0 #222,0 0 20px #4060a0}
#confetti{position:absolute;inset:0;pointer-events:none}
.toast{position:absolute;top:100px;left:50%;transform:translateX(-50%);background:#000c;padding:10px 20px;border-radius:10px;display:none}
</style></head><body><div id="wrap">

<div id="menu" class="screen on"><div class="pts">🪙 <span class="ptv"></span> 알포인트</div>
 <div style="font-size:70px">⚫⚪</div><h1>알까기의 달인</h1><div class="sub">튕겨서 상대 알을 판 밖으로!</div>
 <button class="btn" onclick="show('aiSetup')">🤖 AI 대전</button>
 <button class="btn" onclick="startGame('pvp')">👥 오프라인 대전</button>
 <button class="btn" onclick="openShop()">🛒 스킨 상점</button>
 <button class="btn gray" onclick="show('help')">❓ 게임 방법</button></div>

<div id="help" class="screen"><h1 style="font-size:36px">게임 방법</h1>
 <div style="max-width:440px;line-height:1.9;color:#eedcc0;margin-bottom:20px">
 • 내 차례에 <b>내 알을 누르고 뒤로 당겼다 놓으면</b> 반대 방향으로 튕겨나가요.<br>
 • 많이 당길수록 세게 나가요 (새총 방식).<br>• 판 밖으로 나간 알은 사라져요. 내 알도 나갈 수 있으니 조심!<br>
 • 상대 알을 모두 없애면 승리. 흑이 먼저 둡니다.<br>
 • AI에게 이기면 알포인트 획득 (쉬움 10 · 보통 20 · 어려움 35 + 남은 알 1개당 2).<br>• 포인트로 흑돌·백돌 스킨을 각각 살 수 있어요.</div>
 <button class="btn" onclick="show('menu')">돌아가기</button></div>

<div id="aiSetup" class="screen"><h1 style="font-size:38px">AI 대전</h1>
 <div>난이도</div><div class="opt" id="optDiff"><button data-v="easy">쉬움</button><button data-v="normal" class="sel">보통</button><button data-v="hard">어려움</button></div>
 <div>내 돌</div><div class="opt" id="optColor"><button data-v="black" class="sel">⚫ 흑 (선공)</button><button data-v="white">⚪ 백 (후공)</button></div>
 <button class="btn" onclick="startGame('ai')">대전 시작!</button><button class="btn gray" onclick="show('menu')">뒤로</button></div>

<div id="shop" class="screen" style="justify-content:flex-start;padding-top:30px"><div class="pts">🪙 <span class="ptv"></span> 알포인트</div>
 <h1 style="font-size:38px">스킨 상점</h1>
 <div class="opt" id="optShop"><button data-v="black" class="sel">⚫ 흑돌 스킨</button><button data-v="white">⚪ 백돌 스킨</button></div>
 <div id="shopGrid"></div><button class="btn gray" onclick="show('menu')">메뉴로</button><div class="toast" id="toast"></div></div>

<div id="game" class="screen"><div id="hud">
 <div class="cnt"><canvas id="ib" width="30" height="30"></canvas><span id="nb">5</span> <span id="lb" style="font-size:13px;color:#aaa"></span></div>
 <div id="turn"></div>
 <div class="cnt"><span id="lw" style="font-size:13px;color:#aaa"></span> <span id="nw">5</span><canvas id="iw" width="30" height="30"></canvas></div></div>
 <canvas id="cv" width="640" height="640"></canvas>
 <button class="btn sm gray" style="position:absolute;top:28px;left:50%;transform:translateX(-50%) translateY(28px)" onclick="if(confirm('메뉴로 나갈까요? (진행 중인 게임은 사라져요)'))show('menu')">메뉴</button></div>

<div id="result" class="screen"><canvas id="confetti" width="640" height="740"></canvas>
 <div id="rIcon" style="font-size:80px"></div><h1 id="rTitle"></h1><div id="rSub" class="sub" style="font-size:18px;text-align:center"></div>
 <button class="btn" onclick="startGame(G.mode)">🔁 다시 하기</button><button class="btn gray" onclick="show('menu')">🏠 메뉴로</button></div>
</div>
<script>
// ===== 저장 =====
const SKINS={
 b0:{n:'기본 흑돌',col:'black',p:0,c1:'#666',c2:'#000'},
 b1:{n:'흑요석',col:'black',p:30,c1:'#8a72b8',c2:'#120a1e'},
 b2:{n:'용암',col:'black',p:60,c1:'#ff8a3d',c2:'#2a0500',ring:'#ff4500'},
 b3:{n:'밤하늘',col:'black',p:90,c1:'#3a5bd9',c2:'#050a2a',stars:'#fff'},
 b4:{n:'황금테 흑돌',col:'black',p:150,c1:'#555',c2:'#000',ring:'#ffd700',glow:'#ffd700'},
 b5:{n:'흑룡',col:'black',p:250,c1:'#1fbf6a',c2:'#001a0c',ring:'#00ff88',stars:'#9fffc8',glow:'#00ff88'},
 w0:{n:'기본 백돌',col:'white',p:0,c1:'#ffffff',c2:'#b8b8b8'},
 w1:{n:'진주',col:'white',p:30,c1:'#ffffff',c2:'#d9c6ea'},
 w2:{n:'얼음',col:'white',p:60,c1:'#f0fbff',c2:'#6fbde0',ring:'#bff0ff'},
 w3:{n:'벚꽃',col:'white',p:90,c1:'#fff0f6',c2:'#f48fb8',stars:'#ff5c9a'},
 w4:{n:'은빛 백돌',col:'white',p:150,c1:'#ffffff',c2:'#9aa0b0',ring:'#e0e6ff',glow:'#cfd8ff'},
 w5:{n:'백호',col:'white',p:250,c1:'#ffffff',c2:'#ffcf70',ring:'#ff9d00',stars:'#ff8800',glow:'#ffd36b'}};
let SAVE={points:0,owned:['b0','w0'],equip:{black:'b0',white:'w0'}};
try{const s=JSON.parse(localStorage.getItem('alkkagi_save'));if(s)SAVE=Object.assign(SAVE,s)}catch(e){}
function save(){try{localStorage.setItem('alkkagi_save',JSON.stringify(SAVE))}catch(e){}}
function refreshPts(){document.querySelectorAll('.ptv').forEach(e=>e.textContent=SAVE.points)}

// ===== 화면 =====
const $=id=>document.getElementById(id);
function show(id){document.querySelectorAll('.screen').forEach(s=>s.classList.toggle('on',s.id===id));refreshPts();if(id!=='game')G.running=false;if(id!=='result')confettiOn=false}
function opt(id){const box=$(id);box.querySelectorAll('button').forEach(b=>b.onclick=()=>{box.querySelectorAll('button').forEach(x=>x.classList.remove('sel'));b.classList.add('sel');if(id==='optShop')renderShop()})}
const optVal=id=>$(id).querySelector('.sel').dataset.v;
['optDiff','optColor','optShop'].forEach(opt);

// ===== 알 그리기 =====
function drawStone(c,x,y,r,key,alpha=1){const s=SKINS[key];c.save();c.globalAlpha=alpha;
 if(s.glow){c.shadowColor=s.glow;c.shadowBlur=r*.8}else{c.shadowColor='#0008';c.shadowBlur=r*.4;c.shadowOffsetY=r*.15}
 const g=c.createRadialGradient(x-r*.35,y-r*.35,r*.1,x,y,r);g.addColorStop(0,s.c1);g.addColorStop(1,s.c2);
 c.beginPath();c.arc(x,y,r,0,7);c.fillStyle=g;c.fill();c.shadowBlur=0;c.shadowOffsetY=0;
 if(s.stars){c.fillStyle=s.stars;for(let i=0;i<7;i++){const a=i*2.4+key.length,d=r*(.25+.5*((i*37)%10)/10);c.beginPath();c.arc(x+Math.cos(a)*d,y+Math.sin(a)*d,r*.07,0,7);c.fill()}}
 if(s.ring){c.strokeStyle=s.ring;c.lineWidth=r*.14;c.beginPath();c.arc(x,y,r*.82,0,7);c.stroke()}
 c.fillStyle='#ffffff55';c.beginPath();c.ellipse(x-r*.35,y-r*.4,r*.3,r*.15,-.6,0,7);c.fill();c.restore()}

// ===== 상점 =====
function openShop(){show('shop');renderShop()}
function toast(t){const e=$('toast');e.textContent=t;e.style.display='block';clearTimeout(toast.h);toast.h=setTimeout(()=>e.style.display='none',1500)}
function renderShop(){const col=optVal('optShop'),grid=$('shopGrid');grid.innerHTML='';
 for(const k in SKINS){const s=SKINS[k];if(s.col!==col)continue;const own=SAVE.owned.includes(k),eq=SAVE.equip[col]===k;
  const d=document.createElement('div');d.className='card'+(eq?' eq':'');
  d.innerHTML=`<canvas width="80" height="80"></canvas><div class="nm">${s.n}</div><div class="pr">${s.p?'🪙 '+s.p:'기본'}</div>`;
  const b=document.createElement('button');b.className='btn sm'+(own&&!eq?' gray':'');b.textContent=eq?'장착 중':own?'장착':'구매';
  b.onclick=()=>{if(eq)return;if(own){SAVE.equip[col]=k;save();renderShop();toast(s.n+' 장착!');return}
   if(SAVE.points<s.p){toast('알포인트가 '+(s.p-SAVE.points)+' 부족해요');return}
   if(!confirm(`${s.n} 스킨을 ${s.p} 알포인트에 살까요?`))return;
   SAVE.points-=s.p;SAVE.owned.push(k);SAVE.equip[col]=k;save();refreshPts();renderShop();toast('구매 완료! '+s.n+' 장착')};
  d.appendChild(b);grid.appendChild(d);drawStone(d.querySelector('canvas').getContext('2d'),40,40,28,k)}}

// ===== 게임 =====
const cv=$('cv'),ctx=cv.getContext('2d'),B={x:20,y:20,w:600,h:600},R=19,DECEL=330,MAXPULL=140,POWER=9.5;
const REWARD={easy:10,normal:20,hard:35},NOISE={easy:[.14,.25],normal:[.06,.12],hard:[.02,.05]},DN={easy:'쉬움',normal:'보통',hard:'어려움'};
let G={running:false},aim=null,mouse={x:0,y:0};
function startGame(mode){
 G={mode,running:true,turn:'black',stones:[],moving:false,shooter:null,over:false,msg:'',msgT:0,
   diff:optVal('optDiff'),human:mode==='ai'?optVal('optColor'):null};
 G.skin={black:SAVE.equip.black,white:SAVE.equip.white};
 if(mode==='ai'){const aiCol=G.human==='black'?'white':'black';G.skin[aiCol]=aiCol==='black'?'b0':'w0'}
 for(let i=0;i<5;i++){const x=B.x+100+i*100;G.stones.push({col:'white',x,y:B.y+130+(i%2)*40,vx:0,vy:0,alive:true,fall:0});
  G.stones.push({col:'black',x,y:B.y+B.h-130-(i%2)*40,vx:0,vy:0,alive:true,fall:0})}
 drawStone($('ib').getContext('2d'),15,15,12,G.skin.black);drawStone($('iw').getContext('2d'),15,15,12,G.skin.white);
 $('lb').textContent=mode==='ai'?(G.human==='black'?'나':'AI'):'1P';$('lw').textContent=mode==='ai'?(G.human==='white'?'나':'AI'):'2P';
 show('game');G.running=true;nextTurnUI();last=performance.now();requestAnimationFrame(loop)}
const isAI=()=>G.mode==='ai'&&G.turn!==G.human;
function nextTurnUI(){const n=G.turn==='black'?'⚫ 흑':'⚪ 백';
 $('turn').textContent=G.mode==='ai'?(isAI()?`${n} · AI(${DN[G.diff]}) 생각 중...`:`${n} · 내 차례`):`${n} 차례`;
 if(isAI())setTimeout(aiShoot,900)}
const alive=c=>G.stones.filter(s=>s.alive&&s.col===c);
function updateCount(){$('nb').textContent=alive('black').length;$('nw').textContent=alive('white').length}

function pos(e){const r=cv.getBoundingClientRect(),t=e.touches?e.touches[0]:e;return{x:(t.clientX-r.left)*cv.width/r.width,y:(t.clientY-r.top)*cv.height/r.height}}
function down(e){if(!G.running||G.moving||G.over||isAI())return;const p=pos(e);mouse=p;
 const s=G.stones.find(s=>s.alive&&s.col===G.turn&&Math.hypot(s.x-p.x,s.y-p.y)<R+6);if(s){aim=s;e.preventDefault()}}
function move(e){if(!aim)return;mouse=pos(e);e.preventDefault()}
function up(){if(!aim)return;let dx=aim.x-mouse.x,dy=aim.y-mouse.y,d=Math.hypot(dx,dy);
 if(d>8){const k=Math.min(d,MAXPULL)/d;shoot(aim,dx*k*POWER,dy*k*POWER)}aim=null}
cv.addEventListener('mousedown',down);addEventListener('mousemove',move);addEventListener('mouseup',up);
cv.addEventListener('touchstart',down,{passive:false});addEventListener('touchmove',move,{passive:false});addEventListener('touchend',up);
function shoot(s,vx,vy){s.vx=vx;s.vy=vy;G.moving=true;G.shooter=G.turn}

// ----- AI -----
function aiShoot(){if(!G.running||G.over||!isAI())return;
 const me=alive(G.turn),op=alive(G.turn==='black'?'white':'black');let best=null;
 for(const s of me)for(const t of op){const dx=t.x-s.x,dy=t.y-s.y,dist=Math.hypot(dx,dy),ux=dx/dist,uy=dy/dist;
  // 경로에 다른 알이 있으면 감점
  let blocked=0;for(const o of G.stones){if(!o.alive||o===s||o===t)continue;const px=o.x-s.x,py=o.y-s.y,proj=px*ux+py*uy;
   if(proj>0&&proj<dist&&Math.abs(px*uy-py*ux)<2*R)blocked++}
  // t가 밀려나 판 밖까지 가는 거리
  let exit=1e9;if(ux>0)exit=Math.min(exit,(B.x+B.w-t.x)/ux);if(ux<0)exit=Math.min(exit,(B.x-t.x)/ux);
  if(uy>0)exit=Math.min(exit,(B.y+B.h-t.y)/uy);if(uy<0)exit=Math.min(exit,(B.y-t.y)/uy);
  const vt=Math.sqrt(2*DECEL*(exit+R*2))*1.12, v0=Math.min(Math.sqrt(vt*vt/0.85+2*DECEL*Math.max(0,dist-2*R)),MAXPULL*POWER);
  const score=-exit-dist*.35-blocked*400-(v0>=MAXPULL*POWER?150:0);
  if(!best||score>best.score)best={s,ux,uy,v0,score}}
 if(!best)return;const[na,np]=NOISE[G.diff],a=Math.atan2(best.uy,best.ux)+(Math.random()*2-1)*na,v=best.v0*(1+(Math.random()*2-1)*np);
 const vv=Math.min(v,MAXPULL*POWER);G.aiAim={s:best.s,a,v:vv,t:0}}

// ----- 물리 -----
function step(dt){const st=G.stones.filter(s=>s.alive&&s.fall===0);
 for(const s of st){const sp=Math.hypot(s.vx,s.vy);if(sp>0){const ns=Math.max(0,sp-DECEL*dt);s.vx*=ns/sp;s.vy*=ns/sp}s.x+=s.vx*dt;s.y+=s.vy*dt}
 for(let i=0;i<st.length;i++)for(let j=i+1;j<st.length;j++){const a=st[i],b=st[j],dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);
  if(d<2*R&&d>0){const nx=dx/d,ny=dy/d,o=(2*R-d)/2;a.x-=nx*o;a.y-=ny*o;b.x+=nx*o;b.y+=ny*o;
   const vn=(b.vx-a.vx)*nx+(b.vy-a.vy)*ny;if(vn<0){const J=-(1+.92)*vn/2;a.vx-=J*nx;a.vy-=J*ny;b.vx+=J*nx;b.vy+=J*ny}}}
 for(const s of st)if(s.x<B.x||s.x>B.x+B.w||s.y<B.y||s.y>B.y+B.h)s.fall=0.001}
function loop(now){if(!G.running)return;const dt=Math.min((now-last)/1000,1/30);last=now;
 if(G.aiAim){const A=G.aiAim;A.t+=dt;if(A.t>0.8){shoot(A.s,Math.cos(A.a)*A.v,Math.sin(A.a)*A.v);G.aiAim=null}}
 if(G.moving){for(let i=0;i<10;i++)step(dt/10);
  for(const s of G.stones)if(s.fall>0){s.fall+=dt*2.5;s.x+=s.vx*dt*.3;s.y+=s.vy*dt*.3;if(s.fall>=1){s.alive=false;s.fall=0}}
  updateCount();
  if(G.stones.every(s=>!s.alive||(s.fall===0&&s.vx===0&&s.vy===0)))endShot()}
 draw();requestAnimationFrame(loop)}
function endShot(){G.moving=false;const b=alive('black').length,w=alive('white').length;
 if(b===0||w===0){let win=b===0&&w===0?(G.shooter==='black'?'white':'black'):(b===0?'white':'black');finish(win);return}
 G.turn=G.turn==='black'?'white':'black';nextTurnUI()}

// ----- 그리기 -----
function draw(){ctx.fillStyle='#1b1410';ctx.fillRect(0,0,640,640);
 const g=ctx.createLinearGradient(0,0,640,640);g.addColorStop(0,'#e8b86a');g.addColorStop(1,'#c8913e');
 ctx.shadowColor='#000';ctx.shadowBlur=20;ctx.fillStyle=g;ctx.fillRect(B.x,B.y,B.w,B.h);ctx.shadowBlur=0;
 ctx.strokeStyle='#5a3a10aa';ctx.lineWidth=1;const n=19,step=B.w/(n+1);
 for(let i=1;i<=n;i++){ctx.beginPath();ctx.moveTo(B.x+step,B.y+i*step);ctx.lineTo(B.x+B.w-step,B.y+i*step);ctx.stroke();
  ctx.beginPath();ctx.moveTo(B.x+i*step,B.y+step);ctx.lineTo(B.x+i*step,B.y+B.h-step);ctx.stroke()}
 ctx.fillStyle='#5a3a10';for(const a of[4,10,16])for(const c of[4,10,16]){ctx.beginPath();ctx.arc(B.x+a*step,B.y+c*step,3.5,0,7);ctx.fill()}
 ctx.strokeStyle='#3a2208';ctx.lineWidth=4;ctx.strokeRect(B.x,B.y,B.w,B.h);
 // 내 차례 알 강조
 if(!G.moving&&!G.over&&!isAI()&&!aim)for(const s of alive(G.turn)){ctx.strokeStyle=`rgba(255,230,80,${.4+.3*Math.sin(performance.now()/200)})`;ctx.lineWidth=3;ctx.beginPath();ctx.arc(s.x,s.y,R+5,0,7);ctx.stroke()}
 for(const s of G.stones)if(s.alive)drawStone(ctx,s.x,s.y,R*(1-s.fall*.6),G.skin[s.col],1-s.fall);
 // 조준선
 const A=aim?{s:aim,dx:aim.x-mouse.x,dy:aim.y-mouse.y}:G.aiAim?{s:G.aiAim.s,dx:Math.cos(G.aiAim.a)*G.aiAim.v/POWER*Math.min(1,G.aiAim.t/.5),dy:Math.sin(G.aiAim.a)*G.aiAim.v/POWER*Math.min(1,G.aiAim.t/.5)}:null;
 if(A){let d=Math.hypot(A.dx,A.dy);if(d>1){const k=Math.min(d,MAXPULL)/d,dx=A.dx*k,dy=A.dy*k,pw=Math.min(d,MAXPULL)/MAXPULL;
  ctx.strokeStyle='#fff8';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.beginPath();ctx.moveTo(A.s.x,A.s.y);ctx.lineTo(A.s.x-dx,A.s.y-dy);ctx.stroke();ctx.setLineDash([]);
  const col=`hsl(${120-pw*120},90%,50%)`,ex=A.s.x+dx*1.6,ey=A.s.y+dy*1.6,an=Math.atan2(dy,dx);
  ctx.strokeStyle=col;ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(A.s.x,A.s.y);ctx.lineTo(ex,ey);ctx.stroke();
  ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(ex+Math.cos(an)*14,ey+Math.sin(an)*14);ctx.lineTo(ex+Math.cos(an+2.4)*14,ey+Math.sin(an+2.4)*14);ctx.lineTo(ex+Math.cos(an-2.4)*14,ey+Math.sin(an-2.4)*14);ctx.fill();
  ctx.fillStyle='#000a';ctx.fillRect(220,600,200,14);ctx.fillStyle=col;ctx.fillRect(220,600,200*pw,14);ctx.fillStyle='#fff';ctx.font='12px sans-serif';ctx.fillText('파워 '+Math.round(pw*100)+'%',290,611)}}}

// ----- 결과 -----
let confettiOn=false,parts=[];
function finish(win){G.over=true;setTimeout(()=>{
 let title,icon,sub,isWin=true;const left=alive(win).length;
 if(G.mode==='ai'){isWin=win===G.human;
  if(isWin){const pt=REWARD[G.diff]+left*2;SAVE.points+=pt;save();title='승리!';icon='🏆';sub=`AI(${DN[G.diff]})를 이겼어요!<br>🪙 +${pt} 알포인트 (기본 ${REWARD[G.diff]} + 남은 알 ${left}개 보너스 ${left*2})<br>보유: ${SAVE.points} 알포인트`}
  else{title='패배...';icon='💀';sub=`AI(${DN[G.diff]})에게 졌어요.<br>AI의 알이 ${left}개 남았어요. 다시 도전해 보세요!`}}
 else{title=(win==='black'?'⚫ 흑':'⚪ 백')+' 승리!';icon='🏆';sub=`${win==='black'?'1P':'2P'}가 알 ${left}개를 남기고 이겼어요!`}
 $('rTitle').textContent=title;$('rTitle').className=isWin?'':'lose';$('rIcon').textContent=icon;$('rSub').innerHTML=sub;
 $('result').style.background=isWin?'radial-gradient(circle at 50% 30%,#6a4a10,#1b1410)':'radial-gradient(circle at 50% 30%,#2a3040,#0b0d12)';
 show('result');if(isWin){confettiOn=true;parts=Array.from({length:150},()=>({x:Math.random()*640,y:-Math.random()*740,v:2+Math.random()*3,a:Math.random()*6,c:`hsl(${Math.random()*360},90%,60%)`}));confetti()}
 else rain()},700)}
function confetti(){if(!confettiOn)return;const c=$('confetti').getContext('2d');c.clearRect(0,0,640,740);
 for(const p of parts){p.y+=p.v;p.x+=Math.sin(p.a+=.05)*1.5;if(p.y>740)p.y=-10;c.fillStyle=p.c;c.fillRect(p.x,p.y,7,11)}requestAnimationFrame(confetti)}
function rain(){confettiOn=true;parts=Array.from({length:80},()=>({x:Math.random()*640,y:Math.random()*740,v:6+Math.random()*4}));
 (function r(){if(!confettiOn)return;const c=$('confetti').getContext('2d');c.clearRect(0,0,640,740);c.strokeStyle='#8fa8d855';c.lineWidth=1.5;
  for(const p of parts){p.y+=p.v;if(p.y>740)p.y=-20;c.beginPath();c.moveTo(p.x,p.y);c.lineTo(p.x-2,p.y+14);c.stroke()}requestAnimationFrame(r)})()}
let last=0;refreshPts();
</script></body></html>
'''

components.html(GAME_HTML, height=760, scrolling=False)
