"""Recursive Immunity -- Two-Channel Suppression Dynamics

Paper 8: The Suppressive and Emergent Phenomenon

Phenomenon P8d: An adversarial system attempts to suppress information
about the mechanism it uses to maintain control. The suppression attempt
operates on two INCOMMENSURABLE channels that must be tracked separately:

    E_content(s) = (1 - s)
        The fraction of the distribution channel not blocked. This is the
        population's direct exposure to P: the map of H. E_content > 0 is
        the NECESSARY PRECONDITION for the Re-zeroing Protocol. A population
        with E_content = 0 has no map -- it cannot navigate H regardless of
        what else it observes.

    E_suppression(s) = w * s * obs_prob(s)
        Observable suppression acts: evidence that adversarial system A exists
        and is actively controlling the information environment. E_suppression > 0
        enables detection of A but does NOT deliver the map. A population that
        observes suppression but never receives P knows a controller exists but
        lacks the H representation required for Re-zeroing.

These channels are INCOMMENSURABLE: a population with E_content=0 but
E_suppression>0 cannot Re-zero. These must not be summed into a single scalar
without obscuring the adversary's actual decision problem and the Re-zeroing
Protocol's actual preconditions.

The observation probability is a decreasing function of suppression strength
(V1+V2 operate on the observation channel as well as the distribution channel):

    obs_prob(s) = obs_floor + (1 - obs_floor) * exp(-obs_decay * s)

where obs_floor is the irreducible detection floor maintained by actors outside
the adversarial system's control (international institutions, distributed
archives, independent researchers, structural leakage).

KEY STRUCTURAL PROPERTIES:

    E_content(s): monotone decreasing. Adversary's E_content objective is
        trivially satisfied by s=1. No interior optimum.

    E_suppression(s): NON-MONOTONE. It rises with s at first (more suppression
        acts visible before obs_prob degrades), then decays toward w*obs_floor
        as V1+V2 control the observation channel at high s. This peak
        represents a detection risk the adversary cannot avoid in transit.

    Cascade threshold theta_cascade: E_suppression(s) crossing theta_cascade
        (the level at which observable suppression alone triggers the Re-zeroing
        cascade without requiring the map) is the adversary's binding constraint
        (Paper 8, SS4 and SS11 Q5). If E_suppression's PEAK exceeds theta_cascade,
        the adversary faces a genuine dilemma: the path to E_content=0 passes
        through a detection risk the adversary cannot short-circuit. Intermediate
        suppression may be preferable to maximal suppression.

    Floor constraint: E_suppression(s=1) = w * obs_floor. As long as
        obs_floor > 0 the adversary cannot drive E_suppression to zero at
        maximal suppression. The adversary's second-order response: apply V3
        (Storm Normalization) to the observation channel, normalizing suppression
        acts as routine administrative restriction, driving obs_floor -> 0.

Recovers the U-shape result from SS11 Q5: intermediate suppression can be
adversarially optimal when E_suppression's peak exceeds theta_cascade, because
the adversary must choose between E_content > 0 (partial suppression, safe) and
E_content = 0 (maximal suppression, but cascade-triggering in transit).
"""

from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# -- Metadata -----------------------------------------------------------------

PAPER = 8
PAPER_TITLE = "The Suppressive and Emergent Phenomenon"
LAB_TITLE = "Phenomenon P8d: Recursive Immunity -- Two-Channel Suppression Dynamics"

THESIS = (
    "The adversary's suppression attempt operates on two incommensurable channels: "
    "E_content (direct map exposure, necessary for Re-zeroing) and E_suppression "
    "(observable suppression acts, evidence A exists but not the map). "
    "E_content is trivially minimized at s=1. E_suppression is non-monotone: "
    "it peaks at intermediate s before decaying toward the irreducible floor "
    "w*obs_floor. When the E_suppression peak exceeds the cascade threshold "
    "theta_cascade, the adversary faces a genuine dilemma -- the path to E_content=0 "
    "traverses a detection risk it cannot avoid, recovering the U-shape intuition "
    "in the correct channel. The floor remains the binding constraint: obs_floor > 0 "
    "prevents E_suppression from reaching zero at any suppression level."
)


def describe() -> Dict[str, Any]:
    return dict(
        paper=PAPER,
        paper_title=PAPER_TITLE,
        lab_title=LAB_TITLE,
        thesis=THESIS,
    )


