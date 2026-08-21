from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
MARKER = '// === VD1 CUTFORM CORE RENDERER ============================================='

HEAD_INSERT = '''\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />\n<script src="./design/voidcut-design-system.js"></script>\n<meta name="voidcut-visual-phase" content="VD1">\n'''

HELPERS = r'''// === VD1 CUTFORM CORE RENDERER =============================================
const VD1_RENDERER_VERSION='VD1.0.0';
let vd1PaletteCache=null,vd1PaletteKey='';
function vd1Token(style,name,fallback){const value=style.getPropertyValue(name).trim();return value||fallback}
function vd1Palette(){
 const high=!!save?.settings?.highContrast,theme=document.documentElement.dataset.vcTheme||'paper',key=`${theme}|${high}`;
 if(vd1PaletteCache&&vd1PaletteKey===key)return vd1PaletteCache;
 if(high){vd1PaletteKey=key;vd1PaletteCache={theme:'contrast',bg:'#000000',surface:'#111111',surfaceRaised:'#181818',ink:'#ffffff',inkMuted:'#dddddd',line:'#ffffff',lineStrong:'#ffffff',accent:'#ffffff',accentAlt:'#ffffff',arena:'#101010',edge:'#ffffff',substrate:'#000000',nodeA:'#ffffff',nodeB:'#ffffff',nodeC:'#ffffff',danger:'#ffffff',success:'#ffffff',shadow:'#000000',onSubstrate:'#ffffff'};return vd1PaletteCache}
 const s=getComputedStyle(document.documentElement);vd1PaletteKey=key;vd1PaletteCache={theme,bg:vd1Token(s,'--vc-bg','#E9E4D8'),surface:vd1Token(s,'--vc-surface','#F7F3E8'),surfaceRaised:vd1Token(s,'--vc-surface-raised','#FFFCF3'),ink:vd1Token(s,'--vc-ink','#171714'),inkMuted:vd1Token(s,'--vc-ink-muted','#7C786F'),line:vd1Token(s,'--vc-line','#B7B0A2'),lineStrong:vd1Token(s,'--vc-line-strong','#171714'),accent:vd1Token(s,'--vc-accent','#EF593D'),accentAlt:vd1Token(s,'--vc-accent-alt','#2253C7'),arena:vd1Token(s,'--vc-arena','#F8F4E9'),edge:vd1Token(s,'--vc-arena-edge','#171714'),substrate:vd1Token(s,'--vc-substrate','#181816'),nodeA:vd1Token(s,'--vc-node-a','#171714'),nodeB:vd1Token(s,'--vc-node-b','#2253C7'),nodeC:vd1Token(s,'--vc-node-c','#EF593D'),danger:vd1Token(s,'--vc-danger','#CC3932'),success:vd1Token(s,'--vc-success','#26754C'),shadow:vd1Token(s,'--vc-shadow','#171714'),onSubstrate:vd1Token(s,'--vc-on-substrate','#F7F3E8')};return vd1PaletteCache
}
document.addEventListener('voidcut:themechange',()=>{vd1PaletteCache=null;vd1PaletteKey=''});
function vd1Hash01(n){n=(n|0)+0x6D2B79F5;n=Math.imul(n^(n>>>15),n|1);n^=n+Math.imul(n^(n>>>7),n|61);return((n^(n>>>14))>>>0)/4294967296}
function vd1Bounds(poly){let x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;for(const p of poly){x0=Math.min(x0,p.x);y0=Math.min(y0,p.y);x1=Math.max(x1,p.x);y1=Math.max(y1,p.y)}return{x0,y0,x1,y1,w:x1-x0,h:y1-y0}}
function vd1TextureMode(){return document.documentElement.dataset.vcTexture||'full'}
function vd1DrawGrain(poly,key=0){
 if(save.settings.highContrast||vd1TextureMode()==='off')return;const b=vd1Bounds(poly),tier=typeof performanceTier==='function'?performanceTier():0,mode=vd1TextureMode(),count=mode==='reduced'?18:tier>=2?16:tier===1?28:46,p=vd1Palette();ctx.save();pathPoly(poly);ctx.clip();ctx.fillStyle=p.edge;ctx.globalAlpha=mode==='reduced'?.025:.038;
 for(let i=0;i<count;i++){const x=b.x0+vd1Hash01(key*193+i*37+11)*b.w,y=b.y0+vd1Hash01(key*271+i*53+29)*b.h,s=.45+vd1Hash01(key*97+i*71+47)*.95;ctx.fillRect(Math.round(x),Math.round(y),s,s)}ctx.restore()
}
function vd1DrawPanel(poly,fill,stroke,shadow=true){const p=vd1Palette();ctx.save();if(shadow&&!save.settings.highContrast){ctx.save();ctx.translate(4,5);ctx.globalAlpha=.24;ctx.fillStyle=p.shadow;pathPoly(poly);ctx.fill();ctx.restore()}ctx.fillStyle=fill;pathPoly(poly);ctx.fill();ctx.strokeStyle=stroke;ctx.lineWidth=save.settings.highContrast?3:1.8;ctx.lineJoin='miter';ctx.stroke();ctx.restore()}
function vd1NodeColor(b){const p=vd1Palette();return b.type==='swift'?p.nodeB:b.type==='heavy'?p.nodeC:b.type==='pulse'?p.accent:p.nodeA}
function vd1Audit(){const design=window.VoidcutDesign?.audit?.()||null,p=vd1Palette();return Object.freeze({version:VD1_RENDERER_VERSION,theme:p.theme,designPass:design?.pass??null,substrate:p.substrate,arena:p.arena,edge:p.edge,physicalCuts:true,coreGlow:false,animatedBackdrop:false})}
try{Object.defineProperty(window,'VoidcutRenderer',{value:Object.freeze({version:VD1_RENDERER_VERSION,audit:vd1Audit}),enumerable:true,configurable:true})}catch{window.VoidcutRenderer={version:VD1_RENDERER_VERSION,audit:vd1Audit}}
'''

