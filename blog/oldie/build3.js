(function(src, L){
// L: language pack. src: original post HTML (tistory editor content)
const d=new DOMParser().parseFromString('<div id=r>'+src+'</div>','text/html');
const r=d.getElementById('r');
const kids=[...r.children];
const T=e=>(e.textContent||'').replace(/\s+/g,' ').trim();
const H2=kids.filter(e=>e.tagName==='H2');
const H3=kids.filter(e=>e.tagName==='H3');
const idx=e=>kids.indexOf(e);
const html=e=>e?e.outerHTML:'';
const range=(a,b)=>kids.slice(a,b);
const isTok=(e,n)=>e&&e.innerHTML.includes(n);
const svgURI=s=>'url("data:image/svg+xml,'+encodeURIComponent(s)+'")';
const wavePath='M0 11 Q 25 0 50 11 T 100 11 T 150 11 T 200 11 T 250 11 T 300 11 T 350 11 T 400 11 T 450 11 T 500 11 T 550 11 T 600 11 T 650 11 T 700 11 T 750 11 T 800 11 T 850 11 T 900 11 T 950 11 T 1000 11 T 1050 11 T 1100 11 T 1150 11 T 1200 11';
const wave=c=>svgURI(`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 22' preserveAspectRatio='none'><path d='${wavePath}' fill='none' stroke='${c}' stroke-width='1.6' vector-effect='non-scaling-stroke'/></svg>`);
const capPath='M30 2 l3.1 4.2 4.9-1.9 1.2 5.1 5.2.1-.4 5.2 4.9 1.8-2.1 4.8 4 3.3-3.3 4 3.3 4-4 3.3 2.1 4.8-4.9 1.8.4 5.2-5.2.1-1.2 5.1-4.9-1.9L30 58l-3.1-4.2-4.9 1.9-1.2-5.1-5.2-.1.4-5.2-4.9-1.8 2.1-4.8-4-3.3 3.3-4-3.3-4 4-3.3-2.1-4.8 4.9-1.8-.4-5.2 5.2-.1 1.2-5.1 4.9 1.9z';
const cap=c=>svgURI(`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'><path fill='${c}' d='${capPath}'/></svg>`);
const dusk=svgURI(`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 60' preserveAspectRatio='none'><path d='M0 0 H1200 V22 Q1140 52 1080 30 T960 30 T840 30 T720 30 T600 30 T480 30 T360 30 T240 30 T120 30 T0 30 Z' fill='#F7F3EC'/></svg>`);

// --- pieces ---
const disc=kids[0];                         // 제휴표기 이미지
const note0=kids.find(e=>e.classList&&e.classList.contains('pg-note'));
const langDiv=kids.find(e=>e.tagName==='DIV'&&e.querySelectorAll('a').length>=2&&idx(e)<4);
const wallP=kids.find(e=>isTok(e,'02_wall'));
const iH2a=idx(H2[0]), iH2b=idx(H2[1]), iH2c=idx(H2[2]);
const pre=range(0,iH2a).filter(e=>e!==disc&&e!==langDiv&&e!==note0);   // poster, meta, hook, ticket, map...
const c1body=range(iH2a+1,iH2b).filter(e=>e!==wallP);
const i3=idx(H3[0]);
const c2intro=range(iH2b+1,i3);
const groups=H3.map((h,k)=>{const a=idx(h), b=k<H3.length-1?idx(H3[k+1]):iH2c;return range(a,b);});
const tail=range(iH2c+1,kids.length);
const strip=e=>T(e).replace(/^.*?·\s*\d+\s*/,'');

// lang pills
const langA=langDiv?[...langDiv.querySelectorAll('a')]:[];
const pills=L.pills.map((x,i)=>`<a class="${i==L.self?'on':''}" href="https://aurum41.tistory.com/${x[1]}">${x[0]}</a>`).join('');const _old=langA.map(a=>{const on=/\/5\b/.test(a.getAttribute('href')||'')||a.textContent.includes(L.selfLangHint);return `<a class="${on?'on':''}" href="${a.getAttribute('href')}">${T(a).replace(/[🇰🇷🇬🇧🇯🇵]/gu,'').trim()}</a>`}).join('');

const badge=(n,c,tc)=>`<section class="ag-cap"><section class="ag-capn">${n}</section></section>`;
const chap=(id,n,kick,title,night)=>`<header class="ag-chap">${badge(n,night?'#D9A92E':'#2B4C9B',night?'#0F2236':'#fff')}<span class="ag-kicker"${night?' style="color:#D9A92E"':''}>${kick}</span><section class="ag-h2" role="heading" aria-level="2">${title}</section></header>`;

// works
const work=(g,k)=>{
  const h=g[0]; const ht=T(h); const m=ht.match(/^(\d+)\s*·\s*(.+?)\s+([A-Z][A-Za-z ,'’]+)$/);
  const no=m?m[1]:String(k+1).padStart(2,'0'), ttl=m?m[2]:ht, en=m?m[3]:'';
  const rest=g.slice(1);
  const best=rest.find(e=>/^★/.test(T(e)));
  const toks=rest.filter(e=>/\[##_Image/.test(e.innerHTML));
  const art=toks[0], pair=toks[1];
  const other=rest.filter(e=>e!==best&&e!==art&&e!==pair);
  const q=other.find(e=>/^["“]/.test(T(e)));
  const spec=other.find(e=>/×\d/.test(T(e))&&T(e).length<70);
  const vid=other.find(e=>/^▶/.test(T(e)));
  const capP=other.find(e=>e!==q&&e!==spec&&e!==vid&&T(e).length);
  const extra=other.filter(e=>![q,spec,vid,capP].includes(e));
  const head=`${best&&k!==5?`<span class="ag-best">${T(best)}</span>`:''}<div class="ag-workh"><span class="no">${no}</span><section class="ag-h3" role="heading" aria-level="3">${ttl}</section><small>${en.toUpperCase()}</small></div>`;
  if(k===0){ // webtoon strip
    return `<section class="ag-work ag-strip">${head}<div class="ag-art">${html(art)}</div><div class="g1"></div>${spec?`<p class="ag-capc">${T(spec)}</p>`:''}<div class="g2"></div>${q?`<p class="ag-say">${q.innerHTML}</p>`:''}<div class="g2"></div><div class="ag-pairw">${html(pair)}</div>${capP?`<p class="ag-capc">${capP.innerHTML}</p>`:''}${extra.map(html).join('')}<div class="ag-vid">${html(vid)}</div><div class="g3"></div></section>`;
  }
  return `<section class="ag-work ag-duo ${k%2?'ag-l':'ag-r'}">${head}<div class="ag-duog"><div class="ag-art">${html(art)}</div><div class="ag-pairw">${html(pair)}</div></div>${q?`<blockquote class="ag-wq">${q.innerHTML}</blockquote>`:''}${spec?`<p class="ag-capc">${T(spec)}</p>`:''}${capP?`<p class="ag-capc">${capP.innerHTML}</p>`:''}${extra.map(html).join('')}<div class="ag-vid">${html(vid)}</div></section>`;
};
const works=groups.map(work);
const breathIdx=groups.findIndex(g=>g.some(e=>e.classList&&e.classList.contains('pg-say')));
// pull out the 쉬어가기 pg-say (it sits inside group 3's tail)
let breath='';
groups.forEach((g,k)=>g.forEach(e=>{if(e.classList&&e.classList.contains('pg-say')&&k<5){breath=`<aside class="ag-breath"><p>${e.innerHTML}</p></aside>`;}}));
// rebuild works without pg-say inside extra
const cleanWorks=groups.map((g,k)=>work(g.filter(e=>!(e.classList&&e.classList.contains('pg-say'))),k));

const h2title=e=>{const t=T(e);return t.replace(/^.*?·\s*\d+\s*/,'')};
const pullTxt=(groups[0].find(e=>/^["“]/.test(T(e)))||{textContent:''}).textContent.replace(/^["“]|["”].*$/g,'').trim();

const css=`
body:has(.ag-c-oldie),#wrap:has(.ag-c-oldie),#container:has(.ag-c-oldie),.main:has(.ag-c-oldie),.area-main:has(.ag-c-oldie),.area-view:has(.ag-c-oldie){background:#F7F3EC!important}
body:has(.ag-c-oldie) .article-header{display:none!important}
.ag-discband{font-size:13px!important;line-height:1.6;color:#555;background:#fff;border:1px solid #e3ddd2;border-radius:8px;padding:10px 16px;margin:0 0 14px;text-align:center}
.ag-discimg{display:none!important}
.main:has(.ag-c-oldie),#container:has(.ag-c-oldie),.area-main:has(.ag-c-oldie),.area-view:has(.ag-c-oldie),.article-view:has(.ag-c-oldie){padding-top:0!important;margin-top:0!important}
.article-view:has(.ag-c-oldie){display:flex!important;flex-direction:column}
.article-view:has(.ag-c-oldie)>*{order:1}
.article-view:has(.ag-c-oldie)>ins.adsbygoogle,.article-view:has(.ag-c-oldie)>.revenue_unit_wrap{order:9}

.main:has(.ag-c-oldie){display:block!important;max-width:1140px}
.main:has(.ag-c-oldie) .area-main{width:100%!important;max-width:none!important;float:none!important}
.main:has(.ag-c-oldie) .area-aside{width:100%!important;max-width:none!important;float:none!important;margin-top:120px;border-top:1px solid #e3ddd2;padding-top:40px}
.area-view:has(.ag-c-oldie),.article-view:has(.ag-c-oldie),.contents_style:has(.ag-c-oldie){width:100%!important;max-width:none!important;background:transparent!important}
.ag-c-oldie{--m:#2B4C9B;--s:#D9A92E;--n:#0F2236;--soft:#E9EEF7;color:#2b2b2b;font-family:"Noto Sans KR","Noto Sans JP",sans-serif;font-size:16px;line-height:2;letter-spacing:.4px;word-break:keep-all;max-width:1140px;margin:0 auto}
.ag-c-oldie img{max-width:100%;height:auto}
.ag-c-oldie figure{margin:0}
.ag-c-oldie .ag-col{max-width:700px;margin:0 auto}
.ag-pg{position:fixed;top:0;left:0;height:3px;width:0;background:#2B4C9B;z-index:9999}
.ag-toc{position:fixed;right:22px;top:50%;transform:translateY(-50%);z-index:9998;display:flex;flex-direction:column;gap:14px}
.ag-toc button{font-family:inherit;cursor:pointer;border:0!important;background:none!important;padding:0!important;border-radius:0!important;box-shadow:none!important;min-width:0!important;width:auto!important;height:auto!important;display:flex;align-items:center;gap:10px;justify-content:flex-end;text-decoration:none!important;font-size:12px;color:#8a8a8a!important;line-height:1.4}
.ag-toc button label{opacity:0;transition:opacity .2s;cursor:pointer}.ag-toc button:hover label,.ag-toc button.on label{opacity:1}
.ag-toc button i{width:9px;height:9px;border-radius:50%;border:1.5px solid #8a8a8a;display:block}
.ag-toc button.on i{background:#2B4C9B;border-color:#2B4C9B}.ag-toc button.on{color:#2B4C9B!important}
.ag-lang{display:flex;gap:8px;justify-content:center;padding:6px 0 0}
.ag-lang a{box-shadow:none!important;font-size:13px;text-decoration:none!important;padding:7px 16px;border:1px solid #e3ddd2;border-radius:999px;background:#fff;color:#22252b!important;line-height:1.5}
.ag-lang a.on{background:#22252b;color:#fff!important;border-color:#22252b}
.ag-cover{display:grid;grid-template-columns:2fr 1fr;gap:24px;margin-top:22px;align-items:end}
.ag-cover .ph img{width:100%;aspect-ratio:4/3;object-fit:cover}
.ag-kicker{font-size:12px;letter-spacing:2.4px;color:#2B4C9B;font-weight:600;display:block}
.ag-cover h1{font-family:"Noto Serif KR","Noto Serif JP",serif;font-weight:400;font-size:42px;line-height:1.32;letter-spacing:-.4px;margin:14px 0 18px;color:#22252b;border:0;padding:0}
.ag-cover .dek{font-size:16px;line-height:2;color:#555;margin:0}
.ag-cover .meta{font-size:12px;color:#8a8a8a;margin-top:18px;letter-spacing:.6px}
.ag-wave{display:block;height:22px;margin:8px 0 0;background:${wave('#2B4C9B')} center/100% 100% no-repeat}
.ag-sum{margin:40px auto 0;max-width:700px;border-top:1px solid #22252b;border-bottom:1px solid #e3ddd2;padding:22px 0}
.ag-sum ol{margin:0;padding:0;list-style:none;counter-reset:s}
.ag-sum li{counter-increment:s;display:grid;grid-template-columns:34px 1fr;font-size:16px;line-height:1.9;margin:4px 0}
.ag-sum li::before{content:counter(s,decimal-leading-zero);font-family:"Noto Serif KR",serif;color:#2B4C9B}
.ag-sum .date{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:14px;font-size:13px;color:#8a8a8a}
.ag-sum .date b{color:#22252b;font-weight:500}
.ag-chap{padding:120px 0 40px;max-width:700px;margin:0 auto}
.ag-cap{width:58px;height:58px;background:center/contain no-repeat;display:flex;align-items:center;justify-content:center;margin-bottom:22px}
.ag-cap{background-image:${cap('#2B4C9B')}!important}.ag-night .ag-cap{background-image:${cap('#D9A92E')}!important}.ag-capn{color:#fff;line-height:1;font-family:"Noto Serif KR",serif;font-size:20px;font-weight:400}
.ag-h2{font-family:"Noto Serif KR","Noto Serif JP",serif!important;font-weight:400!important;font-size:34px!important;line-height:1.4!important;margin:10px 0 0!important;color:#22252b;letter-spacing:-.3px;border:0!important;padding:0!important;background:none!important}
.ag-body{max-width:700px;margin:0 auto}
.ag-pull{max-width:820px;margin:72px auto;padding-left:28px;border-left:2px solid #D9A92E}
.ag-pull q{font-family:"Noto Serif KR","Noto Serif JP",serif;font-size:28px;line-height:1.6;color:#22252b;quotes:none;display:block}
.ag-pull cite{display:block;font-style:normal;font-size:13px;color:#8a8a8a;margin-top:14px}
.ag-work{max-width:700px;margin:96px auto 0}
.ag-workh{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 14px;margin:0 0 14px}
.ag-workh .no{font-family:"Noto Serif KR",serif;font-size:44px;color:#2B4C9B;line-height:1}
.ag-workh .ag-h3{margin:0!important;font-family:"Noto Serif KR","Noto Serif JP",serif!important;font-weight:400!important;font-size:24px!important;color:#22252b;border:0!important;padding:0!important;background:none!important}
.ag-workh small{font-size:13px;color:#8a8a8a;letter-spacing:.6px}
.ag-best{display:inline-block;font-size:12px;color:#2B4C9B;border:1px solid #2B4C9B;padding:2px 10px;border-radius:999px;margin-bottom:10px;line-height:1.6}
.ag-strip{display:flex;flex-direction:column;align-items:center}
.ag-strip .ag-workh{align-self:stretch}
.ag-strip .ag-art{width:82%}.ag-strip .ag-pairw{width:62%}
.ag-strip .g1{height:16px}.ag-strip .g2{height:64px}.ag-strip .g3{height:120px}
.ag-say{font-family:"Noto Serif KR","Noto Serif JP",serif;font-size:18px;line-height:1.7;color:#22252b;text-align:center;max-width:460px;margin:0}
.ag-capc{font-size:13px;line-height:1.7;color:#8a8a8a;text-align:center;margin:10px 0 0}
.ag-duog{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.ag-duo.ag-l .ag-duog{grid-template-columns:1.2fr .8fr}.ag-duo.ag-r .ag-duog{grid-template-columns:.8fr 1.2fr}
.ag-wq{font-family:"Noto Serif KR","Noto Serif JP",serif;font-size:19px;line-height:1.8;color:#22252b;border-left:2px solid #D9A92E;padding:0 0 0 18px;margin:28px 0 8px;background:none}
.ag-vid{text-align:center;margin-top:18px}
.ag-vid a{display:inline-flex;align-items:center;gap:8px;text-decoration:none!important;font-size:14px;padding:10px 20px;border-radius:999px;background:#fff;color:#22252b!important;border:1px solid #22252b}
.ag-breath{max-width:700px;margin:96px auto;padding:34px 24px;background:#E9EEF7;text-align:center}
.ag-breath p{font-family:"Noto Serif KR","Noto Serif JP",serif;font-size:19px;line-height:1.8;color:#22252b;margin:0}
.ag-dusk{position:relative;height:260px;background:#0F2236;margin:120px calc(50% - 50vw) 0;width:auto}
.ag-dusk::before{content:"";position:absolute;top:-1px;left:0;right:0;height:60px;background:${dusk} center/100% 100% no-repeat}
.ag-duskl{text-align:center;font-family:"Noto Serif KR",serif;font-size:15px;color:#9aa8bb;padding-top:150px;letter-spacing:1px;margin:0}
.ag-night{position:relative;background:#0F2236;color:#dfe5ee;padding:10px 0 120px;margin:0 calc(50% - 50vw)}
.ag-night>*{max-width:700px;margin-left:auto;margin-right:auto}
.ag-night .ag-chap{padding-top:20px}
.ag-night .ag-h2,.ag-night .ag-workh .ag-h3,.ag-night .ag-say,.ag-night .ag-wq,.ag-night p{color:#fff}
.ag-night .ag-capn{color:#0F2236!important}.ag-night .ag-capc{color:#8fa0b5}.ag-night .ag-work{margin-top:40px}
.ag-c-oldie .ag-tail{max-width:700px;margin:0 auto}
@media (max-width:1180px){.ag-toc{right:8px}}
@media (max-width:820px){
 .ag-cover{grid-template-columns:1fr}.ag-cover h1{font-size:30px}
 .ag-chap{padding:88px 0 28px}.ag-h2{font-size:26px!important}
 .ag-pull{margin:52px 0;padding-left:18px}.ag-pull q{font-size:21px}
 .ag-duog,.ag-duo.ag-l .ag-duog,.ag-duo.ag-r .ag-duog{grid-template-columns:1fr 1fr;gap:10px}
 .ag-strip .ag-art{width:100%}.ag-strip .ag-pairw{width:78%}
 .ag-toc{right:auto;left:0;top:auto;bottom:0;transform:none;flex-direction:row;width:100%;justify-content:center;gap:0;background:rgba(247,243,236,.94);border-top:1px solid #e3ddd2;padding:8px 4px}
 .ag-toc button{font-family:inherit;cursor:pointer;flex:1;justify-content:center;flex-direction:column;gap:3px;font-size:10.5px}.ag-toc button label{opacity:1}
 .ag-dusk,.ag-night{margin-left:-20px;margin-right:-20px}
 .ag-night>*{padding:0 20px}
}
@media (max-width:1024px){.ag-night::before{content:"";position:absolute;inset:0;background:#0F2236;z-index:-1}.ag-night{z-index:0}}
`;

const L2=L;
const out=`<div class="ag-c-oldie"><style>${css}</style>
<div class="ag-pg" id="agpg"></div>
<nav class="ag-toc" id="agtoc">${L.toc.map((t,i)=>`<button type="button" data-t="c${i}"><label>${t}</label><i></i></button>`).join("")}</nav>
<section class="ag-discband">${L.disc||(()=>{const k=[...kids].reverse().find(e=>/commission|手数料|アフィリエイト|affiliate/i.test(T(e))&&T(e).length<400);return k?k.innerHTML:''})()}</section><section class="ag-discimg">${html(disc)}</section>
<nav class="ag-lang">${pills}</nav>
<section id="c0" class="ag-cover"><div class="ph">${html(wallP)}</div><div class="tx"><span class="ag-kicker">${L.kicker}</span><h1>${L.h1}</h1><p class="dek">${L.dek}</p><div class="meta">${L.meta}</div></div></section>
<div class="ag-wave"></div>
<section class="ag-sum"><ol>${L.sum.map(s=>`<li>${s}</li>`).join('')}</ol><div class="date"><span>${L.dateEx}</span><span>${L.dateChk}</span></div></section>
<div class="ag-body">${html(note0)}${pre.map(html).join('')}</div>
<section id="c1">${chap('c1','01',L.k1,h2title(H2[0]))}<div class="ag-body">${c1body.map(html).join('')}</div></section>
<section id="c2">${chap('c2','02',L.k2,h2title(H2[1]))}<div class="ag-body">${c2intro.map(html).join('')}</div>
<blockquote class="ag-pull"><q>${pullTxt}</q><cite>${L.cite}</cite></blockquote>
${cleanWorks.slice(0,3).join('')}${breath}${cleanWorks.slice(3,5).join('')}</section>
<section class="ag-dusk"><section class="ag-duskl">${L.dusk}</section></section>
<section id="c3" class="ag-night">${chap('c3','03',L.k3,T(groups[5][0]).replace(/^\d+\s*·\s*/,'').replace(/\s+[A-Z][A-Za-z ,'’]+$/,''),true)}${cleanWorks[5]}</section>
<section id="c4">${chap('c4','04',L.k4,h2title(H2[2]))}<div class="ag-tail">${tail.map(html).join('')}</div></section>
</div><script>(function(){var pg=document.getElementById("agpg"),ids=["c0","c1","c2","c3","c4"],as=document.querySelectorAll("#agtoc button");for(var k=0;k<as.length;k++)as[k].onclick=function(){var e=document.getElementById(this.getAttribute("data-t"));if(e)e.scrollIntoView({behavior:"smooth"})};function u(){var h=document.documentElement,y=h.scrollTop||document.body.scrollTop;if(pg)pg.style.width=(y/(h.scrollHeight-h.clientHeight)*100)+"%";var cur=0;ids.forEach(function(id,i){var e=document.getElementById(id);if(e&&e.getBoundingClientRect().top<innerHeight*.4)cur=i});for(var i=0;i<as.length;i++)as[i].className=i==cur?"on":""}addEventListener("scroll",u,{passive:true});u()})()<\/script>`;
return out;
})