# -- Core model ---------------------------------------------------------------

def obs_prob(s: float, obs_floor: float, obs_decay: float) -> float:
    """Observation probability as a function of suppression strength.

    V1+V2 reduce it, but cannot suppress below obs_floor.

    Args:
        s: Suppression strength in [0, 1]
        obs_floor: Irreducible detection floor (whistleblowers, structural leakage)
        obs_decay: Rate at which observation probability decreases under suppression
    """
    return obs_floor + (1.0 - obs_floor) * math.exp(-obs_decay * s)


def e_content(s: float) -> float:
    """Direct map exposure channel: fraction of P reaching the population.

    Necessary precondition for Re-zeroing Protocol. Monotone decreasing.
    Adversary trivially minimizes by s -> 1.
    """
    return 1.0 - s


def e_suppression(s: float, obs_floor: float, obs_decay: float, w: float = 1.0) -> float:
    """Observable-suppression-acts channel.

    Evidence that A exists. Does NOT deliver the map. Non-monotone:
    rises initially (more acts visible), peaks, then decays toward w*obs_floor
    as V1+V2 degrade the observation channel at high s.

    Args:
        s: Suppression strength in [0, 1]
        obs_floor: Irreducible floor
        obs_decay: Rate of obs_prob decrease
        w: Reach/credibility of suppression-evidence channel relative to
           direct distribution channel. Higher w -> higher cascade risk.
    """
    return w * s * obs_prob(s, obs_floor, obs_decay)


def find_suppression_peak(
    obs_floor: float,
    obs_decay: float,
    w: float = 1.0,
    resolution: int = 1000,
) -> Tuple[float, float]:
    """Find the s at which E_suppression is maximal (detection risk peak).

    Returns (s_peak, E_suppression_at_peak).
    The adversary must traverse past this point to reach s=1 (total suppression).
    """
    s_values = [i / resolution for i in range(resolution + 1)]
    e_values = [e_suppression(s, obs_floor, obs_decay, w) for s in s_values]
    max_idx = max(range(len(e_values)), key=lambda i: e_values[i])
    return s_values[max_idx], e_values[max_idx]


def adversary_constrained_optimal(
    obs_floor: float,
    obs_decay: float,
    w: float = 1.0,
    theta_cascade: float = 0.2,
    resolution: int = 1000,
) -> Dict[str, Any]:
    """Find adversary's optimal strategy under the cascade threshold constraint.

    The adversary wants to minimize E_content (always: push s -> 1) but faces
    the constraint that E_suppression(s) must not exceed theta_cascade (the level
    at which observable suppression alone can trigger Re-zeroing without the map).

    If E_suppression never exceeds theta_cascade: optimal is s=1, E_content=0.
    If E_suppression exceeds theta_cascade: adversary must choose between:
      (a) Stop before peak -- partial suppression, E_content > 0, safe
      (b) Maximize suppression -- E_content=0 but cascade risk in transit

    Args:
        theta_cascade: E_suppression threshold above which cascade can trigger
    """
    s_values = [i / resolution for i in range(resolution + 1)]
    e_supp_values = [e_suppression(s, obs_floor, obs_decay, w) for s in s_values]
    e_cont_values = [e_content(s) for s in s_values]

    peak_s, peak_e_supp = find_suppression_peak(obs_floor, obs_decay, w, resolution)
    floor_e_supp = e_suppression(1.0, obs_floor, obs_decay, w)

    constraint_binding = peak_e_supp > theta_cascade

    if not constraint_binding:
        # E_suppression never exceeds threshold -- adversary goes to s=1 safely
        return dict(
            s_optimal=1.0,
            e_content_at_optimal=0.0,
            e_suppression_at_optimal=floor_e_supp,
            constraint_binding=False,
            peak_s=round(peak_s, 4),
            peak_e_suppression=round(peak_e_supp, 6),
            floor_e_suppression=round(floor_e_supp, 6),
            strategy="maximal_unconstrained",
        )

    # Constraint binds: find highest s where E_suppression < theta_cascade
    # (i.e., before the peak exceeds threshold)
    safe_s = 0.0
    for i, s in enumerate(s_values):
        if e_supp_values[i] < theta_cascade:
            safe_s = s
        else:
            break  # once we exceed threshold, stop

    return dict(
        s_optimal=round(safe_s, 4),
        e_content_at_optimal=round(e_content(safe_s), 6),
        e_suppression_at_optimal=round(e_suppression(safe_s, obs_floor, obs_decay, w), 6),
        constraint_binding=True,
        peak_s=round(peak_s, 4),
        peak_e_suppression=round(peak_e_supp, 6),
        floor_e_suppression=round(floor_e_supp, 6),
        strategy="constrained_partial",  # intermediate suppression, cascade-safe
    )


