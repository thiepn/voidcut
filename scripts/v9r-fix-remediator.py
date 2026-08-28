from pathlib import Path

p = Path(__file__).with_name('v9r-remediate.py')
s = p.read_text(encoding='utf-8')
start = s.index('# Tutorial: teach the game, not the complete scoring formula.')
end = s.index('# Reduced Motion: manual preference OR operating-system preference controls canvas decoration.')
block = r'''# Tutorial: teach the game, not the complete scoring formula.
tutorial_start=s.find('function showTutorialScoring(){')
tutorial_end=s.find('\nfunction ',tutorial_start+1)
if tutorial_start<0 or tutorial_end<0:
    raise SystemExit('tutorial scoring simplification: function boundary not found')
new_tutorial="function showTutorialScoring(){tutorialLocked=true;ui.tutorial.innerHTML=`<span class=\"tutorial-kicker\">LESSON 3 / 3 • CLEAR & SCORE</span><strong>Clear at least 75% of a normal field.</strong><br>Bigger cuts score more. Riskier close calls can multiply the score. Dividers create safe setups but score no points.<br><button id=\"tutorialContinue\" class=\"primary\" style=\"width:100%;margin-top:12px\">START RUN</button>`;const btn=$('tutorialContinue');if(btn)btn.addEventListener('click',()=>{if(tutorialMode&&tutorialStage===3)completeInteractiveTutorial()},{once:true});announce('Lesson 3 of 3. Clear at least 75 percent of a normal field. Bigger cuts score more. Riskier close calls can multiply the score. Dividers create safe setups but score no points.')}"
s=s[:tutorial_start]+new_tutorial+s[tutorial_end:]

'''
p.write_text(s[:start] + block + s[end:], encoding='utf-8')
print('Updated tutorial remediation matcher.')
