"""Article figures from the raw GDELT scan (no manual edits)."""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'scripts'))
from gdelt_map_png import render
D = R / 'makale'
D.mkdir(exist_ok=True)
snap = json.loads((R / 'research/gdelt/GDELT_HARITA_VERISI.json').read_text())
daily = snap['daily']
x = [f"{r['day'][6:]}.{r['day'][4:6]}" for r in daily]
y = [r['matches'] for r in daily]
rate = [r['matches'] / r['all_articles'] * 1e5 if r['all_articles'] else 0 for r in daily]
plt.rcParams['font.family'] = 'DejaVu Sans'
fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=220)
ax.bar(range(len(y)), y, color=['#b02d26' if r['day'] == '20220927' else '#7fa8cc' for r in daily])
ax.set_xticks(range(len(x)))
ax.set_xticklabels(x, rotation=90, fontsize=7)
ax.set_ylabel('Eşleşen tekil haber (gün)', fontsize=8)
ax2 = ax.twinx()
ax2.plot(range(len(rate)), rate, color='#10253c', lw=1.4, marker='o', ms=2)
ax2.set_ylabel('100.000 GKG kaydı başına', fontsize=8)
for a in (ax, ax2):
    a.tick_params(labelsize=7)

fig.tight_layout()
fig.savefig(D / 'sekil1_gunluk_dagilim.png')
render(snap, D / 'sekil2_harita.png', width_in=7.2, height_in=3.9)
print('ok')
