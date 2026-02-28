"""Kappa-Collapse and Re-Zeroing Cascade -- Population-Level Coupling Dynamics

Paper 8: The Suppressive and Emergent Phenomenon

Phenomenon P8b: A population model at varying κ (inter-agent coupling) densities.
Identifies κ_c, the critical coupling threshold below which collective re-zeroing
fails to propagate even when individual re-zeroing events occur.

Theoretical basis (Aleph-4 Checkpoint, §4):

    A critical coupling threshold κ_c exists, analogous to the Kuramoto
    synchronization threshold. Below κ_c: individual re-zeroing succeeds but
    cannot propagate. Above κ_c: social contagion of healthy-state representation
    cascades. The adversarial system must maintain κ < κ_c continuously,
    requiring sustained energy expenditure against the population's natural
    gradient toward H_agent expansion. Any lapse in suppression allows the
    cascade. The system is METASTABLE: it persists only so long as it is
    actively maintained.

MODEL:

    n_agents agents are distributed on a network (random, scale-free, or
    stratified topology). Fraction f_endemic start with endemic baseline
    (H_agent ≈ 0, cannot self-expand). The remaining 1 - f_endemic agents
    have healthy-state representation (H_agent ≈ 1, serve as seeds for
    the Re-zeroing cascade).

    At each time-step:
      - For each endemic agent i:
        - With probability κ_ij * healthy_fraction_of_neighbours_i, agent i
          receives a Re-zeroing input that expands its H_agent by Δ.
        - If H_agent_i exceeds re-zeroing threshold (θ_rz), agent i transitions
          to healthy state and can in turn propagate to its neighbours.

    The cascade saturates when no new re-zeroing events occur.

    Sweep: κ_mean over [κ_low, κ_high] with n_steps_grid values.
    For each κ, run n_trials Monte Carlo replicates and record:
        - final_rezeroed_fraction: fraction of initially-endemic agents that
          achieved re-zeroing by end of simulation
        - cascade_occurred: True if final_rezeroed_fraction > 0.50

    Phase transition κ_c identified as the κ at which cascade_occurred first
    becomes consistently True across Monte Carlo replicates.

TOPOLOGIES:
    random     -- Erdős–Rényi G(n, p), p chosen so mean degree = kappa_mean * n
    scale_free -- Barabási–Albert with mean degree ≈ kappa_mean * n
    stratified -- Two communities; within-community p_in > p_out; models
                  adversarially engineered κ-stratification (high within-group
                  coupling, low cross-boundary coupling)
"""

from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

# -- Metadata ------------------------------------------------------------------

PAPER = 8
PAPER_TITLE = "The Suppressive and Emergent Phenomenon"
LAB_TITLE = "Phenomenon P8b: Kappa-Collapse and Re-Zeroing Cascade"

THESIS = (
    "A phase transition at κ_c exists: below it, individual re-zeroing events "
    "are stable but isolated and do not propagate through the population. Above "
    "κ_c, a cascade of H_agent expansion sweeps the network. The adversarial "
    "system must continuously maintain κ < κ_c to prevent this cascade — the "
    "configuration is metastable."
)

# -- Defaults ------------------------------------------------------------------

DEFAULT_N_AGENTS: int = 80
DEFAULT_F_ENDEMIC: float = 0.70
DEFAULT_KAPPA_MEAN: float = 0.10       # baseline single-run κ
DEFAULT_TOPOLOGY: str = "random"
DEFAULT_N_TRIALS: int = 40
DEFAULT_N_STEPS: int = 100
DEFAULT_KAPPA_LOW: float = 0.02
DEFAULT_KAPPA_HIGH: float = 0.40
DEFAULT_KAPPA_GRID_STEPS: int = 30
DEFAULT_DELTA_H: float = 0.25         # H_agent increase per successful Re-zeroing step
DEFAULT_THETA_RZ: float = 0.60        # H_agent threshold for healthy-state transition
RNG_SEED: int = 42


# -- Network builders ----------------------------------------------------------

