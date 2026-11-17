#!/usr/bin/env python3
"""Guarded Touchline Legend scouting balance update."""
from pathlib import Path
from datetime import datetime
import shutil, subprocess, tempfile, re
p=Path('/workspaces/Touchline-legend/index.html')
if not p.is_file():
    p=Path(__file__).with_name('index.html')
if not p.is_file(): raise SystemExit('STOP: index.html not found')
s=p.read_text(encoding='utf-8')
if 'tlScoutBalanceV2' in s: raise SystemExit('STOP: update already installed')
old="const ranks=[{name:'Local Scout',min:40,max:54,wage:400},{name:'Regional Scout',min:55,max:69,wage:1000},{name:'National Scout',min:70,max:84,wage:2500},{name:'International Scout',min:85,max:94,wage:5000},{name:'World-Class Scout',min:95,max:99,wage:8500}];"
new="const ranks=[{name:'Local Scout',min:40,max:54,wage:1500},{name:'Regional Scout',min:55,max:69,wage:4000},{name:'National Scout',min:70,max:84,wage:10000},{name:'International Scout',min:85,max:94,wage:25000},{name:'World-Class Scout',min:95,max:99,wage:50000}];"
if s.count(old)!=1: raise SystemExit('STOP: scouting ranks differ from supplied version')
s=s.replace(old,new)
# Upgrade existing scout contracts to the new rank wage once.
old_get="function get(){let x=null;try{x=JSON.parse(localStorage.getItem(key())||'null')}catch(e){}return x&&typeof x==='object'?x:{scout:null,report:null,lastReport:-1,shortlist:[]};}"
new_get="function get(){let x=null;try{x=JSON.parse(localStorage.getItem(key())||'null')}catch(e){}if(!x||typeof x!=='object')return {scout:null,report:null,lastReport:-1,shortlist:[]};if(x.scout&&!x.scout.balanceV2){const rank=ranks.find(r=>r.name===x.scout.name);if(rank){x.scout.wage=rank.wage;x.scout.balanceV2=true;localStorage.setItem(key(),JSON.stringify(x));}}return x;}"
if s.count(old_get)!=1: raise SystemExit('STOP: scouting save marker missing')
s=s.replace(old_get,new_get)
# Make discoveries depend on the actual squad strength, with scout quality increasing the ceiling.
start=s.index('  const d=tlDivision(),base=[59,66,74,81][d];',s.index('<script id="tlScoutingCentreFeature">'))
end=s.index('  const first=[',start)
new_discovery='''  // tlScoutBalanceV2: scout rating is skill, NEVER a player-rating cap.
  const available=squadPlayers.filter(p=>p&&Number.isFinite(Number(p.rating)));
  const average=available.length?available.reduce((sum,p)=>sum+Number(p.rating),0)/available.length:[65,72,79,86][tlDivision()];
  const skill=Math.max(0,Math.min(1,(quality-40)/59));
  const exceptional=Math.random()<(.025+skill*.15);
  const offset=Math.floor(Math.random()*(11+Math.round(skill*10)))-5+Math.round(skill*5);
  const rating=Math.max(55,Math.min(99,Math.round(average+offset+(exceptional?7+Math.floor(Math.random()*12):0))));
  const growth=3+Math.floor(Math.random()*12)+Math.round(skill*9)+(exceptional?8:0);
  const truePotential=Math.max(rating,Math.min(99,rating+growth));
  const error=Math.max(2,Math.round(19-skill*17));
  const low=Math.max(rating,truePotential-error),high=Math.min(99,truePotential+error);
'''
s=s[:start]+new_discovery+s[end:]
# Existing scout contracts are upgraded to the new wages when loaded.
# Add a short explanatory note that routes into the existing dedicated screen's hiring panel.
needle="  line('HIRE OR REPLACE YOUR SCOUT · BETTER SCOUTS GIVE NARROWER POTENTIAL ESTIMATES');"
replacement="  line('SCOUT RATINGS MEASURE SCOUTING ABILITY, NOT PLAYER RATINGS. EVEN LOCAL SCOUTS CAN FIND FUTURE STARS.');\n"+needle
if s.count(needle)!=1: raise SystemExit('STOP: scouting screen marker missing')
s=s.replace(needle,replacement)
needle2="   if(t.startsWith('HIRE OR REPLACE'))return;"
replacement2="   if(t.startsWith('HIRE OR REPLACE'))return;\n   if(t.startsWith('SCOUT RATINGS MEASURE')){node.className='tl-sc-line';node.style.fontSize='1.05cqw';hiring.appendChild(node);return;}"
if s.count(needle2)!=1: raise SystemExit('STOP: dedicated screen marker missing')
s=s.replace(needle2,replacement2)
# Ensure script syntax before modifying the original.
blocks=re.findall(r'<script(?:\\s[^>]*)?>([\\s\\S]*?)</script>',s,re.I)
with tempfile.TemporaryDirectory() as d:
    for i,b in enumerate(blocks):
        js=Path(d)/f'{i}.js';js.write_text(b)
        r=subprocess.run(['node','--check',str(js)],capture_output=True,text=True)
        if r.returncode: raise SystemExit('STOP: JavaScript syntax failed: '+r.stderr[:800])
backup=p.with_name('index-backup-before-scout-balance-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.html')
shutil.copy2(p,backup)
p.write_text(s,encoding='utf-8')
print('Backup:',backup.name)
print('Installed scout wages, squad-relative discoveries and Scouting Centre explanation.')
print('Verified JavaScript syntax. Existing careers retained.')
