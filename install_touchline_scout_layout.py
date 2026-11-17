#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import re, subprocess, sys
p=Path('index.html')
if not p.is_file():sys.exit('STOP: Run from /workspaces/Touchline-legend')
s=p.read_text(encoding='utf-8')
anchor='#tlScoutScreen .tl-sc-footer button{flex:1;border:3px solid #ffce42;border-radius:16px;background:linear-gradient(#2670d0,#07265f);color:white;font-size:1.8cqw;font-weight:900;cursor:pointer}\n</style>'
css='/* Compact scouting panels: preserve all existing report and hiring behaviour. */\n#tlScoutScreen .tl-sc-content{top:18%;height:69%;grid-template-rows:29% 69%}\n#tlScoutScreen .tl-sc-card{padding:1.4% 2%}\n#tlScoutScreen .tl-sc-card h2{margin:0 0 .7%;font-size:1.6cqw}\n#tlScoutScreen .tl-sc-summary .tl-sc-line{font-size:1.22cqw;line-height:1.15;padding:.55% 1.4%;margin:.45% 0}\n#tlScoutScreen .tl-sc-report .tl-sc-player{font-size:1.55cqw;line-height:1.24;padding:1.3% 2%;margin:1% 0}\n#tlScoutScreen .tl-sc-actions{margin-top:1%;gap:2%}\n#tlScoutScreen .tl-sc-actions .ex-button{font-size:1.15cqw;padding:.8% 2.5%}\n'
if css in s:sys.exit('STOP: Scouting layout fix already installed; no changes made.')
if s.count(anchor)!=1 or s.count('id="tlScoutScreen"')!=1 or s.count('id="tlScReport"')!=1:
 sys.exit('STOP: Latest code differs from the inspected version; no changes made.')
out=s.replace(anchor,anchor.replace('</style>',css+'</style>'))
for i,script in enumerate(re.findall(r'<script\b[^>]*>(.*?)</script>',out,re.S|re.I)):
 if script.strip():
  try:r=subprocess.run(['node','--check'],input=script,text=True,capture_output=True)
  except FileNotFoundError:sys.exit('STOP: Node.js is needed for verification; no changes made.')
  if r.returncode:sys.exit('STOP: JavaScript validation failed at block '+str(i)+': '+r.stderr)
backup=p.with_name('index-backup-before-scout-layout-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.html')
backup.write_text(s,encoding='utf-8')
p.write_text(out,encoding='utf-8')
print('Backup:',backup.name)
print('Scouting layout adjusted. All game logic unchanged.')
