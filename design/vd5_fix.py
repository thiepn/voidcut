from pathlib import Path
p=Path(__file__).resolve().parents[1]/'index.html'
text=p.read_text(encoding='utf-8')
old='<div id="cosHeroRarity" class="cos-rarity">ALL FIVE EFFECTS</div>'
new='<div id="cosHeroRarity" class="cos-rarity">FIVE-LAYER MATERIAL SYSTEM</div>'
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('Expected cosmetics rarity label not found')
p.write_text(text,encoding='utf-8')
print('VD5 legacy showroom phrase removed')
