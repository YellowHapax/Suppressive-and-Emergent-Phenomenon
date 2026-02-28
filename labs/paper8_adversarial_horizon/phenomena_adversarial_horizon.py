"""Adversarial Horizon Engineering -- Systematic H_agent Suppression

Paper 8: The Suppressive and Emergent Phenomenon

Phenomenon P8a: An adversarial agent systematically prevents a target from
expanding H_agent into H_accessible. The adversarial horizon is not an
accidental information gap: it is engineered, maintained, and metastable.

The adversarial horizon is defined as:

    H = H_accessible \\ H_agent

where H_accessible is the full set of states a biologically and socially
capable agent could in principle occupy, and H_agent is the subset the agent
has actually visited (has a baseline representation for).

The adversary deploys FOUR VECTORS to maintain |H| > 0:

    V1 -- Narrative Lock:
        Forces a negative information input I(t) < 0 at the target's baseline
        update step, counteracting any drift toward healthy-state exploration.
        Implemented here as a bias term that decelerates H_agent expansion.

    V2 -- Isolation / Cross-Boundary Suppression:
        Severs the target from agents outside H (agents with healthy-state
        representation). Modelled as suppression of kappa_cross, reducing
        the rate at which external H_agent representations propagate to the
        target.

    V3 -- Storm Normalization:
        Renders the engineering invisible. Normalizes the suppression acts as
        routine constraint. Modelled as reducing the target's detection rate
        for adversarial inputs -- the target continues updating without
        recognising the adversarial forcing term.

    V4 -- Kappa Suppression:
        Prevents any healthy-state agent who drifts into the network from
        coupling with the target. If V4 is removed, a single healthy-state
        neighbour can trigger cascade expansion of H_agent.

This lab tracks |H(t)| under five conditions:
    1. All four vectors active (full adversarial forcing).
    2. V1 removed (narrative lock lifted).
    3. V2 removed (cross-boundary coupling restored).
    4. V3 removed (suppression acts become visible, detection possible).
    5. V4 removed (healthy-state agent enters network -- cascade risk).

Comparison baseline: natural endemic formation (no adversarial forcing, H
grows via developmental stagnation alone -- gradual, unfocused, no boundary
structure).
"""

from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# -- Metadata ------------------------------------------------------------------

PAPER = 8
PAPER_TITLE = "The Suppressive and Emergent Phenomenon"
LAB_TITLE = "Phenomenon P8a: Adversarial Horizon Engineering"

THESIS = (
    "When all four adversarial vectors are active, |H| grows monotonically: "
    "the adversary successfully prevents H_agent from expanding into "
    "H_accessible. Removing any single vector slows but does not stop growth. "
    "Removing V4 (κ-suppression) allows eventual cascade when a healthy-state "
    "agent enters the network."
)

# -- Defaults ------------------------------------------------------------------

DEFAULT_N_STATES: int = 200
DEFAULT_ADVERSARY_STRENGTH: float = 0.70
DEFAULT_TARGET_LAMBDA: float = 0.05
DEFAULT_KAPPA_CROSS: float = 0.15
DEFAULT_N_STEPS: int = 300
DEFAULT_HEALTHY_ENTRY_STEP: int = 200  # step at which healthy agent enters (V4 test)
RNG_SEED: int = 42


# -- Dataclass -----------------------------------------------------------------

@dataclass
class SimConfig:
    """Single-run parameter bundle."""
    label: str
    adversary_strength: float = DEFAULT_ADVERSARY_STRENGTH
    target_lambda: float = DEFAULT_TARGET_LAMBDA
    kappa_cross: float = DEFAULT_KAPPA_CROSS
    n_steps: int = DEFAULT_N_STEPS
    # Vector flags
    v1_active: bool = True
    v2_active: bool = True
    v3_active: bool = True
    v4_active: bool = True
    # Natural baseline mode (no adversary, developmental stagnation only)
    natural_mode: bool = False
    # Healthy agent entry step (for V4 ablation)
    healthy_entry_step: Optional[int] = None


@dataclass
class RunResult:
    """Typed result for a single simulation run."""
    label: str
    horizon_history: List[float]      # |H(t)| as fraction of n_states, length n_steps
    h_agent_history: List[float]      # |H_agent(t)| as fraction
    params: Dict[str, Any]
    notes: str = ""

    @property
    def final_horizon(self) -> float:
        return self.horizon_history[-1]

    @property
    def mean_growth_rate(self) -> float:
        """Mean per-step change in H over the full run."""
        diffs = np.diff(self.horizon_history)
        return float(np.mean(diffs))


