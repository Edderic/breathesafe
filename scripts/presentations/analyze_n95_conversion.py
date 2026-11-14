"""Revisit the saved April 2025 conversion notebook output; no database access.

Fits a Bayesian censored log-linear association to the 24 mask aggregates with
measured N99/N95 results. Assigned score-1 rows are excluded. This is a one-person,
selected historical comparison, not a held-out evaluation or a new converter.
"""
import hashlib
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from scipy.special import log_ndtr
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / 'python/mask_recommender/notebooks/inferring-n95-mode-fit-factors.ipynb'
DECK = ROOT / 'prompts/2026-11-17-nasem'


class SavedTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th'):
            self.cell = ''

    def handle_data(self, text):
        if self.cell is not None:
            self.cell += text

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(self.cell.strip())
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def extract_pairs(notebook):
    cells = notebook['cells']
    matches = [i for i, cell in enumerate(cells)
               if "overall_ffs_without_talking.sort_values(" in ''.join(cell.get('source', []))]
    if len(matches) != 1:
        raise ValueError('Expected one saved aggregate comparison table')
    index = matches[0]
    html = ''.join(cells[index]['outputs'][0]['data']['text/html'])
    table = SavedTable()
    table.feed(html)
    headers = table.rows[0][1:]
    assigned_cells = [c for c in cells if 'not_good_fit_df = assume_ff_1_since_no_fit' in ''.join(c.get('source', []))]
    if len(assigned_cells) != 1:
        raise ValueError('Expected the notebook assigned-score table')
    assigned_table = SavedTable()
    assigned_table.feed(''.join(assigned_cells[0]['outputs'][0]['data']['text/html']))
    assigned_names = {row[1] for row in assigned_table.rows[1:]}
    points, excluded = [], 0
    for row in table.rows[2:]:
        values = dict(zip(headers, row[1:]))
        pure_assigned = (values['fit_factor_n99'] == 'NaN'
                         and float(values['actual_fit_factor_n95']) == 1
                         and float(values['clipped_predicted_fit_factor_n95']) == 1)
        if row[0] in assigned_names or pure_assigned:
            # Exclude the whole aggregate if it contains assigned observations,
            # including one mask that pools assigned and measured exercises.
            excluded += 1
            continue
        if values['fit_factor_n99'] == 'NaN':
            raise ValueError('Unexplained missing measured N99 aggregate')
        actual = float(values['actual_fit_factor_n95'])
        predicted = float(values['clipped_predicted_fit_factor_n95'])
        if not (0 < actual <= 200 and 0 < predicted <= 200):
            raise ValueError('Saved scores outside the expected plotting range')
        points.append({'measured_n95': actual, 'conversion_estimate': predicted})
    if not points:
        raise ValueError('No measured pairs')
    return points, excluded, index, html


def log_posterior(theta, x, y, censored):
    """alpha at estimate=100; beta slope; theta[2] = log(sigma).

    log10(measured N95) ~ Normal(alpha + beta*log10(estimate/100), sigma).
    Values of measured N95=200 are lower bounds (right censoring).
    alpha~N(2,1), beta~N(0,1), sigma~HalfNormal(.75), with Jacobian.
    The capped conversion estimate is a fixed covariate, not latent true fit.
    """
    theta = np.atleast_2d(theta)
    alpha, beta, log_sigma = theta.T
    sigma = np.exp(log_sigma)
    mu = alpha[:, None] + beta[:, None] * x
    z = (y - mu) / sigma[:, None]
    likelihood = np.where(censored, log_ndtr(-z),
                          -.5*z*z - log_sigma[:, None] - .5*np.log(2*np.pi)).sum(axis=1)
    prior = -.5*(alpha-2)**2 - .5*beta**2 - .5*(sigma/.75)**2 + log_sigma
    return likelihood + prior


def diagnostics(chains):
    # Split-chain R-hat and conservative initial-positive-pair autocorrelation ESS.
    n = chains.shape[1] // 2
    split = np.concatenate([chains[:, :n], chains[:, -n:]], axis=0)
    within = np.var(split, axis=1, ddof=1).mean(axis=0)
    between = n*np.var(split.mean(axis=1), axis=0, ddof=1)
    variance = (n-1)/n*within + between/n
    rhat = np.sqrt(variance/within)
    centered = split - split.mean(axis=1, keepdims=True)
    fft = np.fft.rfft(centered, n=2*n, axis=1)
    acov = np.fft.irfft(fft*np.conjugate(fft), axis=1)[:, :n].real / n
    rho = 1 - (within - acov.mean(axis=0))/variance
    ess = []
    for j in range(3):
        pairs = rho[1:n-1:2, j] + rho[2:n:2, j]
        stop = next((i for i, value in enumerate(pairs) if value < 0), len(pairs))
        positive = np.minimum.accumulate(pairs[:stop])
        ess.append(float(min(split.shape[0]*n, split.shape[0]*n/(1+2*positive.sum()))))
    return rhat, ess


