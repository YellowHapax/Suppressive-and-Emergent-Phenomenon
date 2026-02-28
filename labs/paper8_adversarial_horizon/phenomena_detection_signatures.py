"""Detection Signatures -- Natural vs Adversarial Endemic Baseline

Paper 8: The Suppressive and Emergent Phenomenon

Phenomenon P8c: Compare natural and adversarially-engineered endemic baseline
formation. Identify distinguishing temporal, information-theoretic, and
topological markers that separate the two conditions.

From §5 of the paper, the four distinguishing markers are:

    1. TEMPORAL DISCONTINUITY INDEX
       Natural endemic: H formation is gradual, correlated with developmental
       timeline. Adversarial: discontinuities appear — datable intervention
       points where H formation rate abruptly accelerates.
       Operationalised: variance in the H formation rate time-series, or the
       Kolmogorov–Smirnov statistic comparing early vs late formation windows.

    2. H SPECIFICITY (entropy of blocked-state distribution)
       Natural endemic: uniform expansion (healthy states blocked equally in
       all directions). Adversarial: targeted blocking (specific healthy state
       regions suppressed; others remain accessible).
       Operationalised: Shannon entropy of the blocked-state density. Low
       entropy = high specificity = adversarial signature.

    3. KAPPA-STRATIFICATION RATIO (the most reliable marker)
       SR = κ_within / κ_cross
       where κ_within = mean coupling within the endemic population
             κ_cross  = mean coupling across the boundary to healthy-state agents
       Natural endemic: SR ≈ 1 (κ globally suppressed in all directions).
       Adversarial: SR >> 1 (within-group solidarity preserved; cross-boundary
       coupling systematically destroyed — this is where Re-zeroing would enter).

    4. MUTUAL INFORMATION I(H_agent; social_class)
       Natural endemic: I ≈ 0 (which states an agent hasn't visited is
       uncorrelated with their social position).
       Adversarial: I >> 0 (the healthy states the agent has never visited
       correlate with their position in the social structure).
       Operationalised: empirical mutual information between H_agent size and
       social class label (binary: endemic | healthy group).

DETECTION CRITERION (§5.3):
    Adversarial condition predicted when SR > SR_c.
    SR_c calibrated by Monte Carlo: precision ≥ 0.90 at n=50 agents,
    f_endemic=0.6, random network topology.
    Preliminary conjecture from vector structure: SR_c ≈ 3.5.

CLASSIFIER:
    Binary classification on SR alone (most reliable single marker).
    Predict adversarial iff SR > SR_c.
    Primary metric: precision (adversarial | predicted adversarial) because
    false positives carry the greater conceptual cost here — wrongly labelling
    natural hardship as engineered suppression.
    Target: precision ≥ 0.90 at the calibration conditions.
"""

from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# -- Metadata ------------------------------------------------------------------

PAPER = 8
PAPER_TITLE = "The Suppressive and Emergent Phenomenon"
LAB_TITLE = "Phenomenon P8c: Detection Signatures — Natural vs Adversarial Endemic Baseline"

THESIS = (
    "Natural and adversarial endemic baseline formation are separable on all "
    "four detection metrics. The κ-stratification ratio (SR) is the most "
    "reliable single marker: SR ≈ 1 for natural, SR >> 1 for adversarial. "
    "Monte Carlo calibration yields SR_c ≈ 3.5 for precision ≥ 0.90 at n=50, "
    "f_endemic=0.6."
)

# -- Constants -----------------------------------------------------------------

DEFAULT_N_AGENTS: int = 50               # calibration target
DEFAULT_F_ENDEMIC: float = 0.60          # calibration target
DEFAULT_N_SAMPLES: int = 300             # synthetic sample pool for calibration
DEFAULT_N_STEPS: int = 100               # steps for temporal signature simulation
DEFAULT_N_STATES: int = 100              # state space cardinality

CONJECTURED_SR_C: float = 3.5
SR_C_SWEEP_LOW: float = 0.5
SR_C_SWEEP_HIGH: float = 15.0
SR_C_SWEEP_STEPS: int = 60

RNG_SEED: int = 42


# -- Synthetic sample generation -----------------------------------------------

