from pathlib import Path
from datetime import datetime
import shutil, sys
p=Path('index.html')
if not p.is_file(): sys.exit('STOP: Run in the Touchline-legend folder (index.html missing).')
s=p.read_text(encoding='utf-8')
markers=['function tlWeeklyWages(){','function tlWageBudget(){','function tlCreditIncome(', 'function tlFreeAgents()', 'function tlFreeAgentKey()', '<script id="tlDashboardContractsShortcut">','</body>']
for m in markers:
 if s.count(m)!=1: sys.exit(f'STOP: expected one marker {m!r}, found {s.count(m)}. No changes made.')
if 'id="tlScoutingCentreFeature"' in s: sys.exit('STOP: Scouting Centre already installed. No changes made.')
backup=p.with_name('index-backup-before-scouting-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.html')
shutil.copy2(p,backup)
addon=r'''<style id="tlScoutingStyle">
#transfersScreen .ex-tabs{gap:1%;}
#transfersScreen .ex-tabs .ex-button{font-size:1.35cqw;min-width:0;padding:.7% .4%;}
#tlScoutPanel{font-size:1.35cqw;line-height:1.45}
#tlScoutPanel .ex-metric{font-size:1.35cqw;margin:.8% 0;padding:1%}
#tlScoutPanel .ex-button{font-size:1.25cqw;margin:.3% .5%;}
#tlScoutPanel .tl-scout-option{display:flex;align-items:center;justify-content:space-between;gap:1%;padding:.7% 1%;border-bottom:1px solid #ffffff33}
</style>
<script id="tlScoutingCentreFeature">
(function(){
 'use strict';
 const ranks=[{name:'Local Scout',min:40,max:54,wage:400},{name:'Regional Scout',min:55,max:69,wage:1000},{name:'National Scout',min:70,max:84,wage:2500},{name:'International Scout',min:85,max:94,wage:5000},{name:'World-Class Scout',min:95,max:99,wage:8500}];
 const key=()=> 'touchlineScout_'+careerClub();
 function get(){let x=null;try{x=JSON.parse(localStorage.getItem(key())||'null')}catch(e){}return x&&typeof x==='object'?x:{scout:null,report:null,lastReport:-1};}
 function save(x){localStorage.setItem(key(),JSON.stringify(x));}
 function scoutWage(){const x=get();return x.scout?Number(x.scout.wage)||0:0;}
 const oldWages=tlWeeklyWages;
 tlWeeklyWages=function(){return oldWages()+scoutWage();};
 function completed(){loadMatches();return leagueMatches.filter(w=>w.some(m=>(teams[m.home]===careerClub()||teams[m.away]===careerClub())&&Number.isInteger(m.homeGoals)&&Number.isInteger(m.awayGoals))).length;}
 function discover(x,week){
  const scout=x.scout,quality=scout.rating;
  const d=tlDivision(),base=[59,66,74,81][d];
  // Better scouts improve odds; no scout guarantees elite talent.
  const luck=Math.random(),bonus=luck<.025?22:luck<.15?13:luck<.43?7:Math.floor(Math.random()*6);
  const potential=Math.min(99,Math.max(55,base+Math.floor((quality-40)/12)+bonus));
  const rating=Math.max(55,Math.min(96,base-4+Math.floor(Math.random()*10)));
  const truePotential=Math.max(rating,potential);
  const error=Math.max(2,Math.round(21-(quality-40)*.33));
  const low=Math.max(rating,truePotential-error),high=Math.min(99,truePotential+error);
  const first=['Oliver','Jacob','Lewis','Freddie','Archie','Noah','Theo','Harry','Ethan','Sam','Max','Isaac','Luca','George'];
  const last=['Bennett','Fletcher','Cooper','Hart','Morris','Hughes','Price','Reed','Turner','Walsh','Mason','Fox','Bailey','Carter'];
  const name=first[Math.floor(Math.random()*first.length)]+' '+last[Math.floor(Math.random()*last.length)];
  const pos=['GK','DC','DR','DL','MC','ML','MR','AMC','ST'][Math.floor(Math.random()*9)];
  const age=16+Math.floor(Math.random()*8);
  x.report={id:'scout-'+tlSeason()+'-'+week+'-'+Math.floor(Math.random()*1e7),name,pos,age,rating,potential:truePotential,low,high,wage:tlWage(rating,tlDivision()),fee:playerPrice({rating,age}),week,season:tlSeason()};
  x.lastReport=week;save(x);
 }
 function progress(){const x=get();if(!x.scout||x.report)return;const w=completed();if(w>=4&&w%4===0&&x.lastReport!==w)discover(x,w);}
 // This function is called only when matchweek income is credited; reports are not created by refreshing.
 const previousCredit=tlCreditIncome;
 tlCreditIncome=function(week,home){const result=previousCredit(week,home);if(result){const x=get();if(x.scout&&!x.report){const w=week+1;if(w>=4&&w%4===0&&x.lastReport!==w)discover(x,w);}}return result;};
 const previousOpen=openTransfers;
 openTransfers=function(){previousOpen();const tabs=document.querySelector('#transfersScreen .ex-tabs');if(tabs&&!document.getElementById('tlScoutTab')){const b=document.createElement('button');b.type='button';b.id='tlScoutTab';b.className='ex-button';b.textContent='SCOUTING';b.onclick=function(){transferTab='scouting';renderTransfers();};tabs.appendChild(b);}};
 const previousRender=renderTransfers;
 renderTransfers=function(){if(transferTab!=='scouting')return previousRender();squadLoad();const host=document.getElementById('transferRows');host.replaceChildren();document.getElementById('transferBudget').textContent='SCOUTING CENTRE · ONE REPORT EVERY FOUR LEAGUE MATCHWEEKS';const panel=document.createElement('div');panel.id='tlScoutPanel';host.appendChild(panel);const x=get(),w=completed();
  const line=(t)=>{const el=document.createElement('div');el.className='ex-metric';el.textContent=t;panel.appendChild(el);return el;};
  const btn=(t,action,where=panel)=>{const b=document.createElement('button');b.type='button';b.className='ex-button';b.textContent=t;b.onclick=action;where.appendChild(b);return b;};
  line('SHARED WEEKLY WAGES: '+pounds(tlWeeklyWages())+' / '+pounds(tlWageBudget())+' · AVAILABLE '+pounds(Math.max(0,tlWageBudget()-tlWeeklyWages())));
  if(x.scout)line('EMPLOYED: '+x.scout.name+' · RATING '+x.scout.rating+' · '+pounds(x.scout.wage())+'/week');
  else line('NO SCOUT EMPLOYED. Hire one to begin receiving reports.');
  if(x.scout){const next=(Math.floor(w/4)+1)*4;line(x.report?'NEW PLAYER REPORT AVAILABLE':('NEXT REPORT: '+(w%4===0&&w>0?4:4-w%4)+' LEAGUE MATCHWEEK(S) · MATCHWEEK '+next));}
  if(x.report){const p=x.report;line('DISCOVERED PLAYER: '+p.name+' · '+p.pos+' · AGE '+p.age+' · CURRENT RATING '+p.rating+' · ESTIMATED POTENTIAL '+p.low+'–'+p.high+' · FEE '+pounds(p.fee)+' · WAGES '+pounds(p.wage)+'/week');
   btn('SIGN PLAYER',()=>{const a=get(),q=a.report;if(!q||q.id!==p.id)return renderTransfers();if(!transferWindow().open)return alert('You can only sign scouted players during a transfer window.');squadLoad();if(squadPlayers.length>=25)return alert('Squad is full (25 players).');const f=financeData();if(f.budget<q.fee)return alert('Insufficient transfer budget.');if(tlWeeklyWages()+q.wage>tlWageBudget())return alert('Signing would exceed the shared wage budget.');if(!confirm('Sign '+q.name+' for '+pounds(q.fee)+' and '+pounds(q.wage)+'/week?'))return;f.budget-=q.fee;f.balance-=q.fee;f.spent+=q.fee;storeFinance(f);const player={id:q.id,name:q.name,pos:q.pos,age:q.age,rating:q.rating,potential:q.potential,wage:q.wage,contractUntil:tlSeason()+3,economyVersion:2,injury:0,ban:0,yellows:0};squadPlayers.push(player);squadSave();a.report=null;save(a);renderTransfers();});
   btn('DISMISS REPORT',()=>{if(!confirm('Dismiss this player report?'))return;const a=get();a.report=null;save(a);renderTransfers();});
  }
  line('HIRE OR REPLACE YOUR SCOUT · BETTER SCOUTS GIVE NARROWER POTENTIAL ESTIMATES');
  for(const r of ranks){const wrap=document.createElement('div');wrap.className='tl-scout-option';const label=document.createElement('span');label.textContent=r.name+' · rating '+r.min+'–'+r.max+' · '+pounds(r.wage)+'/week';wrap.appendChild(label);btn(x.scout&&x.scout.name===r.name?'EMPLOYED':'HIRE',()=>{const a=get();const available=tlWageBudget()-tlWeeklyWages()+(a.scout?Number(a.scout.wage)||0:0);if(r.wage>available)return alert('Not enough wage budget. Available after replacing current scout: '+pounds(Math.max(0,available))+'/week.');if(!confirm('Hire '+r.name+' for '+pounds(r.wage)+'/week?'))return;const rating=r.min+Math.floor(Math.random()*(r.max-r.min+1));a.scout={name:r.name,rating,wage:r.wage};save(a);renderTransfers();},wrap);panel.appendChild(wrap);}
  if(x.scout)btn('RELEASE SCOUT',()=>{if(!confirm('Release your scout and stop future reports?'))return;const a=get();a.scout=null;save(a);renderTransfers();});
 };
 // Display scouting wages in existing financial summary; no second payroll deduction.
 const previousFinances=openFinances;
 openFinances=function(){previousFinances();const body=document.getElementById('financeBody');if(body){const d=document.createElement('div');d.className='ex-metric';d.textContent='SCOUT WAGES INCLUDED IN TOTAL: '+pounds(scoutWage())+'/week';body.appendChild(d);}};
})();
</script>
'''
# fix typo in static addon before install
addon=addon.replace('x.scout.wage()','x.scout.wage')
s=s.replace('</body>',addon+'</body>')
p.write_text(s,encoding='utf-8')
print('Installed scouting. Backup:',backup)
print('Feature marker:',s.count('id="tlScoutingCentreFeature"'))
