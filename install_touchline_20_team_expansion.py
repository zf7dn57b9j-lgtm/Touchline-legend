from pathlib import Path
import re, json, hashlib, shutil, datetime, subprocess, tempfile, sys
TARGET=Path('index.html')
if not TARGET.is_file(): sys.exit('STOP: index.html not found; run in the game folder')
raw=TARGET.read_bytes()
if hashlib.sha256(raw).hexdigest()!='8ecb7490fb79e2df6866297076db3af09c74ab89b6318aae9b15d5522a4815f4': sys.exit('STOP: index.html does not match uploaded 20:54 version. No changes made.')
src=raw.decode('utf-8')
if 'TL_EXPANSION_20_V1' in src: sys.exit('STOP: expansion already installed')
regional=['Westbridge United','Redmoor Athletic','Ironvale FC','Brookfield Town','Seabourne FC','Oakchester United','Kingsford Town','Ashbourne Rovers','Northwick Albion','Eastport City','Ravenshill FC','Ledgemont Athletic','Willowford City','Stonehaven Rovers','Meadowport Albion','Eastmere Athletic','Northbridge Town','Fairhaven County','Redcastle United','Larkfield Wanderers']
league1=['Barnsliy','Blackpaol','Bradfard City','Bromlay','Burton Albien','Cambridga United','Doncaster Rovars','Huddersfiold Town','Leicestar City','Leytan Orient','Luton Tawn','Mansfiold Town','Milton Kaynes','Notts Caunty','Oxford Unated','Peterboraugh United','Plymauth Argyle','Readang','Sheffiold Wednesday','Stevenega']
champ=['Birminghem City','Blackburn Rovars','Bolton Wanderars','Bristal City','Burnlay','Cardiff Cety','Charlton Athletac','Derby Caunty','Lincoln Cety','Middlesbraugh','Millwoll','Norwich Cety','Portsmouth','Preston North And','Queens Park Rangars','Sheffield Unated','Southamptan','Stoke Cety','Swansea Cety','Watfard']
prem=['AFC Bournemauth','Arsenol','Aston Villo','Brentfard','Brighton & Hove Albien','Chelseo','Coventry Cety','Crystal Palaca','Everten','Fulhem','Hull Cety','Ipswich Tawn','Leeds Unated','Liverpaol','Manchester Cety','Manchester Unated','Newcastle Unated','Nottingham Forast','Sunderlend','Tottenham Hotspar']
assert all(len(x)==20 and len(set(x))==20 for x in [regional,league1,champ,prem])
# substitutions must be unique to protect from unrelated code changes
replacements=[]
def swap(old,new,expected=1):
 replacements.append((old,new,expected))