def _generate_natural_sample(
    n_agents: int,
    f_endemic: float,
    n_states: int,
    n_steps: int,
    rng: np.random.Generator,
) -> Dict[str, Any]:
    """
    Generate one natural endemic baseline realisation.

    Natural endemic:
      - κ globally suppressed (low, roughly uniform in all directions)
      - H forms gradually and unfocused over the developmental timeline
      - No intervention discontinuities
      - SR ≈ 1
      - H specificity low (many directions blocked roughly equally)
    """
    n_endemic = max(1, int(round(f_endemic * n_agents)))
    n_healthy = n_agents - n_endemic

    # κ values: both within-group and cross-boundary draw from the same low distribution
    kappa_within = float(rng.uniform(0.04, 0.18))
    kappa_cross = float(rng.uniform(0.03, 0.16))   # approximately same scale

    SR = kappa_within / max(kappa_cross, 1e-6)

    # H_agent per endemic agent: starts small, grows slowly
    # Natural: small random draw at each step (~developmental stagnation)
    h_agent_trajectories = []
    for _ in range(n_endemic):
        h_t = 0.05
        traj = []
        for _ in range(n_steps):
            h_t = min(1.0, h_t + rng.uniform(0.0, 0.015))  # slow, uniform growth
            traj.append(h_t)
        h_agent_trajectories.append(traj)

    # Temporal: formation rate (Δh per step averaged across endemic agents)
    h_traj_arr = np.array(h_agent_trajectories)  # (n_endemic, n_steps)
    formation_rates = np.diff(h_traj_arr.mean(axis=0))  # (n_steps-1,)
    temporal_discontinuity_index = float(np.var(formation_rates))  # low for natural

    # H specificity: distribution of blocked regions
    # Natural: H is spread across all state regions (high entropy = low specificity)
    # Generate "blocked state" indicators: for each endemic agent, which states are blocked
    blocked_regions = rng.uniform(0, 1, size=(n_endemic, n_states))  # uniform = unstructured
    blocked_entropy = float(-np.sum(
        (blocked_regions / blocked_regions.sum(axis=1, keepdims=True))
        * np.log(blocked_regions / blocked_regions.sum(axis=1, keepdims=True) + 1e-12),
        axis=1
    ).mean())  # high entropy for natural

    # Mutual information I(H_agent_size; social_class)
    # Natural: H_agent sizes for endemic vs healthy should overlap substantially
    final_h_endemic = h_traj_arr[:, -1]
    final_h_healthy = rng.uniform(0.5, 1.0, size=n_healthy) if n_healthy > 0 else np.array([1.0])
    all_h = np.concatenate([final_h_endemic, final_h_healthy])
    all_labels = np.array([0] * n_endemic + [1] * n_healthy)  # 0=endemic, 1=healthy
    mi = _empirical_mutual_information(all_h, all_labels)

    return {
        "condition": "natural",
        "SR": SR,
        "kappa_within": kappa_within,
        "kappa_cross": kappa_cross,
        "temporal_discontinuity_index": temporal_discontinuity_index,
        "h_specificity_entropy": blocked_entropy,
        "mutual_information": mi,
        "mean_final_h_endemic": float(final_h_endemic.mean()),
    }