REPLACEMENTS = {
'arenaTheme': r'''function arenaTheme(){const p=vd1Palette();return{arena:p.arena,border:p.line,accent:p.accent,secondary:p.accentAlt,soft:p.line,grid:p.line,radial:p.accent,deep:p.substrate,mid:p.substrate,particle:p.onSubstrate}}''',
'drawBackdrop': r'''function drawBackdrop(now){
 const p=vd1Palette(),mode=vd1TextureMode();ctx.save();ctx.fillStyle=p.substrate;ctx.fillRect(0,0,W,H);
 if(!save.settings.highContrast&&mode!=='off'){
  const tier=performanceTier(),step=tier>=2?150:112;ctx.strokeStyle=p.onSubstrate;ctx.lineWidth=1;ctx.globalAlpha=mode==='reduced'?.035:.055;
  for(let y=28;y<H;y+=step){for(let x=28;x<W;x+=step){const s=((x+y)/step|0)%2?5:8;ctx.beginPath();ctx.moveTo(x-s,y);ctx.lineTo(x+s,y);ctx.moveTo(x,y-s);ctx.lineTo(x,y+s);ctx.stroke()}}
  ctx.globalAlpha=.10;ctx.strokeStyle=p.onSubstrate;for(const [x,y,sx,sy] of [[AX-13,AY-13,1,1],[AX+AW+13,AY-13,-1,1],[AX-13,AY+AH+13,1,-1],[AX+AW+13,AY+AH+13,-1,-1]]){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+sx*18,y);ctx.moveTo(x,y);ctx.lineTo(x,y+sy*18);ctx.stroke()}
 }
 ctx.restore()
}''',
'drawFieldZones': r'''function drawFieldZones(high=false){
 const p=vd1Palette();ctx.save();if(!high){ctx.save();ctx.translate(4,5);ctx.globalAlpha=.26;ctx.fillStyle=p.shadow;pathPoly(sim.arena.v);ctx.fill();ctx.restore()}ctx.fillStyle=p.substrate;pathPoly(sim.arena.v);ctx.fill();ctx.restore();
 for(const r of sim.regions){vd1DrawPanel(r.v,p.arena,p.line,false);if(!high){ctx.save();pathPoly(r.v);ctx.clip();ctx.globalAlpha=.026;ctx.fillStyle=(r.id%2)?p.accent:p.accentAlt;ctx.fillRect(AX,AY,AW,AH);ctx.restore();vd1DrawGrain(r.v,r.id||1)}}
 ctx.save();ctx.lineJoin='miter';ctx.lineCap='butt';ctx.strokeStyle=p.line;ctx.globalAlpha=high?1:.82;ctx.lineWidth=high?3:1;for(const r of sim.regions){pathPoly(r.v);ctx.stroke()}ctx.restore()
}''',
'drawPermanentDividers': r'''function drawPermanentDividers(high=false,now=0){
 const p=vd1Palette();ctx.save();ctx.lineCap='butt';ctx.lineJoin='miter';for(const e of renderCache.dividers){
  ctx.strokeStyle=p.substrate;ctx.lineWidth=high?8:7;ctx.beginPath();ctx.moveTo(e.a.x,e.a.y);ctx.lineTo(e.b.x,e.b.y);ctx.stroke();
  ctx.strokeStyle=p.edge;ctx.lineWidth=high?4:2.2;ctx.beginPath();ctx.moveTo(e.a.x,e.a.y);ctx.lineTo(e.b.x,e.b.y);ctx.stroke();
  if(!high){ctx.strokeStyle=p.accent;ctx.globalAlpha=.72;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(e.a.x,e.a.y);ctx.lineTo(e.b.x,e.b.y);ctx.stroke();ctx.globalAlpha=1}
  for(const a of [e.a,e.b]){ctx.fillStyle=p.substrate;ctx.fillRect(a.x-5,a.y-5,10,10);ctx.strokeStyle=p.edge;ctx.lineWidth=1.5;ctx.strokeRect(a.x-4.5,a.y-4.5,9,9);if(!high){ctx.fillStyle=p.accent;ctx.fillRect(a.x-1.5,a.y-1.5,3,3)}}
 }ctx.restore()
}''',
'drawBorderProgress': r'''function drawBorderProgress(pct){const p=vd1Palette();ctx.save();ctx.lineCap='butt';ctx.lineJoin='miter';ctx.lineWidth=save.settings.highContrast?6:4;ctx.strokeStyle=p.accent;const poly=sim.arena.v;let rem=renderCache.perimeter*pct;for(let i=0;i<poly.length;i++){if(rem<=0)break;const a=poly[i],b=poly[(i+1)%poly.length],l=Math.hypot(b.x-a.x,b.y-a.y),take=Math.min(l,rem),t=l>1e-9?take/l:0;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t);ctx.stroke();rem-=take}ctx.restore()}''',
'drawArenaSignatureFrame': r'''function drawArenaSignatureFrame(){
 if(save.settings.highContrast)return;const p=vd1Palette(),v=sim.arena.v,type=sim.arena?.type||'rectangle';ctx.save();ctx.lineCap='butt';ctx.lineJoin='miter';for(let i=0;i<v.length;i++){const q=v[i],a=v[(i-1+v.length)%v.length],b=v[(i+1)%v.length],ua=norm(sub(a,q)),ub=norm(sub(b,q)),len=type==='rectangle'?11:8;ctx.strokeStyle=i%2?p.accentAlt:p.accent;ctx.globalAlpha=.84;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(q.x+ua.x*4,q.y+ua.y*4);ctx.lineTo(q.x+ua.x*(4+len),q.y+ua.y*(4+len));ctx.moveTo(q.x+ub.x*4,q.y+ub.y*4);ctx.lineTo(q.x+ub.x*(4+len),q.y+ub.y*(4+len));ctx.stroke()}ctx.restore()
}''',
'drawCoreLightField': r'''function drawCoreLightField(){return}''',
'drawTrail': r'''function drawTrail(b,now){
 const p=vd1Palette(),style=save.cosmetics?.trail||'beam',speed=Math.hypot(b.vel.x,b.vel.y);if(speed<1e-6)return;const inv=1/speed,hx=b.vel.x*inv,hy=b.vel.y*inv,nx=-hy,ny=hx,col=vd1NodeColor(b),density=visualDensity(),len=Math.min(72,26+speed*.045)*(1-density*.18);ctx.save();ctx.lineCap='butt';ctx.strokeStyle=col;ctx.globalAlpha=save.settings.highContrast?.52:.34-density*.08;
 if(style==='echo'){for(let i=1;i<=2;i++){ctx.beginPath();ctx.arc(b.pos.x-hx*(b.r+12)*i,b.pos.y-hy*(b.r+12)*i,b.r*(.55-i*.10),0,Math.PI*2);ctx.lineWidth=1.2;ctx.stroke()}}
 else if(style==='sparks'){for(let i=1;i<=4;i++){const d=12+i*10,side=(i%2?1:-1)*(3+i);ctx.beginPath();ctx.moveTo(b.pos.x-hx*d+nx*side,b.pos.y-hy*d+ny*side);ctx.lineTo(b.pos.x-hx*(d+5)+nx*side,b.pos.y-hy*(d+5)+ny*side);ctx.lineWidth=i===1?2:1;ctx.stroke()}}
 else if(style==='ribbon'){for(const side of [-1,1]){ctx.beginPath();ctx.moveTo(b.pos.x-hx*len+nx*4*side,b.pos.y-hy*len+ny*4*side);ctx.lineTo(b.pos.x-hx*b.r+nx*2*side,b.pos.y-hy*b.r+ny*2*side);ctx.lineWidth=1.6;ctx.stroke()}}
 else if(style==='comet'){for(let i=1;i<=3;i++){const d=14+i*12;ctx.fillStyle=col;ctx.globalAlpha=.28-i*.055;ctx.fillRect(b.pos.x-hx*d-1.5,b.pos.y-hy*d-1.5,3,3)}}
 else{ctx.beginPath();ctx.moveTo(b.pos.x-hx*len,b.pos.y-hy*len);ctx.lineTo(b.pos.x-hx*(b.r+3),b.pos.y-hy*(b.r+3));ctx.lineWidth=2;ctx.stroke()}
 ctx.restore()
}''',
'drawBall': r'''function drawBall(b,now){
 const p=vd1Palette(),bump=b.bump||0,pulse=b.type==='pulse'?1+.035*Math.sin(b.pulsePhase):1,r=b.r*(1+bump*.055)*pulse,fill=vd1NodeColor(b),skin=save.cosmetics?.ball||'core',speed=Math.hypot(b.vel.x,b.vel.y),heading=speed>1e-8?Math.atan2(b.vel.y,b.vel.x):0;let danger=0;if(sim.cut&&b.region===sim.cut.region){const hitR=b.r+sim.cutWidth()*.5,d2=Math.min(pSegD2(b.pos,sim.cut.ca,sim.cut.o),pSegD2(b.pos,sim.cut.o,sim.cut.cb)),clear=Math.sqrt(Math.max(0,d2))-hitR;danger=Math.max(0,Math.min(1,(68-clear)/68))}
 ctx.save();ctx.translate(b.pos.x,b.pos.y);
 if(!save.settings.highContrast){ctx.save();ctx.translate(3,4);ctx.globalAlpha=.24;ctx.fillStyle=p.shadow;ctx.beginPath();ctx.arc(0,0,r*.94,0,Math.PI*2);ctx.fill();ctx.restore()}
 ctx.beginPath();ctx.arc(0,0,r*.92,0,Math.PI*2);if(skin==='hollow'){ctx.fillStyle=p.arena;ctx.fill();ctx.strokeStyle=fill;ctx.lineWidth=3;ctx.stroke()}else if(skin==='eclipse'){ctx.fillStyle=p.substrate;ctx.fill();ctx.strokeStyle=fill;ctx.lineWidth=2.4;ctx.stroke()}else{ctx.fillStyle=fill;ctx.fill();ctx.strokeStyle=p.edge;ctx.lineWidth=save.settings.highContrast?3:1.5;ctx.stroke()}
 const glyph=(skin==='hollow'||fill===p.edge)?fill:p.edge;ctx.strokeStyle=glyph;ctx.fillStyle=glyph;ctx.lineCap='butt';ctx.lineJoin='miter';ctx.globalAlpha=.96;
 if(b.type==='swift'){ctx.save();ctx.rotate(heading);ctx.beginPath();ctx.moveTo(r*.42,0);ctx.lineTo(-r*.18,r*.26);ctx.lineTo(-r*.06,0);ctx.lineTo(-r*.18,-r*.26);ctx.closePath();ctx.fill();ctx.restore()}
 else if(b.type==='heavy'){ctx.lineWidth=2;centeredPolygonPath(6,r*.38,Math.PI/6);ctx.stroke();ctx.fillRect(-2,-2,4,4)}
 else if(b.type==='pulse'){ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,0,r*.37,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.arc(0,0,r*.10,0,Math.PI*2);ctx.fill()}
 else{ctx.beginPath();ctx.arc(0,0,r*.17,0,Math.PI*2);ctx.fill();ctx.lineWidth=1.6;for(let i=0;i<3;i++){const a=i*Math.PI*2/3;ctx.beginPath();ctx.moveTo(Math.cos(a)*r*.34,Math.sin(a)*r*.34);ctx.lineTo(Math.cos(a)*r*.57,Math.sin(a)*r*.57);ctx.stroke()}}
 if(skin==='prism'){ctx.globalAlpha=.70;ctx.lineWidth=1.4;ctx.save();ctx.rotate(Math.PI/4);ctx.strokeRect(-r*.30,-r*.30,r*.60,r*.60);ctx.restore()}else if(skin==='reactor'){ctx.globalAlpha=.72;ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(0,0,r*.53,0,Math.PI*2);ctx.stroke();ctx.fillRect(-r*.05,-r*.58,r*.10,r*.20);ctx.fillRect(-r*.05,r*.38,r*.10,r*.20)}
 if(danger>.10){ctx.globalAlpha=.55+.4*danger;ctx.strokeStyle=p.danger;ctx.lineWidth=1.5+danger*1.4;ctx.setLineDash([5,5]);ctx.lineDashOffset=-now*.035;ctx.beginPath();ctx.arc(0,0,r+5+danger*3,0,Math.PI*2);ctx.stroke();ctx.setLineDash([])}
 if(speed>1e-8){ctx.save();ctx.rotate(heading);ctx.globalAlpha=.72;ctx.strokeStyle=glyph;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(r*1.08,0);ctx.lineTo(r*1.36,0);ctx.stroke();ctx.restore()}ctx.restore()
}''',
'drawCut': r'''function drawCut(c,now,high=false){
 const p=vd1Palette(),beamW=sim.cutWidth(),clearance=sim.currentCutClearance(),danger=clearance==null?0:Math.max(0,Math.min(1,(62-clearance)/62)),style=save.cosmetics?.cut||'pulse',seam=style==='blade'?beamW+9:style==='laser'?beamW+4:beamW+7;ctx.save();ctx.lineCap='butt';ctx.lineJoin='miter';const path=()=>{ctx.beginPath();ctx.moveTo(c.ca.x,c.ca.y);ctx.lineTo(c.o.x,c.o.y);ctx.lineTo(c.cb.x,c.cb.y)};
 path();ctx.strokeStyle=p.substrate;ctx.lineWidth=high?seam+3:seam;ctx.stroke();path();ctx.strokeStyle=p.edge;ctx.lineWidth=high?3.5:1.8;ctx.stroke();
 path();ctx.strokeStyle=danger>.32?p.danger:p.accent;ctx.globalAlpha=high?1:.90;ctx.lineWidth=style==='laser'?1:1.6;if(style==='rift')ctx.setLineDash([7,4]);ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1;
 if(danger>.18){path();ctx.strokeStyle=p.danger;ctx.globalAlpha=.35+.55*danger;ctx.lineWidth=2.2+danger*1.8;ctx.setLineDash([6,7]);ctx.lineDashOffset=-now*.04;ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1}
 const endpoint=(q,locked)=>{ctx.save();ctx.translate(q.x,q.y);ctx.fillStyle=locked?p.edge:p.arena;ctx.fillRect(-5,-5,10,10);ctx.strokeStyle=danger>.22?p.danger:p.accent;ctx.lineWidth=1.5;ctx.strokeRect(-5.5,-5.5,11,11);if(locked){ctx.fillStyle=p.accent;ctx.fillRect(-1.5,-1.5,3,3)}ctx.restore()};endpoint(c.ca,!!c.da);endpoint(c.cb,!!c.db);
 ctx.save();ctx.translate(c.o.x,c.o.y);ctx.strokeStyle=p.edge;ctx.lineWidth=1.3;ctx.strokeRect(-4,-4,8,8);ctx.fillStyle=p.accent;ctx.fillRect(-1.5,-1.5,3,3);ctx.restore();ctx.restore()
}''',
'drawCollapse': r'''function drawCollapse(f){
 if(f.age<0)return;const t=Math.min(1,f.age/f.dur),e=1-Math.pow(1-t,3),p=vd1Palette(),style=save.cosmetics?.collapse||'implode',fade=Math.max(0,1-t),center={x:W/2,y:AY+AH/2};let vx=f.c.x-center.x,vy=f.c.y-center.y,vl=Math.hypot(vx,vy);if(vl<1){const a=vd1Hash01(Math.round(f.c.x*7+f.c.y*11))*Math.PI*2;vx=Math.cos(a);vy=Math.sin(a);vl=1}vx/=vl;vy/=vl;const dir=(f.c.x+f.c.y)%2?1:-1;
 const drawPiece=(poly,ox,oy,rot,scale,alpha,fill=p.arena)=>{ctx.save();ctx.translate(f.c.x+ox,f.c.y+oy);ctx.rotate(rot);ctx.scale(scale,scale);ctx.translate(-f.c.x,-f.c.y);if(!save.settings.highContrast){ctx.save();ctx.translate(4+e*3,5+e*3);ctx.globalAlpha=.20*alpha;ctx.fillStyle=p.shadow;pathPoly(poly);ctx.fill();ctx.restore()}ctx.globalAlpha=alpha;ctx.fillStyle=fill;pathPoly(poly);ctx.fill();ctx.strokeStyle=p.edge;ctx.lineWidth=1.7;ctx.stroke();ctx.restore()};
 ctx.save();
 if(style==='shatter'||style==='fracture'){
  for(let i=0;i<f.v.length;i++){const a=f.v[i],b=f.v[(i+1)%f.v.length],tri=[f.c,a,b],mx=(a.x+b.x)/2,my=(a.y+b.y)/2,dx=mx-f.c.x,dy=my-f.c.y,dl=Math.hypot(dx,dy)||1,push=(12+(style==='shatter'?34:22)*e)*(i%2?1:.82),ox=dx/dl*push*e+vx*8*e,oy=dy/dl*push*e+vy*8*e,rot=dir*(i%2?1:-1)*e*(style==='shatter'?.12:.07);drawPiece(tri,ox,oy,rot,1,fade*(style==='shatter'?.92:.98),i%2?p.surface:p.arena)}
 }else{
  const push=style==='vacuum'?6:style==='dissolve'?30:18,scale=style==='implode'?Math.max(.08,1-e*.82):style==='vacuum'?Math.max(.18,1-e*.68):1-e*.10,rot=style==='dissolve'?dir*e*.055:dir*e*.025;drawPiece(f.v,vx*push*e,vy*push*e,rot,scale,fade);
  if(style==='dissolve'&&!save.settings.highContrast){const b=vd1Bounds(f.v),count=12+Math.round(e*20);ctx.save();pathPoly(f.v);ctx.clip();ctx.fillStyle=p.substrate;ctx.globalAlpha=e*.55;for(let i=0;i<count;i++){const x=b.x0+vd1Hash01(i*37+Math.round(f.c.x))*b.w,y=b.y0+vd1Hash01(i*71+Math.round(f.c.y))*b.h,s=1.5+e*2.4;ctx.fillRect(x-s/2,y-s/2,s,s)}ctx.restore()}
 }
 ctx.restore()
}''',
'drawDividerLock': r'''function drawDividerLock(l){
 if(l.age<0)return;const p=vd1Palette(),t=Math.min(1,l.age/l.dur),build=Math.min(1,t/.62),fade=Math.min(1,(1-t)*4),dx=l.b.x-l.a.x,dy=l.b.y-l.a.y,pa={x:l.a.x+dx*.5*build,y:l.a.y+dy*.5*build},pb={x:l.b.x-dx*.5*build,y:l.b.y-dy*.5*build};ctx.save();ctx.globalAlpha=fade;ctx.lineCap='butt';
 ctx.strokeStyle=p.substrate;ctx.lineWidth=7;ctx.beginPath();ctx.moveTo(l.a.x,l.a.y);ctx.lineTo(l.b.x,l.b.y);ctx.stroke();ctx.strokeStyle=p.edge;ctx.lineWidth=2.4;ctx.beginPath();ctx.moveTo(l.a.x,l.a.y);ctx.lineTo(pa.x,pa.y);ctx.moveTo(l.b.x,l.b.y);ctx.lineTo(pb.x,pb.y);ctx.stroke();ctx.strokeStyle=p.accent;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(l.a.x,l.a.y);ctx.lineTo(pa.x,pa.y);ctx.moveTo(l.b.x,l.b.y);ctx.lineTo(pb.x,pb.y);ctx.stroke();
 for(const q of [l.a,l.b,pa,pb]){ctx.fillStyle=p.arena;ctx.fillRect(q.x-4,q.y-4,8,8);ctx.strokeStyle=p.edge;ctx.lineWidth=1.3;ctx.strokeRect(q.x-4.5,q.y-4.5,9,9)}ctx.restore()
}''',
'drawFeedbackBurst': r'''function drawFeedbackBurst(b){const p=vd1Palette(),t=Math.min(1,b.age/b.dur),ease=1-Math.pow(1-t,3),col=b.kind==='death'?p.danger:b.kind==='close'||b.kind==='milestone'?p.accentAlt:p.accent,base=b.kind==='death'?110:b.kind==='milestone'?150:b.kind==='massive'?130:b.kind==='clear'?115:78;ctx.save();ctx.translate(b.x,b.y);ctx.rotate(b.angle||0);ctx.strokeStyle=col;const rays=Math.max(4,Math.ceil(b.rays*.46));for(let i=0;i<rays;i++){const a=i*Math.PI*2/rays,r1=14*ease,r2=base*b.scale*ease;ctx.globalAlpha=(1-t)*(i%2===0?.72:.42);ctx.lineWidth=i%3===0?3:1.5;ctx.beginPath();ctx.moveTo(Math.cos(a)*r1,Math.sin(a)*r1);ctx.lineTo(Math.cos(a)*r2,Math.sin(a)*r2);ctx.stroke()}ctx.restore()}''',
'drawRing': r'''function drawRing(r){if(r.age<0)return;const p=vd1Palette(),t=Math.min(1,r.age/r.dur),rad=10+(r.max-10)*(1-Math.pow(1-t,2)),col=r.kind==='death'?p.danger:r.kind==='close'||r.kind==='split'?p.accentAlt:r.kind==='clear'?p.edge:p.accent;ctx.save();ctx.globalAlpha=(1-t)*(r.kind==='close'?.62:.72);ctx.beginPath();ctx.arc(r.x,r.y,rad,0,Math.PI*2);ctx.strokeStyle=col;ctx.lineWidth=(r.kind==='massive'?3:r.kind==='close'?2.6:2)*(1-t)+.7;ctx.stroke();ctx.restore()}''',
'drawSpark': r'''function drawSpark(q){const p=vd1Palette(),t=q.age/q.dur,s=q.size*(1-t*.55),col=q.death?p.danger:q.hot?p.edge:p.accent;ctx.save();ctx.translate(q.x,q.y);ctx.rotate(Math.PI/4);ctx.globalAlpha=1-t;ctx.fillStyle=col;ctx.fillRect(-s/2,-s/2,s,s);ctx.restore()}''',
'drawScreenImpact': r'''function drawScreenImpact(now,high=false){const p=vd1Palette();if(sim.cut&&!transition){const clear=sim.currentCutClearance(),d=clear==null?0:Math.max(0,Math.min(1,(34-clear)/34));if(d>.45){ctx.save();ctx.strokeStyle=p.danger;ctx.globalAlpha=.12+((d-.45)/.55)*.24;ctx.lineWidth=2+d*2;ctx.strokeRect(8,8,W-16,H-16);ctx.restore()}}if(dangerPulse>.01){ctx.save();ctx.globalAlpha=Math.min(.22,dangerPulse*.16);ctx.strokeStyle=p.danger;ctx.lineWidth=4;ctx.strokeRect(9,9,W-18,H-18);ctx.restore()}if(deathImpact>.01&&lastHit){const t=1-Math.min(1,deathImpact/1.25),r=24+118*(1-Math.pow(1-t,3));ctx.save();ctx.translate(lastHit.x,lastHit.y);ctx.globalAlpha=Math.min(.8,deathImpact*.6);ctx.strokeStyle=p.danger;ctx.lineWidth=3;ctx.strokeRect(-r,-r,r*2,r*2);ctx.fillStyle=p.danger;ctx.fillRect(-30,-2,60,4);ctx.fillRect(-2,-30,4,60);ctx.restore()}}''',
'drawTransition': r'''function drawTransition(now){
 const p=vd1Palette(),t=Math.max(0,Math.min(1,(now-transitionStart)/transitionDuration)),r=transitionResult,enter=Math.min(1,t/.18),exit=Math.max(0,Math.min(1,(t-.82)/.18)),alpha=enter*(1-exit),w=480,h=158,x=(W-w)/2,y=H/2-h/2;ctx.save();ctx.globalAlpha=.34*alpha;ctx.fillStyle=p.substrate;ctx.fillRect(AX,AY,AW,AH);ctx.globalAlpha=alpha;if(!save.settings.highContrast){ctx.fillStyle=p.shadow;ctx.fillRect(x+6,y+7,w,h)}ctx.fillStyle=p.surfaceRaised;ctx.fillRect(x,y,w,h);ctx.strokeStyle=p.edge;ctx.lineWidth=2;ctx.strokeRect(x,y,w,h);ctx.fillStyle=p.accent;ctx.fillRect(x,y,w,6);ctx.textAlign='left';ctx.fillStyle=p.inkMuted;ctx.font='700 11px system-ui,sans-serif';ctx.fillText('CHAMBER CUT COMPLETE',x+24,y+34);ctx.fillStyle=p.ink;ctx.font='800 34px system-ui,sans-serif';ctx.fillText(r?.grade?`${r.grade} MASTERY`:'FIELD CLEARED',x+24,y+76);ctx.fillStyle=p.inkMuted;ctx.font='600 12px system-ui,sans-serif';const pct=Number.isFinite(r?.pct)?`${r.pct.toFixed(1)}% REMOVED`:Number.isFinite(r?.removedPct)?`${r.removedPct.toFixed(1)}% REMOVED`:'';ctx.fillText([pct,r?.tier||''].filter(Boolean).join('  /  '),x+24,y+108);ctx.fillStyle=p.accentAlt;ctx.fillRect(x+24,y+128,Math.max(24,(w-48)*Math.min(1,t/.78)),4);ctx.restore()
}''',
'draw': r'''function draw(now){
 const high=!!save.settings.highContrast,large=!!save.settings.largeUI,mag=UI_PALETTES[save.settings.colorTheme]?.b||'#FF2DAA',gameplayVisible=state==='play'||state==='replay'||state==='dying',p=vd1Palette();ctx.clearRect(0,0,W,H);ctx.fillStyle=p.substrate;ctx.fillRect(0,0,W,H);drawBackdrop(now);if(gameplayVisible){drawGameplayWordmark();const cleared=Math.min(100,Math.round(sim.removed/sim.area*100));if(tutorialMode){ctx.save();ctx.textAlign='left';ctx.fillStyle=p.accentAlt;ctx.font='800 9px system-ui,sans-serif';ctx.fillText('TRAINING',82,72);ctx.fillStyle=C.text;ctx.font='800 23px Bahnschrift,system-ui,sans-serif';const lessonTitle=tutorialStage===1?'COLLAPSE':tutorialStage===2?'DIVIDER':tutorialStep==='setupDivider'?'SETUP':'USE THE SETUP';ctx.fillText(`LESSON ${tutorialStage}/3  •  ${lessonTitle}`,82,101);ctx.textAlign='right';ctx.fillStyle=C.muted;ctx.font='700 9px system-ui,sans-serif';ctx.fillText('NO SCORE • PRACTICE',650,86);ctx.strokeStyle=p.line;ctx.beginPath();ctx.moveTo(40,132.5);ctx.lineTo(680,132.5);ctx.stroke();ctx.restore()}else drawCompactHud(cleared,large,mag);const cam=motionCamera(now);ctx.save();ctx.translate(W/2+cam.x,H/2+cam.y);ctx.rotate(cam.roll);ctx.scale(cam.scale,cam.scale);ctx.translate(-W/2,-H/2);drawFieldZones(high);drawModifierField(now);drawMilestoneField(now);for(const f of fx.collapses)drawCollapse(f);drawPermanentDividers(high,now);for(const l of fx.locks)drawDividerLock(l);if(save.settings.trails){for(const b of sim.balls)drawTrail(b,now)}for(const b of sim.balls)drawBall(b,now);if(tutorialMode)drawTutorialGuide(now);if(aim){const d=sub(aim.p,aim.o),distance=len(d);if(distance>=2){const q=sim.preview(aim.region,aim.o,d);if(q){const valid=distance>=minSwipe(),col=high?(valid?'#fff':'#fff'):(valid?p.accent:p.line);ctx.save();ctx.setLineDash([10,8]);ctx.lineDashOffset=-(now*.022)%18;ctx.beginPath();ctx.moveTo(q.a.x,q.a.y);ctx.lineTo(q.b.x,q.b.y);ctx.strokeStyle=col;ctx.lineWidth=high?4:2;ctx.stroke();ctx.setLineDash([]);ctx.beginPath();ctx.arc(aim.o.x,aim.o.y,minSwipe(),0,Math.PI*2);ctx.strokeStyle=col;ctx.globalAlpha=valid?.72:.42;ctx.lineWidth=1;ctx.stroke();ctx.globalAlpha=1;ctx.fillStyle=col;ctx.fillRect(aim.o.x-(valid?3:2),aim.o.y-(valid?3:2),valid?6:4,valid?6:4);ctx.restore()}}}if(sim.cut)drawCut(sim.cut,now,high);ctx.lineWidth=high?4:2.4;ctx.strokeStyle=p.edge;ctx.globalAlpha=1;pathPoly(sim.arena.v);ctx.stroke();drawBorderProgress(sim.progress());drawArenaSignatureFrame();for(const b of fx.bursts)drawFeedbackBurst(b);for(const r of fx.rings)drawRing(r);for(const q of fx.sparks)drawSpark(q);for(const q of fx.pops)drawPop(q);ctx.restore();drawModifierBadge();drawMilestoneBadge();drawModifierBriefing();drawMilestoneBriefing();if(transition)drawTransition(now)}if(gameplayVisible&&!save.settings.reducedMotion&&flash>.01){ctx.save();ctx.globalAlpha=Math.min(.055,flash*.034);ctx.fillStyle=p.accent;ctx.fillRect(0,0,W,H);ctx.restore()}if(gameplayVisible&&deathFlash>.01){ctx.save();ctx.globalAlpha=Math.min(.16,deathFlash*.14);ctx.fillStyle=p.danger;ctx.fillRect(0,0,W,H);ctx.restore()}if(gameplayVisible)drawScreenImpact(now,high)}''',
}