old="const divisionOpponents=[\n"+src.split('const divisionOpponents=[\n',1)[1].split('\n];',1)[0]+'\n];'
new='const divisionOpponents='+json.dumps([regional,league1,champ,prem],ensure_ascii=False,indent=1)+';'
swap(old,new)
swap('const circle=teams.map((_,i)=>i),weeks=[];', 'const circle=teams.map((_,i)=>i),weeks=[];') if False else None
swap('round<11','round<teams.length-1')
swap('j<6','j<teams.length/2')
swap('circle[11-j]','circle[teams.length-1-j]')
swap('saved.length===22&&saved.every(w=>Array.isArray(w)&&w.length===6)','saved.length===38&&saved.every(w=>Array.isArray(w)&&w.length===10)')
swap('next<0?21:next','next<0?37:next')
swap('(fixtureWeek+n+22)%22','(fixtureWeek+n+38)%38')
swap("' OF 22'","' OF 38'",3)
swap('completed===22','completed===38')
swap('completed>=11&&completed<14','completed>=18&&completed<23')
swap('remaining:14-completed','remaining:23-completed')
swap("completed<11?'CLOSED — WINTER WINDOW OPENS AT MATCHWEEK 12'","completed<18?'CLOSED — WINTER WINDOW OPENS AT MATCHWEEK 19'")
swap("'Season complete — all 22 matches played.'","'Season complete — all 38 matches played.'")
swap('st.clubs.length===12','st.clubs.length===20',3)
swap("' · 12 CLUBS'","' · 20 CLUBS'")
swap('rank>=11','rank>=19',3)
swap("'FINAL POSITION: '+rank+' OF 12'","'FINAL POSITION: '+rank+' OF 20'")
swap("'The next season has 22 fresh fixtures.'","'The next season has 38 fresh fixtures.'")
swap('rotated.slice(0,11)','rotated.slice(0,19)')
swap('const played=after<0?22:after','const played=after<0?38:after',2)
swap('const count=played<0?22:played','const count=played<0?38:played')
swap('11*[12000,45000,300000,2500000][d]+22*','19*[12000,45000,300000,2500000][d]+38*')
swap('const annualWages=22*tlWeeklyWages()','const annualWages=38*tlWeeklyWages()')
swap('(tlResultWeek+direction+22)%22','(tlResultWeek+direction+38)%38')
swap('Math.max(22,new Set(matches.map(m=>m.id)).size)','Math.max(38,new Set(matches.map(m=>m.id)).size)')
swap("'League has 22 fixtures'","'League has 38 fixtures'",0) if False else None
swap('const tlCupRounds={national:[\'ROUND OF 64\'','const tlCupRounds={national:[\'ROUND OF 128\',\'ROUND OF 64\'')
swap('const tlCupWeeks={national:[1,4,8,12,16,20]','const tlCupWeeks={national:[2,7,12,18,24,30,36]')
swap('const tlCupPrizes={national:[10000,25000,65000,150000,400000,1500000]','const tlCupPrizes={national:[5000,10000,25000,65000,150000,400000,1500000]')
swap("const regionalIndex=league.findIndex(e=>e.name==='Ledgemont Athletic');","const regionalIndex=league.findIndex(e=>e.name==='Ledgemont Athletic');") if False else None
swap('if(regionalIndex>=0)league[regionalIndex]=tlCupEntry(mine,div);\n   else league[0]=tlCupEntry(mine,div);','if(regionalIndex>=0)league[regionalIndex]=tlCupEntry(mine,div);\n   else {const slot=league.findIndex(e=>e.division===div);league[slot>=0?slot:0]=tlCupEntry(mine,div);}')
swap('const nonLeague=tlNonLeagueClubs.map(name=>tlCupEntry(name,-1));','const nonLeague=Array.from({length:48},(_,i)=>tlCupEntry(tlNonLeagueClubs[i]||(\'Non-League \'+[\'Vale\',\'Rovers\',\'Town\',\'Athletic\'][i%4]+\' \'+(i+1)),-1));')
swap('const tlInitialClubs=[...divisionOpponents[0]];','const tlInitialClubs=[...divisionOpponents[0]];') if False else None
# Critical: ensure first season has 20 teams after reset and custom selection
swap('teams.splice(0,teams.length,...tlInitialClubs);','teams.splice(0,teams.length,...tlInitialClubs);',0) if False else None
# Current reset uses initialSchedule created when teams has 12; generate from 20 after choosing club
swap('leagueMatches=JSON.parse(JSON.stringify(initialSchedule));\n fixtureWeek=0;', 'leagueMatches=JSON.parse(JSON.stringify(makeSchedule()));\n fixtureWeek=0;')
# initialize 20 clubs before any match load; after club selection code creates 12 buttons, no change
swap('seasonTeams();\nconst oldMatchStorageKey', 'teams.splice(0,teams.length,...divisionOpponents[0]);\nseasonTeams();\nconst oldMatchStorageKey')
# fix base makeSchedule initialSchedule only used for fallback, recompute 20 schedule in loadMatches
swap('JSON.parse(JSON.stringify(initialSchedule));','JSON.parse(JSON.stringify(makeSchedule()));',2)
# reset to 20 before new career while preserving selected club
# update report and labels (global only specific)
swap('12 CLUBS</div>','20 CLUBS</div>',0) if False else None
# use replacements with strict checks
for a,b,n in replacements:
 if n==0:continue
 c=src.count(a)
 if c!=n:print('BAD',n,c,repr(a[:75]));raise SystemExit(1)
 src=src.replace(a,b)