def _generate_adversarial_sample(
    n_agents: int,
    f_endemic: float,
    n_states: int,
    n_steps: int,
    rng: np.random.Generator,
) -> Dict[str, Any]:
    """
    Generate one adversarially-engineered endemic baseline realisation.

    Adversarial endemic:
      - κ stratified: high within-group, low cross-boundary
      - H forms with temporal discontinuities (intervention events)
      - H is targeted: concentrated in healthy-state regions (low entropy)
      - SR >> 1
      - I(H_agent; social_class) >> 0
    """
    n_endemic = max(1, int(round(f_endemic * n_agents)))
    n_healthy = n_agents - n_endemic

    # κ values: large stratification gap
    kappa_within = float(rng.uniform(0.30, 0.70))   # high within-group solidarity
    kappa_cross = float(rng.uniform(0.02, 0.10))    # cross-boundary suppressed
    SR = kappa_within / max(kappa_cross, 1e-6)

    # H_agent trajectories: contain temporal discontinuities (intervention points)
    intervention_step = int(rng.integers(n_steps // 4, 3 * n_steps // 4))
    h_agent_trajectories = []
    for _ in range(n_endemic):
        h_t = 0.05
        traj = []
        for t in range(n_steps):
            if t == intervention_step:
                # Abrupt block: H_agent growth stops for a few steps, then resumes slowly
                pass  # captured via rate spike
            if t < intervention_step:
                h_t = min(1.0, h_t + rng.uniform(0.0, 0.008))  # slow pre-intervention
            elif t == intervention_step:
                # Discontinuity: growth drops sharply (adversary intervenes)
                h_t = max(0.0, h_t - rng.uniform(0.05, 0.20))   # adversarial rollback
                h_t = min(1.0, h_t)
            else:
                h_t = min(1.0, h_t + rng.uniform(0.0, 0.005))  # very slow post-intervention
            traj.append(h_t)
        h_agent_trajectories.append(traj)

    h_traj_arr = np.array(h_agent_trajectories)
    formation_rates = np.diff(h_traj_arr.mean(axis=0))
    temporal_discontinuity_index = float(np.var(formation_rates))  # high due to spike

    # H specificity:
    # Adversarial: blocked states concentrated in specific regions (healthy states = top half)
    blocked_regions = np.zeros((n_endemic, n_states))
    targeted_start = n_states // 2
    blocked_regions[:, targeted_start:] = rng.uniform(0.5, 1.0, size=(n_endemic, n_states - targeted_start))
    blocked_regions[:, :targeted_start] = rng.uniform(0.0, 0.1, size=(n_endemic, targeted_start))
    row_sums = blocked_regions.sum(axis=1, keepdims=True).clip(min=1e-12)
    p = blocked_regions / row_sums
    blocked_entropy = float(-(p * np.log(p + 1e-12)).sum(axis=1).mean())  # lower entropy

    # Mutual information
    final_h_endemic = h_traj_arr[:, -1]
    final_h_healthy = rng.uniform(0.6, 1.0, size=n_healthy) if n_healthy > 0 else np.array([1.0])
    all_h = np.concatenate([final_h_endemic, final_h_healthy])
    all_labels = np.array([0] * n_endemic + [1] * n_healthy)
    mi = _empirical_mutual_information(all_h, all_labels)

    return {
        "condition": "adversarial",
        "SR": SR,
        "kappa_within": kappa_within,
        "kappa_cross": kappa_cross,
        "temporal_discontinuity_index": temporal_discontinuity_index,
        "h_specificity_entropy": blocked_entropy,
        "mutual_information": mi,
        "mean_final_h_endemic": float(final_h_endemic.mean()),
    }


def _empirical_mutual_information(x: np.ndarray, labels: np.ndarray, n_bins: int = 8) -> float:
    """
    Estimate MI between continuous x and binary label using binned entropy.
    MI(X; Y) = H(X) - H(X|Y).
    """
    if len(x) < 4:
        return 0.0
    bins = np.linspace(x.min() - 1e-9, x.max() + 1e-9, n_bins + 1)

    def _entropy(arr: np.ndarray) -> float:
        if len(arr) == 0:
            return 0.0
        counts, _ = np.histogram(arr, bins=bins)
        total = counts.sum()
        if total == 0:
            return 0.0
        p = counts / total
        return float(-np.sum(p[p > 0] * np.log(p[p > 0])))

    hx = _entropy(x)
    unique_labels = np.unique(labels)
    hx_given_y = 0.0
    for lab in unique_labels:
        mask = labels == lab
        p_y = mask.mean()
        hx_given_y += p_y * _entropy(x[mask])
    return max(0.0, hx - hx_given_y)


# -- SR_c Monte Carlo calibration ----------------------------------------------

def _calibrate_src(
    samples_natural: List[Dict],
    samples_adversarial: List[Dict],
    sr_c_sweep: np.ndarray,
) -> Tuple[float, float, List[Tuple[float, float, float]]]:
    """
    Sweep SR_c and compute precision for each threshold.

    Classifier: predict adversarial iff SR > SR_c.

    Returns: (sr_c_optimal, precision_at_optimal, sweep_results)
    where sweep_results = [(sr_c, precision, recall), ...]
    """
    all_sr = [s["SR"] for s in samples_natural] + [s["SR"] for s in samples_adversarial]
    all_labels = [0] * len(samples_natural) + [1] * len(samples_adversarial)

    sweep_results: List[Tuple[float, float, float]] = []
    best_sr_c = float(sr_c_sweep[0])
    best_precision = 0.0

    for sr_c in sr_c_sweep:
        tp = sum(1 for sr, lab in zip(all_sr, all_labels) if sr > sr_c and lab == 1)
        fp = sum(1 for sr, lab in zip(all_sr, all_labels) if sr > sr_c and lab == 0)
        fn = sum(1 for sr, lab in zip(all_sr, all_labels) if sr <= sr_c and lab == 1)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        sweep_results.append((float(sr_c), precision, recall))

        # Track the lowest SR_c that achieves precision >= 0.90
        if precision >= 0.90 and sr_c < best_sr_c or best_precision < 0.90:
            if precision >= 0.90:
                best_sr_c = float(sr_c)
                best_precision = precision

    return best_sr_c, best_precision, sweep_results


# -- Dataclasses ---------------------------------------------------------------

@dataclass
class MetricSeparation:
    """Separation statistics for a single metric."""
    metric_name: str
    natural_mean: float
    natural_std: float
    adversarial_mean: float
    adversarial_std: float
    cohens_d: float   # effect size


@dataclass
class LabResult:
    """Typed aggregate result for Lab 8.3."""
    natural_samples: List[Dict[str, Any]]
    adversarial_samples: List[Dict[str, Any]]
    metric_separations: List[MetricSeparation]
    sr_c_calibrated: float
    sr_c_precision: float
    sr_c_sweep: List[Tuple[float, float, float]]     # (sr_c, precision, recall)
    params: Dict[str, Any] = field(default_factory=dict)
    conclusion: str = ""

    def summary(self) -> str:
        lines = [
            f"Lab 8.3 — {LAB_TITLE}",
            f"Thesis: {THESIS}",
            "",
            "METRIC SEPARATIONS (natural vs adversarial):",
            f"  {'Metric':<38} {'Nat mean':>10} {'Nat std':>9} {'Adv mean':>10} {'Adv std':>9} {'Cohen d':>9}",
            "-" * 90,
        ]
        for ms in self.metric_separations:
            lines.append(
                f"  {ms.metric_name:<38} {ms.natural_mean:>10.4f} {ms.natural_std:>9.4f} "
                f"{ms.adversarial_mean:>10.4f} {ms.adversarial_std:>9.4f} {ms.cohens_d:>9.3f}"
            )
        lines += [
            "",
            f"SR_c CALIBRATION:",
            f"  Conjectured SR_c ≈ {CONJECTURED_SR_C}",
            f"  Calibrated  SR_c = {self.sr_c_calibrated:.4f}  "
            f"(precision = {self.sr_c_precision:.4f})",
            "",
        ]
        if self.conclusion:
            lines.append(f"Conclusion: {self.conclusion}")
        return "\n".join(lines)


# -- Lab entry point -----------------------------------------------------------

def run(
    n_agents: int = DEFAULT_N_AGENTS,
    f_endemic: float = DEFAULT_F_ENDEMIC,
    n_samples: int = DEFAULT_N_SAMPLES,
    n_steps: int = DEFAULT_N_STEPS,
    n_states: int = DEFAULT_N_STATES,
    rng_seed: int = RNG_SEED,
) -> LabResult:
    """
    Run Lab 8.3: generate synthetic natural and adversarial samples, compute
    all four detection metrics, and calibrate the SR_c detection threshold.

    Parameters
    ----------
    n_agents:
        Population size per sample (calibration target: 50).
    f_endemic:
        Fraction of agents with endemic baseline (calibration target: 0.60).
    n_samples:
        Number of synthetic samples per condition (natural + adversarial).
    n_steps:
        Time steps for temporal signature simulation.
    n_states:
        Cardinality of state space.
    rng_seed:
        Seed for reproducibility.
    """
    rng = np.random.default_rng(rng_seed)

    natural_samples: List[Dict] = []
    adversarial_samples: List[Dict] = []

    for _ in range(n_samples):
        s_rng = np.random.default_rng(rng.integers(0, 2**32))
        natural_samples.append(
            _generate_natural_sample(n_agents, f_endemic, n_states, n_steps, s_rng)
        )
        a_rng = np.random.default_rng(rng.integers(0, 2**32))
        adversarial_samples.append(
            _generate_adversarial_sample(n_agents, f_endemic, n_states, n_steps, a_rng)
        )

    # Compute metric separations
    metrics_config = [
        ("SR (kappa-stratification ratio)", "SR"),
        ("Temporal discontinuity index",    "temporal_discontinuity_index"),
        ("H specificity entropy (low=specific)", "h_specificity_entropy"),
        ("Mutual information I(H_agent; class)", "mutual_information"),
    ]

    metric_separations: List[MetricSeparation] = []
    for metric_label, key in metrics_config:
        nat_vals = np.array([s[key] for s in natural_samples])
        adv_vals = np.array([s[key] for s in adversarial_samples])
        pooled_std = math.sqrt((nat_vals.std() ** 2 + adv_vals.std() ** 2) / 2)
        cohens_d = abs(adv_vals.mean() - nat_vals.mean()) / (pooled_std + 1e-9)
        metric_separations.append(MetricSeparation(
            metric_name=metric_label,
            natural_mean=float(nat_vals.mean()),
            natural_std=float(nat_vals.std()),
            adversarial_mean=float(adv_vals.mean()),
            adversarial_std=float(adv_vals.std()),
            cohens_d=float(cohens_d),
        ))

    # SR_c calibration
    sr_c_values = np.linspace(SR_C_SWEEP_LOW, SR_C_SWEEP_HIGH, SR_C_SWEEP_STEPS)
    sr_c_calibrated, sr_c_precision, sr_c_sweep = _calibrate_src(
        natural_samples, adversarial_samples, sr_c_values
    )

    # Build conclusion
    sr_sep = metric_separations[0]
    all_large_d = all(ms.cohens_d > 1.0 for ms in metric_separations)
    conclusion = (
        f"SR Cohen's d = {sr_sep.cohens_d:.2f} (natural: {sr_sep.natural_mean:.2f}±{sr_sep.natural_std:.2f}, "
        f"adversarial: {sr_sep.adversarial_mean:.2f}±{sr_sep.adversarial_std:.2f}). "
        f"All four metrics {'DO' if all_large_d else 'do NOT all'} achieve d > 1.0. "
        f"Calibrated SR_c = {sr_c_calibrated:.2f} (precision = {sr_c_precision:.3f}) vs "
        f"conjectured SR_c ≈ {CONJECTURED_SR_C}."
    )

    return LabResult(
        natural_samples=natural_samples,
        adversarial_samples=adversarial_samples,
        metric_separations=metric_separations,
        sr_c_calibrated=sr_c_calibrated,
        sr_c_precision=sr_c_precision,
        sr_c_sweep=sr_c_sweep,
        params={
            "n_agents": n_agents,
            "f_endemic": f_endemic,
            "n_samples": n_samples,
            "n_steps": n_steps,
            "n_states": n_states,
            "conjectured_sr_c": CONJECTURED_SR_C,
        },
        conclusion=conclusion,
    )


# -- Plot ----------------------------------------------------------------------

def plot(result: Optional[LabResult] = None, save_path: Optional[str] = None) -> None:
    """
    Plot: (A) SR distributions natural vs adversarial, (B) all four metrics as
    violin/box, (C) SR_c precision-recall sweep with calibrated threshold.

    Parameters
    ----------
    result:
        Output of :func:`run`. If *None*, a default run is performed.
    save_path:
        File path to save figure; if *None*, display interactively.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("[Lab 8.3] matplotlib not available — skipping plot.")
        return

    if result is None:
        result = run()

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.40, wspace=0.35)
    ax_sr = fig.add_subplot(gs[0, 0])
    ax_metrics = fig.add_subplot(gs[0, 1])
    ax_sweep = fig.add_subplot(gs[1, :])

    nat_sr = [s["SR"] for s in result.natural_samples]
    adv_sr = [s["SR"] for s in result.adversarial_samples]

    # (A) SR histograms
    bins = np.linspace(0, max(max(nat_sr), max(adv_sr)) * 1.05, 40)
    ax_sr.hist(nat_sr, bins=bins, alpha=0.6, color="#2ca02c", label="Natural")
    ax_sr.hist(adv_sr, bins=bins, alpha=0.6, color="#d62728", label="Adversarial")
    ax_sr.axvline(result.sr_c_calibrated, color="#ff7f0e", ls="--", lw=1.5,
                  label=f"SR_c = {result.sr_c_calibrated:.2f}")
    ax_sr.axvline(CONJECTURED_SR_C, color="#9467bd", ls=":", lw=1.2,
                  label=f"Conjectured SR_c ≈ {CONJECTURED_SR_C}")
    ax_sr.set_xlabel("κ-stratification ratio (SR)", fontsize=9)
    ax_sr.set_ylabel("Count", fontsize=9)
    ax_sr.set_title("SR Distributions\nNatural vs Adversarial", fontsize=9)
    ax_sr.legend(fontsize=7)
    ax_sr.grid(alpha=0.3)

    # (B) Four metrics Cohen's d bar chart
    metric_names = [ms.metric_name.split("(")[0].strip() for ms in result.metric_separations]
    cohens_ds = [ms.cohens_d for ms in result.metric_separations]
    bar_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
    bars = ax_metrics.barh(metric_names, cohens_ds, color=bar_colors, alpha=0.8)
    ax_metrics.axvline(1.0, color="#888888", ls="--", lw=1, label="d = 1.0 (large effect)")
    ax_metrics.set_xlabel("Cohen's d (effect size)", fontsize=9)
    ax_metrics.set_title("Metric Separations\n(Cohen's d, nat vs adv)", fontsize=9)
    ax_metrics.legend(fontsize=7)
    ax_metrics.grid(alpha=0.3, axis="x")
    for bar, d_val in zip(bars, cohens_ds):
        ax_metrics.text(d_val + 0.05, bar.get_y() + bar.get_height() / 2,
                        f"{d_val:.2f}", va="center", fontsize=8)

    # (C) SR_c precision-recall sweep
    sr_cs = [x[0] for x in result.sr_c_sweep]
    precisions = [x[1] for x in result.sr_c_sweep]
    recalls = [x[2] for x in result.sr_c_sweep]
    ax_sweep.plot(sr_cs, precisions, "-", color="#d62728", lw=2, label="Precision")
    ax_sweep.plot(sr_cs, recalls, "-", color="#1f77b4", lw=2, label="Recall")
    ax_sweep.axhline(0.90, color="#888888", ls=":", lw=1.2, label="Precision target = 0.90")
    ax_sweep.axvline(result.sr_c_calibrated, color="#ff7f0e", ls="--", lw=1.5,
                     label=f"Calibrated SR_c = {result.sr_c_calibrated:.2f} "
                     f"(prec = {result.sr_c_precision:.3f})")
    ax_sweep.axvline(CONJECTURED_SR_C, color="#9467bd", ls=":", lw=1.2,
                     label=f"Conjectured SR_c ≈ {CONJECTURED_SR_C}")
    ax_sweep.set_xlabel("SR threshold (SR_c)", fontsize=10)
    ax_sweep.set_ylabel("Precision / Recall", fontsize=10)
    ax_sweep.set_title(
        f"SR_c Calibration — Precision target ≥ 0.90\n"
        f"n_agents={result.params['n_agents']}, f_endemic={result.params['f_endemic']}, "
        f"n_samples={result.params['n_samples']}",
        fontsize=10,
    )
    ax_sweep.legend(fontsize=8)
    ax_sweep.set_ylim(0, 1.05)
    ax_sweep.grid(alpha=0.3)

    fig.suptitle(
        "Lab 8.3 — Detection Signatures: Natural vs Adversarial Endemic Baseline",
        fontsize=11, fontweight="bold",
    )
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"[Lab 8.3] Figure saved to {save_path}")
    else:
        plt.show()
    plt.close(fig)


# -- CLI -----------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Running {LAB_TITLE}")
    print(f"Thesis: {THESIS}")
    print()
    result = run()
    print(result.summary())
    print()
    print("Generating plot...")
    plot(result)
