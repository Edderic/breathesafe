"""Summarize repeated mask readings without updating production or fitting models."""
import hashlib
from html import escape
import json
from pathlib import Path
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'prompts/zimi-sizing.md'
OUT = ROOT/'prompts'


def stats(readings):
    x = np.asarray(readings, dtype=float)
    return dict(n=len(x), readings=readings, median=float(np.median(x)), mean=float(x.mean()),
                sample_sd=float(x.std(ddof=1)), minimum=float(x.min()), maximum=float(x.max()),
                observed_range=float(np.ptp(x)))


def main():
    raw = SOURCE.read_text()
    catalog = json.loads((OUT/'2026-11-17-nasem/production-zimi-perimeter-context.json').read_text())
    values = {x['name'].replace('Zimi ', '').replace('ZM', ''): x['perimeter_mm'] for x in catalog['products']}
    records = []
    for line in raw.splitlines():
        if not line.strip():continue
        match = re.fullmatch(r'(XS|S|M|L|XL):\s*([^:]+):\s*(?:perimeter:\s*)?(.+?),\s*nose:\s*(.+)', line.strip())
        if not match:raise ValueError('Unrecognized measurement line')
        size, name, perimeter, nose = match.groups()
        record = dict(size=size, model=name, perimeter=stats([float(x.strip()) for x in perimeter.split(',')]),
                      nose=stats([float(x.strip()) for x in nose.split(',')]), production_perimeter_mm=values[name])
        record['median_minus_production_mm'] = record['perimeter']['median']-values[name] if values[name] is not None else None
        records.append(record)
    assert len(records) == 5
    gaps = [dict(from_model=a['model'], to_model=b['model'], median_gap_mm=b['perimeter']['median']-a['perimeter']['median']) for a,b in zip(records, records[1:])]
    evidence = dict(source='prompts/zimi-sizing.md', source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(), units='mm',
        procedure='User confirmed November 15, 2026: repeated readings of the same physical mask/frame per size, following the same perimeter and nose paths as production measurements.',
        records=records, adjacent_perimeter_median_gaps=gaps, sd_definition='Sample standard deviation with n−1 denominator.',
        limitations=['Descriptive within-specimen repeatability, not accuracy against independent ground truth or manufacturing variation.',
            'Numbers of perimeter and nose readings differ for some models; readings are not treated as matched pairs.',
            'No readings were discarded or edited; no confidence intervals inferred from these small repeated-reading sets.',
            'Production values are a November 15 read-only catalog snapshot and were not changed.',
            'Mask arc variability does not establish reconstruction accuracy or an acceptable fit tolerance.'])
    (OUT/'zimi-sizing-summary.json').write_text(json.dumps(evidence, indent=2)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={'width_ratios':[1.4,1]}, constrained_layout=True)
    for ax, field, title, color in zip(axes, ['perimeter','nose'], ['Contact perimeter','Nose path'], ['#087f79','#b86219']):
        for i, row in enumerate(records):
            r=row[field]
            ax.plot([r['minimum'],r['maximum']], [i,i], color='#bdc9c6', lw=4, zorder=1)
            offsets = np.linspace(-.13, .13, r['n'])
            ax.scatter(r['readings'], i+offsets, s=38, color=color, alpha=.85, zorder=3)
            ax.plot([r['median'],r['median']], [i-.23,i+.23], color='#153b40', lw=2, zorder=4)
            if field == 'perimeter' and row['production_perimeter_mm'] is not None:
                ax.scatter([row['production_perimeter_mm']],[i], marker='D',s=42,facecolor='none',edgecolor='#7650a2',linewidth=1.8,zorder=5)
        ax.set_yticks(range(len(records)), [r['size']+' · '+r['model'] for r in records])
        ax.set_ylim(len(records)-.5,-.5)
        ax.set_xlabel('Millimeters')
        ax.set_title(title, loc='left', fontweight='bold', color='#153b40', pad=14)
        ax.grid(axis='x', color='#e4e9e6');ax.set_axisbelow(True)
        for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
        ax.tick_params(axis='y',length=0,pad=10)
    fig.savefig(OUT/'zimi-sizing-measurements.svg', metadata={'Date':None}, facecolor='#ffffff')
    plt.close(fig)
    def table(field):
        rows=''
        for r in records:
            x=r[field]
            comparison=''
            if field=='perimeter':
                value=r['production_perimeter_mm'];delta=r['median_minus_production_mm']
                comparison=f'<td>{value:g}</td><td>{delta:+.0f}</td>' if value is not None else '<td colspan="2">Not recorded</td>'
            rows+=f'<tr><th scope="row">{escape(r["size"]+" · "+r["model"])}</th><td>{x["n"]}</td><td><strong>{x["median"]:g}</strong></td><td>{x["mean"]:.1f}</td><td>{x["minimum"]:g}–{x["maximum"]:g}</td><td>{x["sample_sd"]:.1f}</td>{comparison}</tr>'
        comparison='<th>Production</th><th>Median − production</th>' if field=='perimeter' else ''
        return '<div class="scroll"><table><thead><tr><th>Size · model</th><th>Readings</th><th>Median</th><th>Mean</th><th>Min–max</th><th>SD¹</th>'+comparison+'</tr></thead><tbody>'+rows+'</tbody></table></div>'
    html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Zimi repeated measurements · MasqFit</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f5f4ed;color:#153b40;font:17px/1.5 Arial,sans-serif}main{max-width:1180px;margin:auto;padding:40px 28px}h1{font-size:40px;line-height:1.15;margin:10px 0 18px}h2{font-size:25px;margin:0 0 14px}section{background:white;border:1px solid #d9e1dc;border-radius:8px;padding:24px;margin:24px 0}.eyebrow{color:#087f79;font-size:13px;letter-spacing:.12em;font-weight:bold}.callout{background:#dcebe7;border-left:4px solid #087f79;padding:16px 20px;margin:22px 0}.caution{background:#fff0cc;border-left-color:#a76b00}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:left;padding:12px;border-bottom:1px solid #d9e1dc;white-space:nowrap}thead{background:#e4eeea}td strong{color:#087f79}.note{font-size:14px;color:#55696b}img{display:block;width:100%}a{color:#087f79;text-underline-offset:3px}li{margin:10px 0}@media(max-width:650px){main{padding:24px 16px}h1{font-size:31px}section{padding:16px}.chart{min-width:760px}}@media print{main{padding:0}section{break-inside:avoid}.scroll{overflow:visible}table{font-size:11px}th,td{padding:8px}h1{font-size:30px}}
    </style></head><body><main><div class="eyebrow">MASQFIT · MEASUREMENT CONTEXT · NOVEMBER 15, 2026</div><h1>How repeatable are the mask measurements?</h1>
    <p>Five Zimi models, with repeated readings of the same physical mask/frame for each size. You confirmed the paths match those used for production measurements. All lengths below are in millimeters.</p>
    <div class="callout"><strong>Perimeter medians: 314 → 368 → 392 → 414 → 410 mm.</strong> The measured series does not increase monotonically from L to XL; the individual readings make the overlap visible.</div>
    <section><h2>Every reading, not just the average</h2><div class="scroll"><img class="chart" src="zimi-sizing-measurements.svg" alt="Repeated perimeter and nose-path measurements for five Zimi sizes, with medians and observed ranges."></div><p class="note">Dots: individual readings (vertical offsets separate overlaps). Dark tick: median. Gray line: observed min–max. Purple outlined diamond: production perimeter, where recorded. Ranges are not confidence intervals.</p></section>
    <section><h2>Perimeter readings</h2>PERIMETER<p class="note">¹Sample SD, with n−1 denominator. Production values are a read-only November 15 snapshot. 8210 and B95-XL have no perimeter recorded in production. No readings were discarded.</p></section>
    <section><h2>Nose-path readings</h2>NOSE<p class="note">Perimeter and nose counts differ for 7711 and B95-XL; we do not assume the readings are paired. Production has no directly comparable nose-path values in this snapshot.</p></section>
    <section><h2>What this means for a measurement-error budget</h2><ul>
    <li><strong>Reference repeatability matters.</strong> 7711 perimeter readings span 30 mm; B95-XL spans 28 mm. That is variability in remeasuring the same specimen, not evidence of manufacturing variation.</li>
    <li><strong>The repeated median S-to-M gap is 24 mm.</strong> XS-to-S is 54 mm; M-to-L is 22 mm. L-to-XL is −4 mm, with broad overlap. Some readings overlap between neighboring groups.</li>
    <li><strong>The old 14 mm catalog gap needs qualification.</strong> Compared with production, the 95S, 7711 and 9233 medians are higher by 14, 18 and 28 mm. These differences are not a single common offset.</li>
    <li><strong>Nose geometry adds separate context.</strong> B95-XL’s nose median is 48 mm, compared with 62 mm for 8210, despite similar perimeter medians. This is consistent with measuring nose geometry separately; it does not itself validate a prediction model.</li>
    </ul></section>
    <div class="callout caution"><strong>Repeatability is not accuracy.</strong> These repeats cannot establish the true perimeter, reconstruction error, or a universally acceptable fit tolerance. A 2–5 mm algorithm target needs independently repeatable reference paths; width/length checks do not establish full-arc accuracy.</div>
    <section><h2>Practical next step</h2><p>Document the contact path and tape tension, keep the frame condition consistent, and compare repeated readings across sessions or raters. Preserve every reading while investigating the 7711 spread and L/XL overlap. Use a clearly defined reference protocol before treating the medians as ground truth or replacing production values.</p></section>
    <footer class="note"><a href="zimi-sizing.md">Original readings</a> · <a href="zimi-sizing-summary.json">Statistics and provenance</a> · <a href="zimi-sizing-measurements.svg">Exportable chart</a><p>Source readings are unchanged. Production data and model training were not modified.</p></footer></main></body></html>'''
    (OUT/'zimi-sizing.html').write_text(html.replace('PERIMETER',table('perimeter')).replace('NOSE',table('nose')))
    print(OUT/'zimi-sizing.html')


if __name__=='__main__':main()