def sample_posterior(x, y, censored, seed=20261113, warmup=5000, draws=15000):
    rng = np.random.default_rng(seed)
    objective = lambda t: -float(log_posterior(t, x, y, censored)[0])
    optimum = minimize(objective, [2., .5, -1.], method='BFGS', tol=1e-8)
    if not np.isfinite(optimum.fun):
        raise ValueError('MAP initialization failed')
    # Finite-difference Hessian gives a stable proposal covariance.
    steps = np.eye(3)*1e-4
    hessian = np.empty((3, 3))
    for i in range(3):
        for j in range(3):
            hessian[i, j] = (objective(optimum.x+steps[i]+steps[j])
                             - objective(optimum.x+steps[i]-steps[j])
                             - objective(optimum.x-steps[i]+steps[j])
                             + objective(optimum.x-steps[i]-steps[j]))/(4e-8)
    proposal = np.linalg.cholesky(np.linalg.inv(hessian))
    current = optimum.x + rng.normal(size=(4, 3)) @ proposal.T
    logp = log_posterior(current, x, y, censored)
    chains = np.empty((4, draws, 3))
    scale, accepted, batches = 2.38/np.sqrt(3), np.zeros(4), np.zeros(4)
    for iteration in range(warmup+draws):
        candidate = current + scale*rng.normal(size=(4, 3)) @ proposal.T
        candidate_logp = log_posterior(candidate, x, y, censored)
        accept = np.log(rng.random(4)) < candidate_logp-logp
        current[accept], logp[accept] = candidate[accept], candidate_logp[accept]
        if iteration < warmup:
            batches += accept
            if (iteration+1) % 100 == 0:
                scale *= np.exp(.25*(batches.mean()/100-.28))
                batches[:] = 0
        else:
            chains[:, iteration-warmup] = current
            accepted += accept
    rhat, ess = diagnostics(chains)
    if max(rhat) > 1.01 or min(ess) < 500:
        raise ValueError(f'Insufficient mixing: R-hat {rhat}; ESS {ess}')
    return chains.reshape(-1, 3), {'split_rhat': rhat.tolist(), 'ess': ess,
                                 'acceptance': (accepted/draws).tolist(),
                                 'chains': 4, 'warmup_per_chain': warmup,
                                 'draws_per_chain': draws, 'seed': seed}


