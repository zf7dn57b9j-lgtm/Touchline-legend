#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import re, subprocess, sys

path=Path("index.html")
if not path.is_file():
    sys.exit("STOP: index.html not found. Run from /workspaces/Touchline-legend.")
original=path.read_text(encoding="utf-8")
old="""  if(active)document.getElementById('transfersScreen').style.display='none';
 };"""
new="""  if(active)document.getElementById('transfersScreen').style.display='none';
 };
 // Route the existing Scouting tab to its own screen before older tab handlers run.
 document.addEventListener('click',function(event){
  const target=event.target;
  const tab=target&&target.closest?target.closest('#tlScoutTab'):null;
  if(!tab)return;
  event.preventDefault();
  event.stopImmediatePropagation();
  window.openScouting();
 },true);
"""
if new in original:
    sys.exit("STOP: Navigation fix is already installed; no changes made.")
if original.count(old)!=1 or original.count('id="tlScoutingDedicatedScreen"')!=1 or original.count('id="tlScoutingCentreFeature"')!=1:
    sys.exit("STOP: Unexpected index.html structure; no changes made.")
updated=original.replace(old,new)
scripts=re.findall(r"<script\\b[^>]*>(.*?)</script>",updated,re.S|re.I)
for i,s in enumerate(scripts):
    if not s.strip(): continue
    try:
        check=subprocess.run(["node","--check"],input=s,text=True,capture_output=True)
    except FileNotFoundError:
        sys.exit("STOP: Node.js required for syntax verification; no changes made.")
    if check.returncode:
        sys.exit(f"STOP: JavaScript block {i} failed syntax check: {check.stderr}")
backup=path.with_name("index-backup-before-scout-navigation-"+datetime.now().strftime("%Y%m%d-%H%M%S")+".html")
backup.write_text(original,encoding="utf-8")
path.write_text(updated,encoding="utf-8")
print("Backup:",backup.name)
print("Scouting navigation fix installed. Existing scouting logic unchanged.")
print("Checked",len(scripts),"JavaScript blocks.")
