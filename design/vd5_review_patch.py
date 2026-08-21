from pathlib import Path

p=Path(__file__).resolve().parents[1]/'index.html'
text=p.read_text(encoding='utf-8')

marker='// === VD5 COSMETICS CONTRACT'
if 'function cosmeticLoadoutDisplayName(name)' not in text:
    old="let cosmeticsFocusCat='arena';\nconst COSMETIC_UI="
    new="let cosmeticsFocusCat='arena';\nfunction cosmeticLoadoutDisplayName(name){return name==='VOID'?'STANDARD':name==='NEON'?'OFFSET':name}\nconst COSMETIC_UI="
    if old not in text: raise SystemExit('Cosmetics focus anchor not found')
    text=text.replace(old,new,1)

repls={
"$('cosHeroName').textContent=slot?.filled?slot.name:'CUSTOM'":"$('cosHeroName').textContent=slot?.filled?cosmeticLoadoutDisplayName(slot.name):'CUSTOM'",
"showCoach('LOADOUT EQUIPPED',slot.name,cosmeticComboLabel(clean),1100)":"showCoach('LOADOUT EQUIPPED',cosmeticLoadoutDisplayName(slot.name),cosmeticComboLabel(clean),1100)",
"showCoach('LOADOUT SAVED',slot.name,'All five visual slots stored.',1050)":"showCoach('LOADOUT SAVED',cosmeticLoadoutDisplayName(slot.name),'All five visual slots stored.',1050)",
"<span>${slot.name}</span>":"<span>${cosmeticLoadoutDisplayName(slot.name)}</span>",
"<span class=\"cos-card-badge\">${selected?'LIVE':ok?'READY':'LOCK'}</span>":"<span class=\"cos-card-badge\">${selected?'ON':ok?'AVAILABLE':'LOCKED'}</span>",
}
for old,new in repls.items():
    if old in text: text=text.replace(old,new,1)
    elif new not in text: raise SystemExit('Expected certification target not found: '+old[:60])

CSS='''\n/* === VD5 CERTIFICATION CORRECTIONS ======================================= */\n.cos-card-badge{max-width:calc(100% - 24px)!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}\n@media(max-width:420px){.cos-card-badge{font-size:7px!important;padding:3px 4px!important}}\n'''
if '/* === VD5 CERTIFICATION CORRECTIONS' not in text:
    anchor='\n</style>\n\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />'
    if anchor not in text: raise SystemExit('Style close anchor not found')
    text=text.replace(anchor,CSS+anchor,1)

p.write_text(text,encoding='utf-8')
print('VD5 certification corrections applied')
