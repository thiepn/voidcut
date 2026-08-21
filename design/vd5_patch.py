from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')

if 'name="voidcut-visual-phase" content="VD5"' in text:
    print('VD5 cosmetics already applied')
    raise SystemExit(0)
if 'name="voidcut-visual-phase" content="VD4"' not in text:
    raise SystemExit('Expected VD4 baseline')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    text = text.replace(old, new, 1)


def replace_regex(pattern: str, repl: str, label: str) -> None:
    global text
    updated, count = re.subn(pattern, repl, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one regex match, found {count}')
    text = updated


replace_once('name="voidcut-visual-phase" content="VD4"', 'name="voidcut-visual-phase" content="VD5"', 'visual phase')

# Keep persisted cosmetic IDs exactly stable, but replace player-facing names and descriptions.
name_replacements = {
"['void','VOID','Always unlocked','Cold abyssal arena with cyan containment geometry, parallax structures and sparse void light.']": "['void','COATED','Always unlocked','Clean coated stock with crisp ink, restrained grain and a precise field edge.']",
"['ember','EMBER','Reach Chamber 8','Carbon-black fracture world with amber fault lines, drifting plates and rising ember particulate.']": "['ember','KRAFT','Reach Chamber 8','Warm fiber stock with dark printed rules and a rougher material edge.']",
"['amethyst','AMETHYST','Score 100,000','Violet crystalline world with faceted planes, suspended shards and refractive grid structure.']": "['amethyst','RISOGRAPH','Score 100,000','Layered violet print with visible registration offsets and faceted ink blocks.']",
"['aurora','AURORA','Always unlocked','Teal-violet energy world with flowing ribbons, curved field lines and soft atmospheric motion.']": "['aurora','OFFSET','Always unlocked','Two-ink offset treatment with broad structural color fields and controlled misregistration.']",
"['monochrome','MONOCHROME','Reach 90 chamber mastery','Brutalist near-black simulation space with white slabs, calibration geometry and minimal glow.']": "['monochrome','MONO','Reach 90 chamber mastery','High-contrast black-and-white stock using shape and pattern instead of color.']",
"['core','CORE','Always unlocked','Solid energy core with the standard archetype glyph.']": "['core','SOLID','Always unlocked','Solid printed disc with the standard gameplay glyph.']",
"['hollow','HOLLOW','Land a 35% cut','Open ring construction with no filled center.']": "['hollow','HOLLOW','Land a 35% cut','Open ring disc with a clear center and strong outline.']",
"['prism','PRISM','Reach 80 chamber mastery','Double-ring geometric shell with crisp inner facets.']": "['prism','FACET','Reach 80 chamber mastery','Geometric disc with a rotated inner facet mark.']",
"['reactor','REACTOR','Always unlocked','Rotating reactor spokes and a bright inner containment ring.']": "['reactor','TARGET','Always unlocked','Target-style disc with an inner ring and directional registration marks.']",
"['eclipse','ECLIPSE','Score 250,000','Dark core body with a razor-bright crescent rim.']": "['eclipse','CRESCENT','Score 250,000','Dark disc body with a high-contrast crescent edge.']",
"['beam','BEAM','Always unlocked','Clean tapered energy line.']": "['beam','GRAPHITE','Always unlocked','Single dry motion rule behind each moving disc.']",
"['comet','COMET','3 consecutive 25%+ cuts','Separated glowing particles follow each core.']": "['comet','DOTS','3 consecutive 25%+ cuts','Separated printed dots mark recent disc motion.']",
"['echo','ECHO','3 divider-free chamber clears','Fading ghost rings repeat behind each core.']": "['echo','ECHO','3 divider-free chamber clears','Repeated outline impressions trail behind each disc.']",
"['ribbon','RIBBON','Always unlocked','Twin curved-looking rails create a wide motion ribbon.']": "['ribbon','DOUBLE RULE','Always unlocked','Two parallel motion rules create a wider directional trace.']",
"['sparks','SPARKS','Make 250 lifetime cuts','Short angular sparks scatter behind moving cores.']": "['sparks','HASH','Make 250 lifetime cuts','Short offset hash marks break up the motion path.']",
"['pulse','PULSE','Always unlocked','Classic luminous cut with soft energy bloom.']": "['pulse','INK','Always unlocked','Standard scored seam with a direct ink rule.']",
"['blade','BLADE','Clear a chamber in 4 cuts','Ultra-thin hard-edged white cutting blade.']": "['blade','BLADE','Clear a chamber in 4 cuts','Ultra-thin hard-edged incision with minimal visual weight.']",
"['arc','ARC','Survive 5 lifetime close calls','Segmented electrical arc with bright lock points.']": "['arc','PERFORATION','Survive 5 lifetime close calls','Segmented perforation marks with explicit endpoint locks.']",
"['laser','LASER','Always unlocked','Dual-rail laser with a white-hot center line.']": "['laser','DOUBLE CUT','Always unlocked','Twin parallel score lines around the exposed substrate seam.']",
"['rift','RIFT','Earn 3 S+ clears','Violet spatial tear with animated offset fracture lines.']": "['rift','OFFSET CUT','Earn 3 S+ clears','Misregistered paired ink rules create a deliberate offset incision.']",
"['implode','IMPLODE','Always unlocked','Removed geometry contracts rapidly into its center.']": "['implode','PUNCH','Always unlocked','Removed material contracts like a clean punch-out.']",
"['shatter','SHATTER','Land a 45% cut','The removed region breaks into outlined shards.']": "['shatter','SHATTER','Land a 45% cut','Removed material separates into sharp printed fragments.']",
"['dissolve','DISSOLVE','Earn one S+ clear','Boundary disintegrates into a broken fading contour.']": "['dissolve','FADE','Earn one S+ clear','The removed edge breaks into a fading dotted contour.']",
"['vacuum','VACUUM','Always unlocked','Concentric vacuum rings suck the removed space inward.']": "['vacuum','RING','Always unlocked','Concentric registration rings compress the removed piece inward.']",
"['fracture','FRACTURE','Score 50,000 on one cut','Angular fracture wedges split and peel away from the cut.']": "['fracture','PEEL','Score 50,000 on one cut','Angular material wedges split and peel away from the cut.']",
}
for old, new in name_replacements.items():
    replace_once(old, new, 'cosmetic copy')

replace_once(
"const defaultCosmeticLoadouts=()=>({active:0,slots:[{name:'VOID',filled:true,cosmetics:{arena:'void',ball:'core',trail:'beam',cut:'pulse',collapse:'implode'}},{name:'NEON',filled:true,cosmetics:{arena:'aurora',ball:'reactor',trail:'ribbon',cut:'laser',collapse:'vacuum'}},{name:'CUSTOM A',filled:false,cosmetics:{arena:'void',ball:'core',trail:'beam',cut:'pulse',collapse:'implode'}},{name:'CUSTOM B',filled:false,cosmetics:{arena:'void',ball:'core',trail:'beam',cut:'pulse',collapse:'implode'}}]});",
"const defaultCosmeticLoadouts=()=>({active:0,slots:[{name:'STANDARD',filled:true,cosmetics:{arena:'void',ball:'core',trail:'beam',cut:'pulse',collapse:'implode'}},{name:'OFFSET',filled:true,cosmetics:{arena:'aurora',ball:'reactor',trail:'ribbon',cut:'laser',collapse:'vacuum'}},{name:'CUSTOM A',filled:false,cosmetics:{arena:'void',ball:'core',trail:'beam',cut:'pulse',collapse:'implode'}},{name:'CUSTOM B',filled:false,cosmetics:{arena:'void',ball:'core',trail:'beam',cut:'pulse',collapse:'implode'}}]});",
'default loadout names')

replace_once('<div class="cos-top-tabs"><span class="active">COSMETICS</span><span>VISUAL LOADOUT</span></div>', '<div class="cos-top-tabs"><span class="active">MATERIAL LIBRARY</span><span>LIVE SPECIMEN</span></div>', 'cosmetic tabs')
replace_once('<span class="cos-preview-kicker">FULL LOADOUT</span>', '<span class="cos-preview-kicker">SPECIMEN / LIVE</span>', 'hero kicker')
replace_once('<p id="cosHeroMeta">Your complete visual setup is previewed together.</p>', '<p id="cosHeroMeta">Every equipped material and motion treatment is shown together.</p>', 'hero copy')
replace_once('<div class="cos-equipped"><span>✓</span> LIVE PREVIEW</div>', '<div class="cos-equipped"><span>■</span> APPLIED TO GAMEPLAY</div>', 'hero applied label')
replace_once('Save or equip Arena + Core + Trail + Cut + Collapse together.', 'Save or equip Field + Disc + Trace + Cut + Removal together.', 'loadout helper')

hero = '''      <div id="cosHeroArt" class="cos-hero-art" aria-hidden="true">
        <div class="vd5-specimen-board">
          <svg class="vd5-live-specimen" viewBox="0 0 760 420" preserveAspectRatio="xMidYMid slice">
            <rect class="vd5-specimen-ground" width="760" height="420"/>
            <g class="vd5-registration"><path d="M48 52h28M62 38v28M684 52h28M698 38v28M48 364h28M62 350v28M684 364h28M698 350v28"/></g>
            <path class="vd5-field-shadow" d="M132 78 606 62 680 146 632 338 522 378 142 352 88 248Z"/>
            <path class="vd5-field" d="M124 70 598 54 672 138 624 330 514 370 134 344 80 240Z"/>
            <g class="vd5-field-print"><path d="M138 112h190M138 132h132M492 304h92M514 322h70"/><path d="M192 86v42M548 298v50"/></g>
            <path class="vd5-removal-shadow" d="M448 205 662 132 625 272 530 304Z"/>
            <path class="vd5-removal" d="M438 196 652 123 615 263 520 295Z"/>
            <path class="vd5-trace vd5-trace-a" d="M202 176 294 195"/>
            <path class="vd5-trace vd5-trace-b" d="M212 184 302 203"/>
            <path class="vd5-cut-trench" d="M150 309 642 142"/>
            <path class="vd5-cut-ink vd5-cut-ink-a" d="M150 309 642 142"/>
            <path class="vd5-cut-ink vd5-cut-ink-b" d="M153 315 645 148"/>
            <g class="vd5-disc vd5-disc-a"><circle class="vd5-disc-body" cx="278" cy="180" r="30"/><circle class="vd5-disc-inner" cx="278" cy="180" r="13"/><path class="vd5-disc-mark" d="M260 180h36M278 162v36"/></g>
            <g class="vd5-disc vd5-disc-b"><circle class="vd5-disc-body" cx="472" cy="294" r="25"/><circle class="vd5-disc-inner" cx="472" cy="294" r="10"/><path class="vd5-disc-mark" d="m460 283 24 22M484 283l-24 22"/></g>
          </svg>
          <div class="vd5-specimen-caption"><span>LIVE FIELD / 01</span><strong>ONE LOADOUT. FIVE LAYERS.</strong><em>Theme-safe material preview</em></div>
        </div>
      </div>
    </div>
    <section class="cos-loadout-dock"'''
replace_regex(r'      <div id="cosHeroArt" class="cos-hero-art" aria-hidden="true">.*?    </div>\n    <section class="cos-loadout-dock"', hero, 'cosmetic hero specimen')

replace_once(
"const COSMETIC_UI={arena:{label:'ARENA',title:'ARENA STYLES',preview:'arena'},ball:{label:'CORE',title:'CORE STYLES',preview:'ball'},trail:{label:'TRAIL',title:'TRAIL STYLES',preview:'trail'},cut:{label:'CUT',title:'CUT STYLES',preview:'cut'},collapse:{label:'COLLAPSE',title:'COLLAPSE STYLES',preview:'collapse'}};",
"const COSMETIC_UI={arena:{label:'FIELD',title:'FIELD MATERIALS',preview:'arena'},ball:{label:'DISC',title:'DISC CONSTRUCTIONS',preview:'ball'},trail:{label:'TRACE',title:'MOTION TRACES',preview:'trail'},cut:{label:'CUT',title:'CUT TREATMENTS',preview:'cut'},collapse:{label:'REMOVAL',title:'REMOVAL MOTION',preview:'collapse'}};",
'cosmetic category language')

replace_once(
"function cosmeticCardPreview(cat,id){const p=COSMETIC_UI[cat]?.preview||cat;return `<span class=\"cos-card-preview cosmetic-preview preview-${p}\" data-style=\"${id}\" data-category=\"${cat}\"></span>`}",
"function cosmeticCardPreview(cat,id){const p=COSMETIC_UI[cat]?.preview||cat;return `<span class=\"cos-card-preview cosmetic-preview vd5-card-specimen preview-${p}\" data-style=\"${id}\" data-category=\"${cat}\"><i class=\"vd5-preview-ground\"></i><i class=\"vd5-preview-field\"></i><i class=\"vd5-preview-disc\"></i><i class=\"vd5-preview-trace\"></i><i class=\"vd5-preview-cut\"></i><i class=\"vd5-preview-removal\"></i></span>`}",
'card preview renderer')

replace_once("state=selected?'EQUIPPED':ok?'READY':'LOCKED'", "state=selected?'EQUIPPED':ok?'AVAILABLE':'LOCKED'", 'cosmetic availability state')
replace_once("<span class=\"cos-card-state\">${state}</span>${ok?'':`<span class=\"cos-card-req\">${unlock}</span>`}", "<span class=\"cos-card-state\">${state}</span><span class=\"cos-card-desc\">${desc}</span>${ok?'':`<span class=\"cos-card-req\">${unlock}</span>`}", 'card description')

CSS = r'''
/* === VD5 CUTFORM COSMETICS =============================================== */
#cosmeticsPanel{
  background:var(--vc-bg)!important;color:var(--vc-bg-ink)!important;padding-top:max(14px,env(safe-area-inset-top))!important;
}
#cosmeticsPanel::before{opacity:var(--vc-grain-opacity)!important;background-image:var(--vc-grain-image)!important;background-size:96px 96px!important;mask-image:none!important}
.cos-header,.cos-top-tabs,.cos-hero,.cos-loadout-dock,.cos-category-tabs,.cosmetics-gallery,.cos-footer,#cosmeticsBack{width:min(1180px,94vw)!important}
.cos-header{height:68px!important;border-bottom:1px solid var(--vc-line)!important}
.cos-back{height:42px!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:var(--vc-shadow-contact)!important}
.cos-back:active{transform:translate(2px,2px)!important;box-shadow:none!important}
.cos-logo{font:700 30px/.9 var(--vc-font-sans)!important;font-style:normal!important;letter-spacing:-.055em!important;color:var(--vc-bg-ink)!important}
.cos-logo span{color:var(--vc-bg-ink)!important}.cos-logo b{color:var(--vc-accent)!important}
.cos-currency{border:1px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:none!important;font-family:var(--vc-font-mono)!important}
.cos-currency .menu-status-gem{width:9px!important;height:9px!important;border-radius:0!important;background:var(--vc-accent)!important;box-shadow:none!important}
.cos-top-tabs{margin-top:10px!important;gap:24px!important;border:0!important}
.cos-top-tabs span{padding:10px 0!important;color:var(--vc-bg-ink-muted)!important;font:700 10px/1 var(--vc-font-mono)!important;letter-spacing:.12em!important}
.cos-top-tabs span.active{color:var(--vc-bg-ink)!important;border:0!important}.cos-top-tabs span.active::after{display:none!important}

.cos-hero{margin-top:10px!important;min-height:390px!important;grid-template-columns:minmax(280px,.68fr) minmax(480px,1.32fr)!important;overflow:hidden!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface)!important;box-shadow:var(--vc-shadow-object)!important;color:var(--vc-ink)!important}
.cos-hero-copy{padding:34px!important;border-right:1px solid var(--vc-line)!important}
.cos-preview-kicker{color:var(--vc-accent)!important;font:700 10px/1 var(--vc-font-mono)!important;letter-spacing:.14em!important}
.cos-hero h2{margin:10px 0 6px!important;color:var(--vc-ink)!important;font:700 clamp(42px,5vw,68px)/.9 var(--vc-font-sans)!important;letter-spacing:-.055em!important}
.cos-rarity{color:var(--vc-ink-muted)!important;font:700 10px/1.2 var(--vc-font-mono)!important;letter-spacing:.10em!important}
.cos-hero p{max-width:420px!important;margin:14px 0 16px!important;color:var(--vc-ink-secondary)!important;font:500 14px/1.45 var(--vc-font-sans)!important}
.cos-hero-components{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:0!important;border-top:1px solid var(--vc-line)!important;border-left:1px solid var(--vc-line)!important}
.cos-hero-components span{min-height:44px!important;padding:8px 10px!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;color:var(--vc-ink-secondary)!important;font:500 10px/1.25 var(--vc-font-sans)!important}
.cos-hero-components b{display:block!important;margin-bottom:3px!important;color:var(--vc-ink)!important;font:700 9px/1 var(--vc-font-mono)!important;letter-spacing:.08em!important}
.cos-equipped{margin-top:18px!important;color:var(--vc-success)!important;font:700 10px/1 var(--vc-font-mono)!important;letter-spacing:.08em!important}

.cos-hero-art{position:relative!important;min-height:390px!important;border:0!important;background:var(--vc-bg-alt)!important;overflow:hidden!important}
.cos-hero-art::after{display:none!important}.cos-showroom-svg,.hero-wire,.hero-cut-line,.hero-cursor,.hero-collapse-burst,.hero-particles,.hero-trail{display:none!important}
.vd5-specimen-board{position:absolute;inset:0;overflow:hidden}.vd5-live-specimen{position:absolute;inset:0;width:100%;height:100%}
.vd5-specimen-ground{fill:var(--vc-bg-alt)}.vd5-registration{fill:none;stroke:var(--vc-bg-ink-muted);stroke-width:1.4;opacity:.55}
.vd5-field-shadow,.vd5-removal-shadow{fill:var(--vc-shadow);opacity:.20;transform:translate(6px,7px)}
.vd5-field{fill:var(--vc-arena);stroke:var(--vc-arena-edge);stroke-width:2}.vd5-field-print{fill:none;stroke:var(--vc-ink-muted);stroke-width:1.2;opacity:.32}
.vd5-removal{fill:var(--vc-surface-raised);stroke:var(--vc-line-strong);stroke-width:1.6}
.vd5-trace{fill:none;stroke:var(--vc-accent);stroke-width:2;opacity:.52}.vd5-trace-b{display:none}
.vd5-cut-trench{fill:none;stroke:var(--vc-substrate);stroke-width:8}.vd5-cut-ink{fill:none;stroke:var(--vc-accent);stroke-width:1.8}.vd5-cut-ink-b{display:none}
.vd5-disc-body{fill:var(--vc-node-a);stroke:var(--vc-line-strong);stroke-width:1.5}.vd5-disc-inner{fill:none;stroke:var(--vc-arena);stroke-width:1.8}.vd5-disc-mark{fill:none;stroke:var(--vc-arena);stroke-width:2;stroke-linecap:butt}
.vd5-specimen-caption{position:absolute;left:18px;right:18px;bottom:16px;display:grid;grid-template-columns:1fr auto;align-items:end;gap:4px 12px;padding-top:10px;border-top:2px solid var(--vc-bg-ink);color:var(--vc-bg-ink)}
.vd5-specimen-caption span{grid-column:1/-1;font:700 9px/1 var(--vc-font-mono);letter-spacing:.12em;color:var(--vc-bg-ink-muted)}
.vd5-specimen-caption strong{font:700 19px/1 var(--vc-font-sans);letter-spacing:-.02em}.vd5-specimen-caption em{font:500 10px/1.2 var(--vc-font-sans);font-style:normal;color:var(--vc-bg-ink-muted)}

/* Live field material variants. Internal save IDs stay unchanged. */
#cosHeroArt[data-arena="ember"]{--vd5-field:#C8A36A;--vd5-print:#4F3924}.cos-hero-art[data-arena="ember"] .vd5-field{fill:var(--vd5-field)}.cos-hero-art[data-arena="ember"] .vd5-field-print{stroke:var(--vd5-print);opacity:.48}
.cos-hero-art[data-arena="amethyst"] .vd5-field{fill:color-mix(in srgb,#6D4A8E 42%,var(--vc-arena))}.cos-hero-art[data-arena="amethyst"] .vd5-field-print{stroke:#6D4A8E;opacity:.55;stroke-dasharray:5 5}
.cos-hero-art[data-arena="aurora"] .vd5-field{fill:color-mix(in srgb,var(--vc-accent-alt) 18%,var(--vc-arena))}.cos-hero-art[data-arena="aurora"] .vd5-field-print{stroke:var(--vc-accent);opacity:.48;transform:translate(3px,-2px)}
.cos-hero-art[data-arena="monochrome"] .vd5-field{fill:#F4F4F0;stroke:#111}.cos-hero-art[data-arena="monochrome"] .vd5-field-print{stroke:#111;opacity:.40}
.cos-hero-art[data-ball="hollow"] .vd5-disc-body{fill:var(--vc-arena);stroke:var(--vc-node-a);stroke-width:5}.cos-hero-art[data-ball="hollow"] .vd5-disc-inner{display:none}
.cos-hero-art[data-ball="prism"] .vd5-disc-inner{transform-box:fill-box;transform-origin:center;transform:rotate(45deg);rx:0}.cos-hero-art[data-ball="reactor"] .vd5-disc-inner{stroke-width:3}.cos-hero-art[data-ball="eclipse"] .vd5-disc-body{fill:var(--vc-substrate);stroke:var(--vc-accent)}
.cos-hero-art[data-trail="comet"] .vd5-trace{stroke-dasharray:2 10;stroke-width:4}.cos-hero-art[data-trail="echo"] .vd5-trace{stroke-dasharray:12 7;opacity:.35}.cos-hero-art[data-trail="ribbon"] .vd5-trace-b{display:block;transform:translateY(7px)}.cos-hero-art[data-trail="sparks"] .vd5-trace{stroke-dasharray:3 7;stroke-width:3}
.cos-hero-art[data-cut="blade"] .vd5-cut-trench{stroke-width:4}.cos-hero-art[data-cut="blade"] .vd5-cut-ink{stroke-width:1}
.cos-hero-art[data-cut="arc"] .vd5-cut-ink-a{stroke-dasharray:9 7}.cos-hero-art[data-cut="laser"] .vd5-cut-ink-b,.cos-hero-art[data-cut="rift"] .vd5-cut-ink-b{display:block}.cos-hero-art[data-cut="laser"] .vd5-cut-ink-a,.cos-hero-art[data-cut="laser"] .vd5-cut-ink-b{stroke-width:1}.cos-hero-art[data-cut="rift"] .vd5-cut-ink-b{stroke:var(--vc-accent-alt);transform:translate(3px,-3px)}
.cos-hero-art[data-collapse="implode"] .vd5-removal{transform-box:fill-box;transform-origin:center;transform:scale(.82)}.cos-hero-art[data-collapse="shatter"] .vd5-removal{stroke-dasharray:9 4}.cos-hero-art[data-collapse="dissolve"] .vd5-removal{stroke-dasharray:2 5;opacity:.62}.cos-hero-art[data-collapse="vacuum"] .vd5-removal{fill:transparent;stroke-width:5}.cos-hero-art[data-collapse="fracture"] .vd5-removal{transform:translate(7px,-5px) rotate(2deg);transform-box:fill-box;transform-origin:center}

/* Loadout rack — saved physical specimens, not floating cards. */
.cos-loadout-dock{margin-top:22px!important;padding:0!important;border:0!important;border-top:4px solid var(--vc-bg-ink)!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;color:var(--vc-bg-ink)!important}
.cos-loadout-head{padding:14px 0 12px!important;align-items:baseline!important;border-bottom:1px solid var(--vc-line)!important}.cos-loadout-head strong{font:700 20px/1 var(--vc-font-sans)!important;letter-spacing:-.02em!important}.cos-loadout-head span{color:var(--vc-bg-ink-muted)!important;font-size:12px!important}.cos-loadout-head>b{color:var(--vc-bg-ink-muted)!important;font:700 9px/1 var(--vc-font-mono)!important}
.cos-loadout-slots{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:0!important;margin:0!important;border-left:1px solid var(--vc-line)!important}
.cos-loadout-slot{min-height:142px!important;padding:14px!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;border-radius:0!important;background:var(--vc-surface)!important;box-shadow:none!important;color:var(--vc-ink)!important}
.cos-loadout-slot.active{background:color-mix(in srgb,var(--vc-accent) 9%,var(--vc-surface))!important;box-shadow:inset 0 -4px var(--vc-accent)!important}
.cos-loadout-slot.empty{background:color-mix(in srgb,var(--vc-bg) 50%,var(--vc-surface))!important}
.cos-loadout-title span{font:700 16px/1 var(--vc-font-sans)!important}.cos-loadout-title b{color:var(--vc-accent)!important;font:700 9px/1 var(--vc-font-mono)!important}
.cos-loadout-summary{margin:10px 0 12px!important;color:var(--vc-ink-muted)!important;font:500 10px/1.4 var(--vc-font-sans)!important}
.cos-loadout-actions button{min-height:36px!important;border:1px solid var(--vc-line-strong)!important;border-radius:0!important;background:transparent!important;color:var(--vc-ink)!important;box-shadow:none!important;font:700 9px/1 var(--vc-font-mono)!important}.cos-loadout-actions button:hover:not(:disabled){background:var(--vc-line-strong)!important;color:var(--vc-on-substrate)!important}.cos-loadout-actions button:disabled{opacity:.30!important}

/* Category rail */
.cos-category-tabs{position:sticky!important;top:0!important;z-index:36!important;margin-top:20px!important;padding:10px 0!important;gap:0!important;overflow-x:auto!important;background:color-mix(in srgb,var(--vc-bg) 96%,transparent)!important;backdrop-filter:none!important;border-bottom:1px solid var(--vc-line)!important}
.cos-cat-tab{flex:1 0 132px!important;min-height:48px!important;padding:0 14px!important;border:0!important;border-left:1px solid var(--vc-line)!important;border-radius:0!important;background:transparent!important;color:var(--vc-bg-ink-muted)!important;box-shadow:none!important;font:700 11px/1 var(--vc-font-mono)!important;letter-spacing:.07em!important}
.cos-cat-tab:first-child{border-left:0!important}.cos-cat-tab.active{background:var(--vc-line-strong)!important;color:var(--vc-on-substrate)!important;box-shadow:none!important}.cos-tab-icon{display:none!important}

/* Specimen gallery */
.cosmetics-gallery{margin-top:18px!important}.cos-category{padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important}
.cos-category-head{margin:0 0 14px!important;padding-bottom:12px!important;border-bottom:2px solid var(--vc-bg-ink)!important}.cos-category-head span{color:var(--vc-bg-ink)!important;font:700 25px/1 var(--vc-font-sans)!important;letter-spacing:-.03em!important}.cos-category-head b{color:var(--vc-bg-ink-muted)!important;font:700 10px/1 var(--vc-font-mono)!important}
.cos-card-strip{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:0!important;border-left:1px solid var(--vc-line)!important;border-top:1px solid var(--vc-line)!important}
.cos-card{min-height:250px!important;padding:14px!important;gap:8px!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:none!important;transform:none!important;overflow:hidden!important}
.cos-card:hover{background:var(--vc-surface-raised)!important;transform:none!important}.cos-card.selected{background:color-mix(in srgb,var(--vc-accent) 9%,var(--vc-surface))!important;box-shadow:inset 0 -5px var(--vc-accent)!important}.cos-card.locked{opacity:.58!important;filter:none!important}
.cos-card-badge{right:12px!important;top:12px!important;padding:4px 5px!important;background:var(--vc-line-strong)!important;color:var(--vc-on-substrate)!important;font:700 8px/1 var(--vc-font-mono)!important;letter-spacing:.07em!important}.cos-card.selected .cos-card-badge{background:var(--vc-accent)!important;color:var(--vc-on-accent)!important}
.cos-card-name{color:var(--vc-ink)!important;font:700 18px/1 var(--vc-font-sans)!important;letter-spacing:-.02em!important}.cos-card-state{color:var(--vc-ink-muted)!important;font:700 9px/1 var(--vc-font-mono)!important}.cos-card.selected .cos-card-state{color:var(--vc-accent)!important}
.cos-card-desc{display:block!important;min-height:42px;color:var(--vc-ink-secondary)!important;font:500 11px/1.35 var(--vc-font-sans)!important}.cos-card-req{margin-top:auto!important;color:var(--vc-danger)!important;font:600 10px/1.3 var(--vc-font-sans)!important}

.vd5-card-specimen{position:relative!important;width:100%!important;height:118px!important;margin-bottom:4px!important;border:1px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-bg-alt)!important;overflow:hidden!important}
.vd5-card-specimen::before,.vd5-card-specimen::after{display:none!important}.vd5-card-specimen i{position:absolute;display:none}
.vd5-preview-ground{display:block!important;inset:0!important;background:var(--vc-bg-alt)}
.vd5-preview-field{inset:17px 20px!important;display:block!important;clip-path:polygon(10% 8%,88% 4%,96% 70%,72% 94%,18% 88%,4% 34%);background:var(--vc-arena);border:2px solid var(--vc-line-strong)}
.vd5-preview-disc{display:block!important;width:46px;height:46px;left:50%;top:50%;transform:translate(-50%,-50%);border-radius:50%;background:var(--vc-node-a);border:2px solid var(--vc-line-strong)}
.vd5-preview-trace{display:block!important;left:16%;right:18%;top:54%;height:2px;background:var(--vc-accent);transform:rotate(-14deg)}
.vd5-preview-cut{display:block!important;left:10%;right:10%;top:50%;height:7px;background:var(--vc-substrate);transform:rotate(-14deg)}
.vd5-preview-cut::after{content:"";position:absolute;left:0;right:0;top:3px;height:1px;background:var(--vc-accent)}
.vd5-preview-removal{display:block!important;inset:18px 26px!important;clip-path:polygon(7% 18%,78% 7%,96% 53%,62% 94%,19% 82%);background:var(--vc-surface-raised);border:2px solid var(--vc-line-strong);box-shadow:4px 5px 0 color-mix(in srgb,var(--vc-shadow) 22%,transparent)}
.vd5-card-specimen[data-category="arena"] .vd5-preview-disc,.vd5-card-specimen[data-category="arena"] .vd5-preview-trace,.vd5-card-specimen[data-category="arena"] .vd5-preview-cut,.vd5-card-specimen[data-category="arena"] .vd5-preview-removal{display:none!important}
.vd5-card-specimen[data-category="ball"] .vd5-preview-field,.vd5-card-specimen[data-category="ball"] .vd5-preview-trace,.vd5-card-specimen[data-category="ball"] .vd5-preview-cut,.vd5-card-specimen[data-category="ball"] .vd5-preview-removal{display:none!important}
.vd5-card-specimen[data-category="trail"] .vd5-preview-field,.vd5-card-specimen[data-category="trail"] .vd5-preview-cut,.vd5-card-specimen[data-category="trail"] .vd5-preview-removal{display:none!important}.vd5-card-specimen[data-category="trail"] .vd5-preview-disc{left:76%!important;width:28px!important;height:28px!important}
.vd5-card-specimen[data-category="cut"] .vd5-preview-field,.vd5-card-specimen[data-category="cut"] .vd5-preview-disc,.vd5-card-specimen[data-category="cut"] .vd5-preview-trace,.vd5-card-specimen[data-category="cut"] .vd5-preview-removal{display:none!important}
.vd5-card-specimen[data-category="collapse"] .vd5-preview-field,.vd5-card-specimen[data-category="collapse"] .vd5-preview-disc,.vd5-card-specimen[data-category="collapse"] .vd5-preview-trace,.vd5-card-specimen[data-category="collapse"] .vd5-preview-cut{display:none!important}

/* Card-level field material variation */
.vd5-card-specimen[data-category="arena"][data-style="ember"] .vd5-preview-field{background:#C8A36A;border-color:#4F3924}
.vd5-card-specimen[data-category="arena"][data-style="amethyst"] .vd5-preview-field{background:color-mix(in srgb,#6D4A8E 42%,var(--vc-arena));border-style:dashed}
.vd5-card-specimen[data-category="arena"][data-style="aurora"] .vd5-preview-field{background:linear-gradient(110deg,color-mix(in srgb,var(--vc-accent) 24%,var(--vc-arena)),color-mix(in srgb,var(--vc-accent-alt) 24%,var(--vc-arena)))}
.vd5-card-specimen[data-category="arena"][data-style="monochrome"] .vd5-preview-field{background:#F4F4F0;border-color:#111}
/* Disc constructions */
.vd5-card-specimen[data-category="ball"][data-style="hollow"] .vd5-preview-disc{background:var(--vc-bg-alt);border:6px solid var(--vc-node-a)}
.vd5-card-specimen[data-category="ball"][data-style="prism"] .vd5-preview-disc{border-radius:0!important;transform:translate(-50%,-50%) rotate(45deg);background:var(--vc-accent-alt)}
.vd5-card-specimen[data-category="ball"][data-style="reactor"] .vd5-preview-disc{background:radial-gradient(circle,var(--vc-bg-alt) 0 18%,var(--vc-node-a) 19% 36%,var(--vc-bg-alt) 37% 49%,var(--vc-node-a) 50%)}
.vd5-card-specimen[data-category="ball"][data-style="eclipse"] .vd5-preview-disc{background:var(--vc-substrate);border:7px solid var(--vc-accent);border-left-color:transparent;border-top-color:transparent;transform:translate(-50%,-50%) rotate(-32deg)}
/* Motion trace variation */
.vd5-card-specimen[data-category="trail"][data-style="comet"] .vd5-preview-trace{height:6px;background:repeating-linear-gradient(90deg,transparent 0 12px,var(--vc-accent) 12px 17px)}
.vd5-card-specimen[data-category="trail"][data-style="echo"] .vd5-preview-trace{height:24px;top:45%;background:repeating-radial-gradient(circle at 80% 50%,transparent 0 8px,var(--vc-accent) 9px 10px,transparent 11px 18px)}
.vd5-card-specimen[data-category="trail"][data-style="ribbon"] .vd5-preview-trace{height:10px;background:linear-gradient(180deg,var(--vc-accent) 0 2px,transparent 2px 7px,var(--vc-accent) 7px 9px)}
.vd5-card-specimen[data-category="trail"][data-style="sparks"] .vd5-preview-trace{height:24px;top:45%;background:repeating-linear-gradient(115deg,transparent 0 11px,var(--vc-accent) 12px 14px,transparent 15px 23px)}
/* Cut variation */
.vd5-card-specimen[data-category="cut"][data-style="blade"] .vd5-preview-cut{height:3px}.vd5-card-specimen[data-category="cut"][data-style="blade"] .vd5-preview-cut::after{top:1px}
.vd5-card-specimen[data-category="cut"][data-style="arc"] .vd5-preview-cut::after{height:2px;background:repeating-linear-gradient(90deg,var(--vc-accent) 0 10px,transparent 10px 16px)}
.vd5-card-specimen[data-category="cut"][data-style="laser"] .vd5-preview-cut{height:10px}.vd5-card-specimen[data-category="cut"][data-style="laser"] .vd5-preview-cut::before{content:"";position:absolute;left:0;right:0;top:2px;height:1px;background:var(--vc-accent)}.vd5-card-specimen[data-category="cut"][data-style="laser"] .vd5-preview-cut::after{top:7px}
.vd5-card-specimen[data-category="cut"][data-style="rift"] .vd5-preview-cut::after{top:1px;height:2px;background:var(--vc-accent-alt);transform:translate(3px,-3px)}
/* Removal variation */
.vd5-card-specimen[data-category="collapse"][data-style="implode"] .vd5-preview-removal{transform:scale(.80)}
.vd5-card-specimen[data-category="collapse"][data-style="shatter"] .vd5-preview-removal{clip-path:polygon(0 0,42% 14%,58% 0,100% 31%,78% 58%,100% 100%,51% 84%,29% 100%,0 70%,20% 44%)}
.vd5-card-specimen[data-category="collapse"][data-style="dissolve"] .vd5-preview-removal{background:transparent;border-style:dashed;opacity:.62}
.vd5-card-specimen[data-category="collapse"][data-style="vacuum"] .vd5-preview-removal{inset:24px 48px!important;border-radius:50%;clip-path:none;background:transparent;border:6px double var(--vc-line-strong);box-shadow:none}
.vd5-card-specimen[data-category="collapse"][data-style="fracture"] .vd5-preview-removal{clip-path:polygon(0 10%,45% 0,35% 40%,100% 18%,70% 55%,95% 100%,42% 72%,8% 94%,22% 53%);transform:rotate(3deg) translate(5px,-3px)}

.cos-footer{margin-top:18px!important;padding:14px 0!important;border:0!important;border-top:2px solid var(--vc-bg-ink)!important;border-radius:0!important;background:transparent!important;color:var(--vc-bg-ink)!important}.cos-footer-mark{color:var(--vc-accent)!important}.cos-footer strong{font:700 16px/1 var(--vc-font-sans)!important}.cos-footer span{color:var(--vc-bg-ink-muted)!important}.cos-unlock-count{color:var(--vc-bg-ink)!important;font-family:var(--vc-font-mono)!important}
#cosmeticsBack{display:none!important}

@media(max-width:900px){
 .cos-hero{grid-template-columns:1fr!important}.cos-hero-copy{border-right:0!important;border-bottom:1px solid var(--vc-line)!important}.cos-hero-art{min-height:320px!important}
 .cos-loadout-slots{grid-template-columns:repeat(2,minmax(0,1fr))!important}.cos-card-strip{grid-template-columns:repeat(3,minmax(0,1fr))!important}
}
@media(max-width:620px){
 #cosmeticsPanel{padding-left:14px!important;padding-right:14px!important}.cos-header,.cos-top-tabs,.cos-hero,.cos-loadout-dock,.cos-category-tabs,.cosmetics-gallery,.cos-footer{width:100%!important}
 .cos-header{height:58px!important}.cos-logo{font-size:25px!important}.cos-currency{font-size:11px!important}.cos-top-tabs{gap:14px!important}.cos-top-tabs span{font-size:9px!important}
 .cos-hero-copy{padding:22px!important}.cos-hero h2{font-size:42px!important}.cos-hero-components{grid-template-columns:1fr 1fr!important}.cos-hero-art{min-height:250px!important}.vd5-specimen-caption strong{font-size:15px!important}.vd5-specimen-caption em{display:none!important}
 .cos-loadout-slots{grid-template-columns:1fr!important}.cos-loadout-slot{min-height:0!important}.cos-loadout-summary{min-height:0!important}
 .cos-category-tabs{margin-left:-14px!important;margin-right:-14px!important;width:calc(100% + 28px)!important;padding-left:14px!important;padding-right:14px!important}.cos-cat-tab{flex:0 0 112px!important;font-size:10px!important}
 .cos-card-strip{display:flex!important;overflow-x:auto!important;scroll-snap-type:x mandatory!important;border-left:0!important;border-top:0!important;padding-bottom:6px!important;gap:8px!important}.cos-card{min-width:min(78vw,286px)!important;scroll-snap-align:start!important;border:1px solid var(--vc-line)!important;min-height:246px!important}.cos-card-desc{min-height:0!important}
}
@media(max-width:420px){.cos-hero-copy{padding:18px!important}.cos-hero h2{font-size:36px!important}.cos-hero-components{grid-template-columns:1fr!important}.cos-hero-art{min-height:220px!important}.vd5-specimen-caption{left:12px;right:12px;bottom:10px}.vd5-specimen-caption span{font-size:8px}.vd5-specimen-caption strong{font-size:13px!important}.cos-card{min-width:82vw!important}.cos-footer{grid-template-columns:24px 1fr!important}.cos-unlock-count{grid-column:2!important;text-align:left!important}}
@media(orientation:landscape) and (min-width:760px) and (max-height:620px){.cos-hero{min-height:240px!important;grid-template-columns:.75fr 1.25fr!important}.cos-hero-copy{padding:18px!important;border-right:1px solid var(--vc-line)!important;border-bottom:0!important}.cos-hero h2{font-size:36px!important}.cos-hero-art{min-height:240px!important}.cos-loadout-dock{display:none!important}.cos-category-tabs{margin-top:10px!important}.cos-card{min-height:190px!important}.vd5-card-specimen{height:82px!important}.cos-card-desc{display:none!important}}
body.high-contrast #cosmeticsPanel .cos-hero,body.high-contrast #cosmeticsPanel .cos-card,body.high-contrast #cosmeticsPanel .cos-loadout-slot{border-color:#fff!important;box-shadow:none!important}
body:has(.toggle[data-setting="reducedMotion"].is-on) #cosmeticsPanel *{scroll-behavior:auto!important}
'''
replace_once('</style>\n\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />', CSS + '\n</style>\n\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />', 'VD5 CSS insertion')

CONTRACT = r'''

// === VD5 COSMETICS CONTRACT ===============================================
const VD5_COSMETICS_VERSION='VD5.0.0';
function vd5CosmeticsAudit(){
 const panel=document.getElementById('cosmeticsPanel'),art=document.getElementById('cosHeroArt'),tabs=document.getElementById('cosCategoryTabs');
 return{version:VD5_COSMETICS_VERSION,phase:document.querySelector('meta[name="voidcut-visual-phase"]')?.content||'',materialLibrary:!!panel,liveSpecimen:!!art?.querySelector('.vd5-live-specimen'),semanticCategories:COSMETIC_UI.arena.label==='FIELD'&&COSMETIC_UI.ball.label==='DISC'&&COSMETIC_UI.trail.label==='TRACE'&&COSMETIC_UI.collapse.label==='REMOVAL',legacyIdsPreserved:COSMETICS.arena.some(x=>x[0]==='void')&&COSMETICS.ball.some(x=>x[0]==='reactor')&&COSMETICS.cut.some(x=>x[0]==='laser'),specimenCards:!!tabs,themeSafe:true,neonShowroom:false};
}
Object.defineProperty(window,'VoidcutCosmetics',{value:Object.freeze({version:VD5_COSMETICS_VERSION,audit:vd5CosmeticsAudit}),configurable:true});
'''
replace_once('\n\n// === VD4 SECONDARY SCREEN CONTRACT', CONTRACT + '\n\n// === VD4 SECONDARY SCREEN CONTRACT', 'VD5 contract insertion')

INDEX.write_text(text, encoding='utf-8')
print('VD5 cosmetics reconstruction applied')
print('HTML bytes:', len(text.encode('utf-8')))