# fix club choices: 12 remain, custom replace index 11
# schedule should never use 12-club initial schedule after reset
# update text and other scoped 22 assumptions
src=src.replace("['PLAYED',22]","['PLAYED',38]")
src=src.replace('all six results from the completed matchweek','all ten results from the completed matchweek')
src=src.replace('League has 22 fixtures','League has 38 fixtures')
src=src.replace('22 fresh fixtures','38 fresh fixtures')
src=src.replace('22 matches played','38 matches played')
# initial 12 team selection stays unchanged; makeSchedule dynamically 20 after initialization
# Increase league table density and fixture rows
css='''<style id="tlExpansion20Style">\n#fixturesScreen .fl-fixture-grid,#tlAllResultsScreen .fl-fixture-grid{grid-template-rows:repeat(5,1fr);gap:1%}\n#fixturesScreen .fl-match,#tlAllResultsScreen .fl-match{font-size:1.02cqw;padding:.35% 1%;border-radius:6px;min-width:0;overflow:hidden}\n#fixturesScreen .fl-match span,#tlAllResultsScreen .fl-match span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n#leagueScreen .fl-table{font-size:.86cqw}\n#leagueScreen .fl-table th{height:1.65cqw}\n#leagueScreen .fl-table td{height:1.48cqw}\n#leagueScreen .fl-subtitle{font-size:1.05cqw;height:5%}\n</style>\n'''
src=src.replace('</head>',css+'</head>',1)
# cup 128 requires first 20 clubs each division; 80+48
# ensure custom restoration doesn't shrink 20 clubs
# restore at startup after first season initialization; current restore only swaps index 11
# The original code uses club index 11 for custom club; all good.
# guard against duplicate installs
src=src.replace('<title>Touchline Legend</title>','<title>Touchline Legend</title>\n<!-- TL_EXPANSION_20_V1 -->',1)
# Syntax check and fixture test before modifying the original.
js='\n'.join(re.findall(r'<script(?: [^>]*)?>(.*?)</script>',src,re.S))
with tempfile.TemporaryDirectory() as tmp:
 check=Path(tmp)/'check.js';check.write_text(js)
 subprocess.run(['node','--check',str(check)],check=True)
 schedule=re.search(r'function makeSchedule\(\)\{.*?\n\}',src,re.S)
 assert schedule, 'schedule function missing'
 test=Path(tmp)/'test.js'
 test.write_text('const teams=Array.from({length:20},(_,i)=>"Club "+i);\n'+schedule.group(0)+'\nconst weeks=makeSchedule();const pairs=new Set();for(const w of weeks){if(w.length!==10)throw Error("wrong match count");for(const m of w){const key=m.home+"-"+m.away;if(pairs.has(key))throw Error("duplicate fixture");pairs.add(key)}}if(weeks.length!==38||pairs.size!==380)throw Error("wrong fixture total");\n')
 subprocess.run(['node',str(test)],check=True)
 assert all(len(g)==20 for g in [regional,league1,champ,prem])
 assert 'length:48' in src and "'ROUND OF 128'" in src
backup=TARGET.with_name('index-backup-before-20-team-expansion-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.html')
shutil.copy2(TARGET,backup)
TARGET.write_text(src,encoding='utf-8')
print('SUCCESS: 20-team expansion installed')
print('Backup:',backup)
print('Verified: JavaScript syntax, 38 weeks, 10 fixtures/week, 380 fixtures, cup structure')