def main():
    raw = NOTEBOOK.read_bytes()
    points, excluded, cell, html = extract_pairs(json.loads(raw))
    actual = np.array([p['measured_n95'] for p in points])
    predicted = np.array([p['conversion_estimate'] for p in points])
    x, y, censored = np.log10(predicted/100), np.log10(actual), actual >= 200
    posterior, diagnostic = sample_posterior(x, y, censored)
    grid = np.geomspace(predicted.min(), predicted.max(), 180)
    mu = posterior[:, 0, None] + posterior[:, 1, None]*np.log10(grid/100)
    typical = 10**np.quantile(mu, [.025, .5, .975], axis=0)
    rng = np.random.default_rng(20261114)
    individual = 10**np.quantile(mu + np.exp(posterior[:, 2, None])*rng.normal(size=mu.shape),
                               [.025, .975], axis=0)
    interval = np.quantile(posterior[:, 1], [.025, .5, .975]).tolist()
    stats = {
        'notebook': str(NOTEBOOK.relative_to(ROOT)), 'notebook_sha256': hashlib.sha256(raw).hexdigest(),
        'saved_cell_index': cell, 'saved_table_sha256': hashlib.sha256(html.encode()).hexdigest(),
        'people': 1, 'mask_aggregates': len(points), 'excluded_assigned_or_mixed_mask_aggregates': excluded,
        'measured_at_ceiling': int(censored.sum()), 'conversion_at_ceiling': int((predicted >= 200).sum()),
        'points': points, 'log10_slope_quantiles_2_5_50_97_5': interval,
        'posterior_probability_positive_slope': float((posterior[:, 1] > 0).mean()),
        'spearman_displayed_scores': float(spearmanr(actual, predicted).statistic),
        'model': 'log10(measured N95) ~ Normal(alpha + beta*log10(capped conversion estimate/100), sigma); measured 200 is right-censored',
        'priors': 'alpha ~ Normal(2,1); beta ~ Normal(0,1); sigma ~ HalfNormal(.75)',
        'sampler': 'Four-chain random-walk Metropolis; MAP Hessian proposal; scale adapts only during warmup',
        'diagnostics': diagnostic,
        'limitations': [
            'Saved, six-decimal notebook outputs; not a rerun against raw records.',
            'One author, selected mask aggregates; not independent people or held-out validation.',
            'Notebook excludes selected N95 tests based on author interpretation and pools repeated tests/exercises by mask.',
            'Twelve mask aggregates containing assigned observations are excluded (11 pure-assigned and one mixed); historical sensitivity/specificity must not be reused for this subset.',
            'Conversion estimates were exercise-clipped at 200 before harmonic aggregation; this is a fixed, capped predictor.',
            'Response censoring is modeled; predictor error, filtration uncertainty, correlated measurements and selection are not.',
            'Notebook documents a factor-2 bias adjustment; exact historical runtime state cannot be reconstructed from outputs alone.',
            'Current production conversion pools filtration references differently; this plot does not validate that exact pipeline.',
            'Posterior intervals are conditional on this model and these data, not population accuracy guarantees.'
        ],
    }
    output = DECK/'n95-conversion-evidence.json'
    output.write_text(json.dumps(stats, indent=2, allow_nan=False)+'\n')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'svg.fonttype': 'path'})
    fig, ax = plt.subplots(figsize=(12.5, 4.0), layout='constrained')
    fig.patch.set_facecolor('#f5f4ed')
    ax.set_facecolor('#ffffff')
    ax.fill_between(grid, individual[0], individual[1], color='#087f79', alpha=.13,
                    label='95% posterior predictive interval')
    ax.fill_between(grid, typical[0], typical[2], color='#087f79', alpha=.30,
                    label='95% credible interval: median trend')
    ax.plot(grid, typical[1], color='#087f79', lw=2.5, label='Bayesian median trend')
    ax.plot([35, 230], [35, 230], '--', color='#6b7778', lw=1.3, label='Agreement: measured = estimated')
    counts = Counter(zip(predicted, actual))
    for (estimate, observed), count in counts.items():
        ax.scatter(estimate, observed, s=45+20*(count-1), marker='^' if observed >= 200 else 'o',
                   color='#153b40', edgecolor='white', lw=.8, zorder=5)
    ax.axvline(100, color='#b37a40', lw=1, ls=':')
    ax.axhline(100, color='#b37a40', lw=1, ls=':')
    ax.axhline(200, color='#7b8a8b', lw=.8, ls=':')
    ax.annotate(f'{counts[(200., 200.)]} aggregates overlap at (200, ≥200)', xy=(200, 200), xytext=(68, 390),
                fontsize=10, arrowprops={'arrowstyle': '-', 'color': '#55696b'})
    ax.set(xscale='log', yscale='log', xlim=(38, 230), ylim=(5, max(1100, individual.max()*1.05)),
           xlabel='N95-mode estimate from N99 + filtration (capped at 200)',
           ylabel='Measured N95-mode fit factor (200 = ceiling)')
    from matplotlib.ticker import FixedLocator, FixedFormatter
    ax.xaxis.set_major_locator(FixedLocator([40, 60, 100, 150, 200]))
    ax.xaxis.set_major_formatter(FixedFormatter(['40', '60', '100', '150', '200']))
    ax.yaxis.set_major_locator(FixedLocator([10, 30, 100, 200, 500, 1000]))
    ax.yaxis.set_major_formatter(FixedFormatter(['10', '30', '100', '200', '500', '1000']))
    ax.tick_params(which='minor', labelbottom=False, labelleft=False)
    ax.grid(which='major', alpha=.16)
    ax.legend(loc='upper left', fontsize=9, framealpha=.95)
    fig.savefig(DECK/'assets/n95-conversion-uncertainty.svg', metadata={'Date': None})
    svg = DECK/'assets/n95-conversion-uncertainty.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(DECK/'assets/n95-conversion-uncertainty.png', dpi=180)
    plt.close(fig)
    print(json.dumps({k:stats[k] for k in ['mask_aggregates', 'excluded_assigned_or_mixed_mask_aggregates',
          'measured_at_ceiling', 'log10_slope_quantiles_2_5_50_97_5', 'diagnostics']}, indent=2))


if __name__ == '__main__':
    main()