# -- Simulation ---------------------------------------------------------------

def run(
    *,
    obs_floor_values: Optional[List[float]] = None,
    obs_decay_values: Optional[List[float]] = None,
    w_values: Optional[List[float]] = None,
    theta_cascade_values: Optional[List[float]] = None,
    resolution: int = 200,
) -> Dict[str, Any]:
    """Sweep parameter space. Track E_content and E_suppression separately.

    For each combination of (obs_floor, obs_decay, w):
    - E_content curve: trivially 1-s
    - E_suppression curve: non-monotone, peaks, then decays to floor
    - E_suppression peak (s_peak, peak height)
    - E_suppression floor at s=1: w * obs_floor (irreducible)
    - For each theta_cascade: adversary's constrained optimal strategy

    Returns dict with curves, peak analysis, cascade threshold analysis.
    """
    if obs_floor_values is None:
        obs_floor_values = [0.0, 0.05, 0.10, 0.20, 0.35]
    if obs_decay_values is None:
        obs_decay_values = [1.0, 3.0, 8.0]
    if w_values is None:
        w_values = [0.5, 1.0, 2.0]
    if theta_cascade_values is None:
        theta_cascade_values = [0.05, 0.10, 0.20, 0.35]

    s_grid = [i / resolution for i in range(resolution + 1)]

    curves: List[Dict] = []
    peak_map: List[Dict] = []
    cascade_analysis: List[Dict] = []

    for obs_floor in obs_floor_values:
        for obs_decay in obs_decay_values:
            for w in w_values:
                # Full separate curves
                e_cont_curve = [round(e_content(s), 6) for s in s_grid]
                e_supp_curve = [round(e_suppression(s, obs_floor, obs_decay, w), 6) for s in s_grid]
                obs_curve = [round(obs_prob(s, obs_floor, obs_decay), 6) for s in s_grid]

                curves.append(dict(
                    obs_floor=round(obs_floor, 4),
                    obs_decay=round(obs_decay, 4),
                    w=round(w, 4),
                    s_grid=s_grid,
                    e_content_curve=e_cont_curve,
                    e_suppression_curve=e_supp_curve,
                    obs_curve=obs_curve,
                ))

                # Peak and floor
                peak_s, peak_e_supp = find_suppression_peak(obs_floor, obs_decay, w, resolution)
                floor_e_supp = e_suppression(1.0, obs_floor, obs_decay, w)

                peak_map.append(dict(
                    obs_floor=round(obs_floor, 4),
                    obs_decay=round(obs_decay, 4),
                    w=round(w, 4),
                    peak_s=round(peak_s, 4),
                    peak_e_suppression=round(peak_e_supp, 6),
                    floor_e_suppression=round(floor_e_supp, 6),
                    # How much higher is the peak than the floor?
                    peak_excess=round(peak_e_supp - floor_e_supp, 6),
                ))

                # Cascade threshold analysis
                for theta in theta_cascade_values:
                    opt = adversary_constrained_optimal(
                        obs_floor, obs_decay, w,
                        theta_cascade=theta,
                        resolution=resolution,
                    )
                    cascade_analysis.append(dict(
                        obs_floor=round(obs_floor, 4),
                        obs_decay=round(obs_decay, 4),
                        w=round(w, 4),
                        theta_cascade=round(theta, 4),
                        **opt,
                    ))

    # Summary: for each theta_cascade, how many configs face a binding constraint?
    summary_by_theta: Dict[float, Dict] = {}
    for theta in theta_cascade_values:
        rows = [r for r in cascade_analysis if r["theta_cascade"] == round(theta, 4)]
        n_binding = sum(1 for r in rows if r["constraint_binding"])
        n_total = len(rows)
        summary_by_theta[theta] = dict(
            theta_cascade=theta,
            n_configurations=n_total,
            n_constraint_binding=n_binding,
            n_unconstrained=n_total - n_binding,
            pct_binding=round(n_binding / n_total, 3) if n_total else 0.0,
        )

    return dict(
        curves=curves,
        peak_map=peak_map,
        cascade_analysis=cascade_analysis,
        params=dict(
            obs_floor_values=obs_floor_values,
            obs_decay_values=obs_decay_values,
            w_values=w_values,
            theta_cascade_values=theta_cascade_values,
            resolution=resolution,
        ),
        summary_by_theta=summary_by_theta,
        summary=dict(
            n_configurations=len(peak_map),
            finding=(
                "E_content is trivially minimized at s=1 (no interior optimum). "
                "E_suppression is non-monotone: it peaks at intermediate s before "
                "decaying toward w*obs_floor. When the peak exceeds the cascade "
                "threshold theta_cascade, the adversary's path to s=1 traverses "
                "a detection risk it cannot avoid -- recovering the U-shape result "
                "in the correct channel. The floor w*obs_floor is the binding limit: "
                "obs_floor > 0 prevents E_suppression from reaching zero even at "
                "maximal suppression."
            ),
        ),
    )