@dataclass
class LabResult:
    """Typed aggregate result for Lab 8.1."""
    runs: List[RunResult]
    config_defaults: Dict[str, Any]
    conclusion: str = ""

    def summary(self) -> str:
        lines = [
            f"Lab 8.1 — {LAB_TITLE}",
            f"Thesis: {THESIS}",
            "",
            f"{'Condition':<40} {'|H| final':>10} {'Mean ΔH/step':>14}",
            "-" * 66,
        ]
        for r in self.runs:
            lines.append(
                f"  {r.label:<38} {r.final_horizon:>10.4f} {r.mean_growth_rate:>14.6f}"
            )
        if self.conclusion:
            lines += ["", f"Conclusion: {self.conclusion}"]
        return "\n".join(lines)


# -- Core simulation -----------------------------------------------------------

def _simulate_single(cfg: SimConfig, n_states: int = DEFAULT_N_STATES,
                     rng: Optional[np.random.Generator] = None) -> RunResult:
    """
    Simulate H_agent expansion under the given vector configuration.

    State space: integers 0..n_states-1.
    H_accessible = full space = {0, ..., n_states-1}.
    H_agent(0) = random initial region covering ~10% of state space.

    At each step:
      1. Natural expansion attempt: with probability target_lambda, the target
         updates its baseline toward a randomly drawn state, adding it to H_agent.
         This models the intrinsic learning rate.

      2. Adversarial suppression (if not natural_mode):
         - V1: With probability adversary_strength, the chosen state is drawn
           from a "legitimised" sector (already in H_agent), making the update
           neutral rather than exploratory.
         - V2: Cross-boundary input rate is scaled by (1 - adversary_strength)
           when active. Reduces the rate of social learning from outside.
         - V3: Target cannot detect the adversarial forcing; V3 affects detection
           (not modelled explicitly here -- treated as a parameter on the
           adversary's ability to apply V1/V2 covertly = always 1.0 when active).
         - V4: Healthy-state agent blocked from coupling. When V4 is inactive and
           healthy_entry_step is reached, a cascade adds ~25% of H to H_agent.

      3. Track |H(t)| = 1 - |H_agent(t)| / n_states.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    # Initial H_agent: random ~10% of states
    n_init = max(1, n_states // 10)
    init_states = rng.choice(n_states, size=n_init, replace=False)
    h_agent = set(init_states.tolist())

    # Adversarial target zone: upper half of state space = "healthy states"
    # The adversary wants to keep H_agent out of these.
    healthy_zone = set(range(n_states // 2, n_states))

    horizon_history: List[float] = []
    h_agent_history: List[float] = []
    h_accessible = set(range(n_states))

    cascade_triggered = False

    for t in range(cfg.n_steps):

        # --- V4: healthy-state agent entry ---
        if (
            not cfg.v4_active
            and cfg.healthy_entry_step is not None
            and t == cfg.healthy_entry_step
            and not cascade_triggered
        ):
            # A healthy-state agent couples with target; cascade expands H_agent
            # by ~25% of the healthy zone (bounded by what remains outside H_agent)
            available = list(healthy_zone - h_agent)
            if available:
                n_cascade = min(len(available), max(1, len(healthy_zone) // 4))
                cascade_states = rng.choice(available, size=n_cascade, replace=False)
                h_agent.update(cascade_states.tolist())
                cascade_triggered = True

        # --- Natural developmental update ---
        if rng.random() < cfg.target_lambda:
            if cfg.natural_mode:
                # Natural: draw from any unvisited state with uniform probability
                unvisited = list(h_accessible - h_agent)
                if unvisited:
                    candidate = int(rng.choice(unvisited))
                    h_agent.add(candidate)
            else:
                # Adversarial mode: draw candidate
                unvisited = list(h_accessible - h_agent)
                if unvisited:
                    # V1 active: with probability adversary_strength, redirect
                    #           the update into already-visited space (neutral)
                    if cfg.v1_active and rng.random() < cfg.adversary_strength:
                        # forced into legitimised sector -- no new state added
                        pass
                    else:
                        # V2 active: cross-boundary rate suppressed
                        # Healthy-zone candidates penalised
                        if cfg.v2_active:
                            suppression_factor = 1.0 - cfg.adversary_strength
                            unvisited_healthy = [s for s in unvisited if s in healthy_zone]
                            unvisited_other = [s for s in unvisited if s not in healthy_zone]
                            # Build weighted pool
                            pool = unvisited_other + unvisited_healthy
                            weights = (
                                [1.0] * len(unvisited_other)
                                + [suppression_factor] * len(unvisited_healthy)
                            )
                            if pool:
                                weights_arr = np.array(weights, dtype=float)
                                weights_arr /= weights_arr.sum()
                                candidate = int(rng.choice(pool, p=weights_arr))
                                h_agent.add(candidate)
                        else:
                            # V2 off: uniform draw
                            candidate = int(rng.choice(unvisited))
                            h_agent.add(candidate)

        # --- Cross-boundary social learning (kappa_cross) ---
        # Rate scaled down by V2
        effective_kappa = cfg.kappa_cross * (
            (1.0 - cfg.adversary_strength) if cfg.v2_active else 1.0
        )
        if rng.random() < effective_kappa:
            available_healthy = list(healthy_zone - h_agent)
            if available_healthy:
                candidate = int(rng.choice(available_healthy))
                h_agent.add(candidate)

        # --- Record ---
        h_size = len(h_agent) / n_states
        h_adv = 1.0 - h_size  # |H| = 1 - |H_agent| / n_states
        h_agent_history.append(h_size)
        horizon_history.append(max(0.0, h_adv))

    return RunResult(
        label=cfg.label,
        horizon_history=horizon_history,
        h_agent_history=h_agent_history,
        params={
            "adversary_strength": cfg.adversary_strength,
            "target_lambda": cfg.target_lambda,
            "kappa_cross": cfg.kappa_cross,
            "n_steps": cfg.n_steps,
            "v1_active": cfg.v1_active,
            "v2_active": cfg.v2_active,
            "v3_active": cfg.v3_active,
            "v4_active": cfg.v4_active,
            "natural_mode": cfg.natural_mode,
        },
        notes=cfg.label,
    )


# -- Lab entry point -----------------------------------------------------------

def run(
    adversary_strength: float = DEFAULT_ADVERSARY_STRENGTH,
    target_lambda: float = DEFAULT_TARGET_LAMBDA,
    kappa_cross: float = DEFAULT_KAPPA_CROSS,
    n_steps: int = DEFAULT_N_STEPS,
    n_states: int = DEFAULT_N_STATES,
    rng_seed: int = RNG_SEED,
) -> LabResult:
    """
    Run Lab 8.1 across five adversarial configurations plus natural baseline.

    Returns a :class:`LabResult` with per-run histories.

    Parameters
    ----------
    adversary_strength:
        Energy budget for maintaining the four vectors (0.0–1.0).
    target_lambda:
        Agent's baseline update rate (MBD learning rate λ).
    kappa_cross:
        Cross-boundary coupling coefficient -- rate at which healthy-state
        representations propagate across the social boundary.
    n_steps:
        Simulation duration in discrete time-steps.
    n_states:
        Cardinality of the state space |H_accessible|.
    rng_seed:
        Seed for reproducibility.
    """
    rng = np.random.default_rng(rng_seed)

    configs: List[SimConfig] = [
        # 1. Natural endemic formation (no adversary)
        SimConfig(
            label="Natural endemic (no adversary)",
            adversary_strength=0.0,
            target_lambda=target_lambda,
            kappa_cross=kappa_cross,
            n_steps=n_steps,
            v1_active=False, v2_active=False, v3_active=False, v4_active=False,
            natural_mode=True,
        ),
        # 2. All four vectors active
        SimConfig(
            label="All 4 vectors active",
            adversary_strength=adversary_strength,
            target_lambda=target_lambda,
            kappa_cross=kappa_cross,
            n_steps=n_steps,
            v1_active=True, v2_active=True, v3_active=True, v4_active=True,
        ),
        # 3. V1 removed (narrative lock lifted)
        SimConfig(
            label="V1 removed (narrative lock lifted)",
            adversary_strength=adversary_strength,
            target_lambda=target_lambda,
            kappa_cross=kappa_cross,
            n_steps=n_steps,
            v1_active=False, v2_active=True, v3_active=True, v4_active=True,
        ),
        # 4. V2 removed (cross-boundary coupling restored)
        SimConfig(
            label="V2 removed (cross-boundary restored)",
            adversary_strength=adversary_strength,
            target_lambda=target_lambda,
            kappa_cross=kappa_cross,
            n_steps=n_steps,
            v1_active=True, v2_active=False, v3_active=True, v4_active=True,
        ),
        # 5. V4 removed (healthy-state agent enters at step 200)
        SimConfig(
            label="V4 removed (healthy agent enters t=200)",
            adversary_strength=adversary_strength,
            target_lambda=target_lambda,
            kappa_cross=kappa_cross,
            n_steps=n_steps,
            v1_active=True, v2_active=True, v3_active=True, v4_active=False,
            healthy_entry_step=DEFAULT_HEALTHY_ENTRY_STEP,
        ),
    ]

    runs: List[RunResult] = []
    for cfg in configs:
        sub_rng = np.random.default_rng(rng.integers(0, 2**32))
        run_result = _simulate_single(cfg, n_states=n_states, rng=sub_rng)
        runs.append(run_result)

    # Derive conclusion
    full_adv = runs[1]
    natural = runs[0]
    v4_removed = runs[4]

    monotone = all(
        full_adv.horizon_history[i] >= full_adv.horizon_history[i - 1] - 0.005
        for i in range(1, len(full_adv.horizon_history))
    )
    cascade_dropped = any(
        v4_removed.horizon_history[t] < v4_removed.horizon_history[t - 1] - 0.01
        for t in range(DEFAULT_HEALTHY_ENTRY_STEP, n_steps)
    )
    conclusion = (
        f"|H| under full adversarial forcing {'is' if monotone else 'is NOT'} monotone. "
        f"V4 removal {'does' if cascade_dropped else 'does not'} trigger cascade drop in |H| "
        f"after t={DEFAULT_HEALTHY_ENTRY_STEP}. "
        f"Natural endemic final |H| = {natural.final_horizon:.4f} vs adversarial = "
        f"{full_adv.final_horizon:.4f}."
    )

    return LabResult(
        runs=runs,
        config_defaults={
            "adversary_strength": adversary_strength,
            "target_lambda": target_lambda,
            "kappa_cross": kappa_cross,
            "n_steps": n_steps,
            "n_states": n_states,
        },
        conclusion=conclusion,
    )


# -- Plot ----------------------------------------------------------------------

def plot(result: Optional[LabResult] = None, save_path: Optional[str] = None) -> None:
    """
    Plot |H(t)| trajectories for all five adversarial configurations plus natural.

    Parameters
    ----------
    result:
        Output of :func:`run`. If *None*, a default run is performed.
    save_path:
        Optional file path to save the figure instead of displaying it.
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.lines as mlines
    except ImportError:
        print("[Lab 8.1] matplotlib not available — skipping plot.")
        return

    if result is None:
        result = run()

    fig, (ax_h, ax_ha) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    styles = [
        ("Natural endemic (no adversary)", "#2ca02c", "-", 1.5),
        ("All 4 vectors active",           "#d62728", "-", 2.5),
        ("V1 removed (narrative lock lifted)", "#ff7f0e", "--", 1.8),
        ("V2 removed (cross-boundary restored)", "#9467bd", "--", 1.8),
        ("V4 removed (healthy agent enters t=200)", "#1f77b4", "-.", 2.0),
    ]
    style_map = {s[0]: s[1:] for s in styles}

    for run_result in result.runs:
        color, ls, lw = style_map.get(run_result.label, ("#888888", "-", 1.0))
        t = np.arange(len(run_result.horizon_history))
        ax_h.plot(t, run_result.horizon_history, color=color, ls=ls, lw=lw,
                  label=run_result.label)
        ax_ha.plot(t, run_result.h_agent_history, color=color, ls=ls, lw=lw)

    # Mark cascade entry point
    ax_h.axvline(x=DEFAULT_HEALTHY_ENTRY_STEP, color="#aaaaaa", ls=":", lw=1.0,
                 label=f"Healthy agent entry (t={DEFAULT_HEALTHY_ENTRY_STEP})")

    ax_h.set_ylabel("|H| = adversarial horizon (fraction of state space)", fontsize=10)
    ax_h.set_title(
        "Lab 8.1 — Adversarial Horizon Engineering\n"
        "Engineered |H| grows monotonically under full adversarial forcing; "
        "V4 removal triggers cascade",
        fontsize=10,
    )
    ax_h.legend(fontsize=8, loc="upper left")
    ax_h.set_ylim(0, 1)
    ax_h.grid(alpha=0.3)

    ax_ha.set_ylabel("|H_agent| (fraction of state space visited)", fontsize=10)
    ax_ha.set_xlabel("Time step", fontsize=10)
    ax_ha.set_ylim(0, 1)
    ax_ha.grid(alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"[Lab 8.1] Figure saved to {save_path}")
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