def replace_function(text: str, name: str, replacement: str) -> str:
    pattern = re.compile(rf'(?ms)^function {re.escape(name)}\([^\n]*\)\{{.*?(?=^function [A-Za-z_$][\w$]*\()')
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f'{name}: expected exactly one top-level function, found {len(matches)}')
    return text[:matches[0].start()] + replacement.rstrip() + '\n' + text[matches[0].end():]


def main() -> None:
    text = INDEX.read_text(encoding='utf-8')
    original = text

    if 'voidcut-design-system.css' not in text:
        text = text.replace('</head>', HEAD_INSERT + '</head>', 1)
    elif 'voidcut-visual-phase' not in text:
        text = text.replace('</head>', '<meta name="voidcut-visual-phase" content="VD1">\n</head>', 1)

    if MARKER not in text:
        anchor = 'const ARENA_THEMES={'
        if anchor not in text:
            raise RuntimeError('ARENA_THEMES anchor missing')
        text = text.replace(anchor, HELPERS + '\n' + anchor, 1)

    for name, replacement in REPLACEMENTS.items():
        text = replace_function(text, name, replacement)

    if text == original:
        print('VD1 patch already applied; no changes.')
        return

    INDEX.write_text(text, encoding='utf-8')
    print(f'VD1 renderer patch applied: {len(original)} -> {len(text)} bytes')
    print('Replaced:', ', '.join(REPLACEMENTS))


if __name__ == '__main__':
    main()