# -- Plotting -----------------------------------------------------------------

def plot(results=None, **kw):
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm

    if results is None:
        results = run(**kw)

    curves = results["curves"]
    peak_map = results["peak_map"]
    cascade_analysis = results["cascade_analysis"]
    params = results["params"]
    w_values = params["w_values"]
    obs_decay_values = params["obs_decay_values"]
    obs_floor_values = params["obs_floor_values"]
    theta_cascade_values = params["theta_cascade_values"]

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle(LAB_TITLE + "\nTwo incommensurable channels: E_content (map) vs E_suppression (detection)",
                 fontsize=10, fontweight="bold")

    target_decay = obs_decay_values[len(obs_decay_values) // 2]
    target_w = w_values[len(w_values) // 2]
    target_floor = 0.10

    color_floor = cm.RdYlGn(np.linspace(0.1, 0.9, len(obs_floor_values)))
    color_w = cm.plasma(np.linspace(0.1, 0.9, len(w_values)))
    color_decay = cm.viridis(np.linspace(0.1, 0.9, len(obs_decay_values)))

    # -- (top-left) E_content vs E_suppression split, fixed params ----------
    ax1 = fig.add_subplot(2, 3, 1)
    # Show one representative config clearly
    c_rep = [cr for cr in curves
             if cr["obs_floor"] == round(target_floor, 4)
             and cr["obs_decay"] == round(target_decay, 4)
             and cr["w"] == round(target_w, 4)]
    if c_rep:
        c = c_rep[0]
        ax1.plot(c["s_grid"], c["e_content_curve"],
                 color="steelblue", linewidth=2.5, label="E_content(s) = 1-s (map)")
        ax1.plot(c["s_grid"], c["e_suppression_curve"],
                 color="crimson", linewidth=2.5, label="E_suppression(s) (detection)")
        # Mark peak of E_suppression
        pm = [p for p in peak_map
              if p["obs_floor"] == round(target_floor, 4)
              and p["obs_decay"] == round(target_decay, 4)
              and p["w"] == round(target_w, 4)]
        if pm:
            ax1.plot(pm[0]["peak_s"], pm[0]["peak_e_suppression"],
                     "^", color="crimson", markersize=10, label="E_supp peak (detection risk)")
            ax1.axhline(pm[0]["floor_e_suppression"], color="crimson",
                        linestyle=":", linewidth=1.5, alpha=0.7,
                        label=f"floor = w*obs_floor = {pm[0]['floor_e_suppression']:.3f}")
        ax1.axhline(0, color="grey", linestyle=":", linewidth=1, alpha=0.3)
    ax1.set(xlabel="Suppression strength s", ylabel="Channel value",
            title=f"Two channels (obs_floor={target_floor}, obs_decay={target_decay}, w={target_w})\n"
                  f"Channels are incommensurable: E_content=0 prevents Re-zeroing")
    ax1.legend(fontsize=7)

    # -- (top-center) E_suppression at varying obs_floor --------------------
    ax2 = fig.add_subplot(2, 3, 2)
    for i, obs_floor in enumerate(obs_floor_values):
        c = [cr for cr in curves
             if cr["obs_floor"] == round(obs_floor, 4)
             and cr["obs_decay"] == round(target_decay, 4)
             and cr["w"] == round(target_w, 4)]
        if not c:
            continue
        ax2.plot(c[0]["s_grid"], c[0]["e_suppression_curve"],
                 color=color_floor[i], linewidth=2,
                 label=f"floor={obs_floor:.2f}")
        pm = [p for p in peak_map
              if p["obs_floor"] == round(obs_floor, 4)
              and p["obs_decay"] == round(target_decay, 4)
              and p["w"] == round(target_w, 4)]
        if pm:
            ax2.plot(pm[0]["peak_s"], pm[0]["peak_e_suppression"],
                     "^", color=color_floor[i], markersize=7)
    # Show example cascade thresholds
    for theta in [0.10, 0.20]:
        ax2.axhline(theta, linestyle="--", linewidth=1, alpha=0.5,
                    label=f"theta_cascade={theta}")
    ax2.set(xlabel="Suppression strength s", ylabel="E_suppression(s)",
            title=f"E_suppression at varying obs_floor\n"
                  f"(obs_decay={target_decay}, w={target_w})\n"
                  f"^ marks peak (detection risk). Dashed = cascade thresholds")
    ax2.legend(fontsize=7)

    # -- (top-right) E_suppression peak vs obs_floor, varying w ------------
    ax3 = fig.add_subplot(2, 3, 3)
    for i, w in enumerate(w_values):
        floor_scan = sorted(set(p["obs_floor"] for p in peak_map))
        peaks = []
        floors_plot = []
        for f in floor_scan:
            pm = [p for p in peak_map
                  if p["obs_floor"] == f
                  and p["obs_decay"] == round(target_decay, 4)
                  and p["w"] == round(w, 4)]
            if pm:
                peaks.append(pm[0]["peak_e_suppression"])
                floors_plot.append(f)
        ax3.plot(floors_plot, peaks, color=color_w[i], linewidth=2,
                 marker="o", markersize=5,
                 label=f"w={w} peak height")
        # Also plot floor line
        ax3.plot(floors_plot, [w * f for f in floors_plot],
                 color=color_w[i], linewidth=1, linestyle=":",
                 label=f"w={w} floor")
    for theta in [0.10, 0.20]:
        ax3.axhline(theta, linestyle="--", linewidth=1, alpha=0.5,
                    label=f"theta_cascade={theta}")
    ax3.set(xlabel="obs_floor", ylabel="E_suppression value",
            title=f"Peak height vs. floor height\n"
                  f"(obs_decay={target_decay})\n"
                  f"Peak above theta_cascade -> constraint is binding")
    ax3.legend(fontsize=6)

    # -- (bottom-left) Cascade threshold phase: binding vs unconstrained ----
    ax4 = fig.add_subplot(2, 3, 4)
    # For target_decay and target_w, show binding/not over (obs_floor, theta_cascade)
    theta_arr = sorted(set(r["theta_cascade"] for r in cascade_analysis))
    floor_arr = sorted(set(r["obs_floor"] for r in cascade_analysis))
    Z = np.zeros((len(floor_arr), len(theta_arr)))
    for i, f in enumerate(floor_arr):
        for j, theta in enumerate(theta_arr):
            matches = [r for r in cascade_analysis
                       if r["obs_floor"] == f
                       and r["theta_cascade"] == round(theta, 4)
                       and r["obs_decay"] == round(target_decay, 4)
                       and r["w"] == round(target_w, 4)]
            if matches:
                Z[i, j] = 1.0 if matches[0]["constraint_binding"] else 0.0
    ax4.imshow(Z, origin="lower", aspect="auto", cmap="RdYlGn_r",
               vmin=0, vmax=1,
               extent=[min(theta_arr) - 0.01, max(theta_arr) + 0.01,
                       min(floor_arr) - 0.01, max(floor_arr) + 0.01])
    ax4.set(xlabel="Cascade threshold theta_cascade",
            ylabel="Detection floor obs_floor",
            title=f"Constraint binding: green=binding, red=unconstrained\n"
                  f"(obs_decay={target_decay}, w={target_w})\n"
                  f"Binding -> intermediate suppression potentially optimal")
    ax4.set_xticks([round(t, 2) for t in theta_arr])
    ax4.set_yticks([round(f, 2) for f in floor_arr])

    # -- (bottom-center) Adversary's E_content loss under constraint --------
    ax5 = fig.add_subplot(2, 3, 5)
    theta_mid = theta_cascade_values[len(theta_cascade_values) // 2]
    color_floor2 = cm.RdYlGn(np.linspace(0.1, 0.9, len(obs_floor_values)))
    for i, obs_floor in enumerate(obs_floor_values):
        rows = [r for r in cascade_analysis
                if r["obs_floor"] == round(obs_floor, 4)
                and r["theta_cascade"] == round(theta_mid, 4)
                and r["w"] == round(target_w, 4)]
        if not rows:
            continue
        # Plot E_content_at_optimal vs obs_decay
        decays_sorted = sorted(rows, key=lambda x: x["obs_decay"])
        dec_vals = [r["obs_decay"] for r in decays_sorted]
        ec_vals = [r["e_content_at_optimal"] for r in decays_sorted]
        ax5.plot(dec_vals, ec_vals, color=color_floor2[i], linewidth=2,
                 marker="o", markersize=6,
                 label=f"floor={obs_floor:.2f}")
    ax5.axhline(0, color="red", linestyle=":", linewidth=1, alpha=0.6,
                label="E_content=0 (full block)")
    ax5.set(xlabel="obs_decay", ylabel="E_content at adversary's constrained optimal",
            title=f"Adversary's map-exposure residual under cascade constraint\n"
                  f"(theta_cascade={theta_mid}, w={target_w})\n"
                  f"E_content>0 = adversary CANNOT fully block map")
    ax5.legend(fontsize=7)

    # -- (bottom-right) Summary table (theta_cascade = mid) ------------------
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis("off")
    summary_by_theta = results["summary_by_theta"]
    table_data = [["theta_c", "N binding", "N free", "pct binding"]]
    for theta in theta_cascade_values:
        row = summary_by_theta.get(theta, {})
        table_data.append([
            f"{theta:.2f}",
            str(row.get("n_constraint_binding", "?")),
            str(row.get("n_unconstrained", "?")),
            f"{row.get('pct_binding', 0)*100:.0f}%",
        ])
    tbl = ax6.table(cellText=table_data[1:], colLabels=table_data[0],
                    loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.2, 1.6)
    ax6.set_title(
        "Binding constraint by cascade threshold\n"
        "(binding = peak E_suppression > theta_cascade;\n"
        " adversary faces intermediate-suppression dilemma)",
        fontsize=8, pad=10,
    )

    fig.tight_layout()
    return fig


# -- Entry point --------------------------------------------------------------

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import json

    results = run()
    summary = results["summary"]
    summary_by_theta = results["summary_by_theta"]

    print(f"\n{'='*60}")
    print(f"  {LAB_TITLE}")
    print(f"{'='*60}\n")
    print(f"Configurations tested:  {summary['n_configurations']}")
    print()
    print("E_content channel: trivially maximized at s=0, minimized at s=1.")
    print("No interior optimum. Adversary's primary objective always s=1.\n")

    print("E_suppression peak analysis (obs_decay=3.0, w=1.0):")
    print(f"  {'obs_floor':>10}  {'peak_s':>8}  {'peak_E_supp':>12}  {'floor_E_supp':>13}")
    for p in results["peak_map"]:
        if abs(p["obs_decay"] - 3.0) < 0.01 and abs(p["w"] - 1.0) < 0.01:
            print(f"  {p['obs_floor']:>10.2f}  {p['peak_s']:>8.3f}  "
                  f"{p['peak_e_suppression']:>12.4f}  {p['floor_e_suppression']:>13.4f}")

    print()
    print("Cascade threshold analysis (configs where constraint is BINDING):")
    for theta, row in sorted(summary_by_theta.items()):
        print(f"  theta_cascade={theta:.2f}: "
              f"{row['n_constraint_binding']}/{row['n_configurations']} binding "
              f"({row['pct_binding']*100:.0f}%)")

    print()
    print("Finding:")
    print(f"  {summary['finding']}")

    outfile = "_p8d_test.png"
    plot(results)
    plt.savefig(outfile, dpi=80, bbox_inches="tight")
    print(f"\nPASS - plot saved to {outfile}")