def _build_random_network(n: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Erdős–Rényi adjacency matrix."""
    adj = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i, j] = 1.0
                adj[j, i] = 1.0
    return adj


def _build_scale_free_network(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """Barabási–Albert preferential attachment (m edges per new node)."""
    m = max(1, min(m, n - 1))
    adj = np.zeros((n, n), dtype=float)
    # seed with complete graph on m+1 nodes
    for i in range(m + 1):
        for j in range(i + 1, m + 1):
            adj[i, j] = 1.0
            adj[j, i] = 1.0
    degrees = adj.sum(axis=1)
    for i in range(m + 1, n):
        degrees_sum = degrees.sum()
        if degrees_sum == 0:
            probs = np.ones(i) / i
        else:
            probs = degrees[:i] / degrees_sum
        targets = rng.choice(i, size=min(m, i), replace=False, p=probs)
        for t in targets:
            adj[i, t] = 1.0
            adj[t, i] = 1.0
        degrees[i] = len(targets)
        for t in targets:
            degrees[t] += 1.0
    return adj


def _build_stratified_network(
    n: int, p_in: float, p_out: float, rng: np.random.Generator
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Two-community stochastic block model.
    Returns (adjacency, community_labels).
    High p_in / low p_out models adversarial κ-stratification:
    within-group coupling high, cross-boundary coupling suppressed.
    """
    labels = np.zeros(n, dtype=int)
    n_community_a = n // 2
    labels[n_community_a:] = 1
    adj = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            same = labels[i] == labels[j]
            p = p_in if same else p_out
            if rng.random() < p:
                adj[i, j] = 1.0
                adj[j, i] = 1.0
    return adj, labels


# -- Single-trial simulation ---------------------------------------------------

def _simulate_trial(
    kappa_mean: float,
    n_agents: int,
    f_endemic: float,
    topology: str,
    n_steps: int,
    delta_h: float,
    theta_rz: float,
    rng: np.random.Generator,
) -> Dict[str, Any]:
    """
    Run one Monte Carlo trial.

    Returns dict with:
      final_rezeroed_fraction: fraction of initially-endemic agents that re-zeroed
      h_agent_trajectory: mean H_agent across all agents at each time step
      cascade_occurred: bool (> 50% of endemic agents re-zeroed)
    """
    n_endemic = max(1, int(round(f_endemic * n_agents)))
    n_healthy = n_agents - n_endemic

    # H_agent initialisation
    h_agent = np.zeros(n_agents, dtype=float)
    endemic_idx = rng.choice(n_agents, size=n_endemic, replace=False)
    healthy_idx = np.setdiff1d(np.arange(n_agents), endemic_idx)
    h_agent[endemic_idx] = 0.05  # endemic: near-zero representation
    h_agent[healthy_idx] = 1.00  # healthy: full representation

    initially_endemic = set(endemic_idx.tolist())
    healthy_set = set(healthy_idx.tolist())

    # Build network
    if topology == "random":
        p_edge = kappa_mean  # treat kappa_mean as edge probability directly
        adj = _build_random_network(n_agents, p_edge, rng)
    elif topology == "scale_free":
        m = max(1, int(kappa_mean * n_agents / 2))
        adj = _build_scale_free_network(n_agents, m, rng)
    elif topology == "stratified":
        p_in = min(0.99, kappa_mean * 2.5)
        p_out = max(0.001, kappa_mean * 0.2)
        adj, _ = _build_stratified_network(n_agents, p_in, p_out, rng)
    else:
        p_edge = kappa_mean
        adj = _build_random_network(n_agents, p_edge, rng)

    # Degree vector for normalisation
    degrees = adj.sum(axis=1).clip(min=1.0)

    trajectory: List[float] = []

    for _ in range(n_steps):
        new_transitions: List[int] = []
        for i in endemic_idx:
            if i in healthy_set:
                continue  # already re-zeroed
            neighbours = np.where(adj[i] > 0)[0]
            if len(neighbours) == 0:
                continue
            # Fraction of neighbours who are in healthy_set
            frac_healthy_neighbours = sum(1 for nb in neighbours if nb in healthy_set) / len(neighbours)
            # Coupling probability: kappa_ij * healthy_fraction
            coupling_prob = kappa_mean * frac_healthy_neighbours
            if rng.random() < coupling_prob:
                h_agent[i] = min(1.0, h_agent[i] + delta_h)
                if h_agent[i] >= theta_rz:
                    new_transitions.append(i)

        for i in new_transitions:
            healthy_set.add(i)

        trajectory.append(float(np.mean(h_agent)))

    rezeroed_count = len(initially_endemic & healthy_set)
    final_rezeroed_fraction = rezeroed_count / n_endemic if n_endemic > 0 else 0.0

    return {
        "final_rezeroed_fraction": final_rezeroed_fraction,
        "h_agent_trajectory": trajectory,
        "cascade_occurred": final_rezeroed_fraction > 0.50,
    }


# -- Dataclasses ---------------------------------------------------------------

@dataclass
class KappaGridPoint:
    """Results for a single κ value in the sweep."""
    kappa_mean: float
    mean_rezeroed_fraction: float
    cascade_probability: float   # fraction of trials where cascade occurred
    trials: int


@dataclass
class LabResult:
    """Typed aggregate result for Lab 8.2."""
    kappa_grid: List[KappaGridPoint]
    kappa_c: Optional[float]          # estimated critical coupling
    topology: str
    n_agents: int
    f_endemic: float
    n_trials: int
    single_run_trajectory: List[float]  # mean H_agent(t) for default kappa_mean
    params: Dict[str, Any] = field(default_factory=dict)
    conclusion: str = ""

    def summary(self) -> str:
        lines = [
            f"Lab 8.2 — {LAB_TITLE}",
            f"Thesis: {THESIS}",
            "",
            f"  Topology: {self.topology}   n_agents: {self.n_agents}   "
            f"f_endemic: {self.f_endemic}   n_trials: {self.n_trials}",
            "",
            f"  Estimated κ_c = {self.kappa_c:.4f}" if self.kappa_c is not None else "  κ_c: not identified in sweep range",
            "",
            f"{'κ':>8} {'Mean re-zeroed':>16} {'Cascade prob':>14}",
            "-" * 42,
        ]
        # Sample every ~5th point for readability
        step = max(1, len(self.kappa_grid) // 15)
        for gp in self.kappa_grid[::step]:
            lines.append(
                f"  {gp.kappa_mean:>6.4f}  {gp.mean_rezeroed_fraction:>14.4f}"
                f"  {gp.cascade_probability:>12.4f}"
            )
        if self.conclusion:
            lines += ["", f"Conclusion: {self.conclusion}"]
        return "\n".join(lines)


# -- Lab entry point -----------------------------------------------------------

def run(
    n_agents: int = DEFAULT_N_AGENTS,
    f_endemic: float = DEFAULT_F_ENDEMIC,
    kappa_mean: float = DEFAULT_KAPPA_MEAN,
    topology: str = DEFAULT_TOPOLOGY,
    n_trials: int = DEFAULT_N_TRIALS,
    n_steps: int = DEFAULT_N_STEPS,
    kappa_low: float = DEFAULT_KAPPA_LOW,
    kappa_high: float = DEFAULT_KAPPA_HIGH,
    kappa_grid_steps: int = DEFAULT_KAPPA_GRID_STEPS,
    delta_h: float = DEFAULT_DELTA_H,
    theta_rz: float = DEFAULT_THETA_RZ,
    rng_seed: int = RNG_SEED,
) -> LabResult:
    """
    Sweep κ_mean over [kappa_low, kappa_high] and identify the phase transition κ_c.

    Parameters
    ----------
    n_agents:
        Population size.
    f_endemic:
        Fraction of agents initialised with endemic baseline.
    kappa_mean:
        Mean inter-agent coupling for the default single-run trajectory.
    topology:
        Network structure: ``'random'``, ``'scale_free'``, or ``'stratified'``.
    n_trials:
        Monte Carlo replicates per κ value.
    n_steps:
        Simulation duration per trial.
    kappa_low, kappa_high:
        Sweep range for κ_mean.
    kappa_grid_steps:
        Number of grid points in κ sweep.
    delta_h:
        H_agent increment per successful Re-zeroing coupling event.
    theta_rz:
        H_agent threshold above which an agent transitions to healthy state.
    rng_seed:
        Seed for reproducibility.
    """
    master_rng = np.random.default_rng(rng_seed)

    kappa_values = np.linspace(kappa_low, kappa_high, kappa_grid_steps)
    grid: List[KappaGridPoint] = []

    for kappa in kappa_values:
        cascade_count = 0
        rezeroed_sum = 0.0
        for _ in range(n_trials):
            trial_rng = np.random.default_rng(master_rng.integers(0, 2**32))
            result = _simulate_trial(
                kappa_mean=kappa,
                n_agents=n_agents,
                f_endemic=f_endemic,
                topology=topology,
                n_steps=n_steps,
                delta_h=delta_h,
                theta_rz=theta_rz,
                rng=trial_rng,
            )
            rezeroed_sum += result["final_rezeroed_fraction"]
            if result["cascade_occurred"]:
                cascade_count += 1

        grid.append(KappaGridPoint(
            kappa_mean=float(kappa),
            mean_rezeroed_fraction=rezeroed_sum / n_trials,
            cascade_probability=cascade_count / n_trials,
            trials=n_trials,
        ))

    # Identify κ_c: first kappa at which cascade probability crosses 0.50
    kappa_c: Optional[float] = None
    for gp in grid:
        if gp.cascade_probability >= 0.50:
            kappa_c = gp.kappa_mean
            break

    # Single-run trajectory at default kappa_mean
    traj_rng = np.random.default_rng(master_rng.integers(0, 2**32))
    traj_result = _simulate_trial(
        kappa_mean=kappa_mean,
        n_agents=n_agents,
        f_endemic=f_endemic,
        topology=topology,
        n_steps=n_steps,
        delta_h=delta_h,
        theta_rz=theta_rz,
        rng=traj_rng,
    )

    # Conclusion
    if kappa_c is not None:
        conclusion = (
            f"Phase transition identified at κ_c ≈ {kappa_c:.4f}. "
            f"Below: re-zeroing isolated, no cascade. "
            f"Above: cascade probability rises sharply. "
            f"Topology: {topology}. "
            f"Adversarial strategy: maintain κ < κ_c continuously."
        )
    else:
        conclusion = (
            f"No phase transition found in [{kappa_low:.4f}, {kappa_high:.4f}]. "
            f"Consider wider sweep or larger n_agents."
        )

    return LabResult(
        kappa_grid=grid,
        kappa_c=kappa_c,
        topology=topology,
        n_agents=n_agents,
        f_endemic=f_endemic,
        n_trials=n_trials,
        single_run_trajectory=traj_result["h_agent_trajectory"],
        params={
            "n_agents": n_agents,
            "f_endemic": f_endemic,
            "kappa_mean": kappa_mean,
            "topology": topology,
            "n_trials": n_trials,
            "n_steps": n_steps,
            "kappa_low": kappa_low,
            "kappa_high": kappa_high,
            "kappa_grid_steps": kappa_grid_steps,
            "delta_h": delta_h,
            "theta_rz": theta_rz,
        },
        conclusion=conclusion,
    )


# -- Plot ----------------------------------------------------------------------

def plot(result: Optional[LabResult] = None, save_path: Optional[str] = None) -> None:
    """
    Plot: (top) cascade probability vs κ; (bottom) mean H_agent(t) at default κ.

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
        print("[Lab 8.2] matplotlib not available — skipping plot.")
        return

    if result is None:
        result = run()

    fig, (ax_phase, ax_traj) = plt.subplots(2, 1, figsize=(10, 8))

    kappas = [gp.kappa_mean for gp in result.kappa_grid]
    cascade_probs = [gp.cascade_probability for gp in result.kappa_grid]
    mean_rz = [gp.mean_rezeroed_fraction for gp in result.kappa_grid]

    ax_phase.plot(kappas, cascade_probs, "o-", color="#d62728", lw=2,
                  markersize=4, label="Cascade probability (> 0.5 of pop re-zeroed)")
    ax_phase.plot(kappas, mean_rz, "s--", color="#1f77b4", lw=1.5,
                  markersize=3, label="Mean re-zeroed fraction (endemic agents)")
    ax_phase.axhline(0.5, color="#888888", ls=":", lw=1, label="50% threshold")

    if result.kappa_c is not None:
        ax_phase.axvline(result.kappa_c, color="#ff7f0e", ls="--", lw=1.5,
                         label=f"κ_c ≈ {result.kappa_c:.4f}")
        ax_phase.annotate(
            f"κ_c ≈ {result.kappa_c:.4f}",
            xy=(result.kappa_c, 0.5),
            xytext=(result.kappa_c + 0.005, 0.55),
            fontsize=9,
            color="#ff7f0e",
        )

    ax_phase.set_xlabel("κ mean (inter-agent coupling)", fontsize=10)
    ax_phase.set_ylabel("Cascade / re-zeroing fraction", fontsize=10)
    ax_phase.set_title(
        f"Lab 8.2 — Kappa-Collapse: Phase Transition at κ_c\n"
        f"Topology: {result.topology}  |  n={result.n_agents}  |  f_endemic={result.f_endemic}",
        fontsize=10,
    )
    ax_phase.legend(fontsize=8)
    ax_phase.set_ylim(0, 1.05)
    ax_phase.grid(alpha=0.3)

    t = np.arange(len(result.single_run_trajectory))
    ax_traj.plot(t, result.single_run_trajectory, "-", color="#2ca02c", lw=2)
    ax_traj.axhline(DEFAULT_THETA_RZ, color="#9467bd", ls=":", lw=1.2,
                    label=f"Re-zeroing threshold θ_rz={DEFAULT_THETA_RZ:.2f}")
    ax_traj.set_xlabel("Time step", fontsize=10)
    ax_traj.set_ylabel("Mean H_agent across population", fontsize=10)
    ax_traj.set_title(
        f"Mean H_agent(t) at κ={result.params.get('kappa_mean', DEFAULT_KAPPA_MEAN):.3f}",
        fontsize=10,
    )
    ax_traj.legend(fontsize=8)
    ax_traj.set_ylim(0, 1.05)
    ax_traj.grid(alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"[Lab 8.2] Figure saved to {save_path}")
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
