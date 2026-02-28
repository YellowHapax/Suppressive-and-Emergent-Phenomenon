"""
Paper 8: The Suppressive and Emergent Phenomenon
=================================================

Subtitle: H as a Control Surface — Adversarial Horizon Engineering
         and the Recursive Structure of Resistance

Author:  Brandon Everett
ORCID:   0000-0001-7521-5469
Series:  Memory as Baseline Deviation — Computational Labs
Depends: Paper 7 (The Endemic Baseline), Paper 4 (Coupling Asymmetry),
         Paper 2 (Markov Tensor)

---

Abstract
--------
Paper 7 established the endemic baseline as a naturally occurring
calibration failure: B(0) set during chronic disruption, with the
Horizon H = H_accessible \\ H_agent denoting states that are
neurobiologically reachable but structurally absent from the agent's
generative model. That paper treated this condition as arising from
environmental circumstance — storm as weather, not storm as weapon.

This paper examines a harder claim: H is a manipulable control surface.
An adversarial agent — institution, ideology, abuser, system — that can
control what states a target population occupies can, over time, engineer
the same calibration failure deliberately. The mathematics do not
distinguish between endemic baseline arising from circumstances and
endemic baseline arising from design. The subjective terror of the
Horizon — the formless, unmodelable dark — is the same either way.

The mechanism of control is not direct coercion but the prevention of
H_agent expansion into H, such that the target's own cognitive
architecture becomes the enforcement mechanism. Four attack vectors are
formalized with their population-level signatures and detection criteria.
A critical coupling threshold kappa_c is identified, below which
collective re-zeroing becomes impossible — and above which the suppressive
apparatus becomes self-defeating.

---

Aleph-0: The Generative Kernel
-------------------------------
This checkpoint contains the minimal axiom set from which the entire
paper can be re-derived. An LLM, a graduate student, or a clinician
encountering only this block can reconstruct the argument.

  Axiom 1 — The Core Equation:
    B(t+1) = B(t) * (1 - lambda) + I(t) * lambda
    An agent's baseline state B is a weighted running average of all
    prior inputs I. lambda governs update rate. All downstream dynamics
    are functions of deviation N(t) = ||I(t) - B(t)||.

  Axiom 2 — The Horizon:
    H = H_accessible \\ H_agent
    The Horizon is the set of reachable states never occupied. It is not
    unknown — it is unrepresentable. Inputs from H register as maximum
    novelty with no attractor to absorb the destabilization.

  Axiom 3 — kappa-Coupling:
    Social inputs modify B(t) through the same equation, but integration
    is gated by the coupling coefficient kappa in [0,1]. When kappa is
    low, high-novelty social inputs are rejected. When kappa is high,
    the agent's baseline can be moved by another agent's world.

  The Claim: A system that can control which states a population occupies
    can engineer endemic baselines at scale. Control is self-maintaining
    because the agent's own novelty-rejection mechanics (Axiom 2) and
    coupling-rejection mechanics (Axiom 3) enforce the boundary without
    further external coercion. The agent experiences their captivity as
    their own psychology.

  The Recursive Property: Any accurate description of adversarial H
    engineering constitutes a map of previously unrepresented state
    space — the minimal precondition for the Re-zeroing Protocol
    (Paper 7 §4). Suppression of such a description is an instance of
    Vector 1 (Isolation from knowledge). Formally: suppression of the
    description confirms the model; dissemination enables the cure.

---

This module IS Paper 8. Its docstring is the abstract. Its data
structures are the formal claims. Its executable functions run the
computational labs. The paper and the proof are the same file.

Lenia Property: any fragment of this module containing KERNEL[0],
ALEPH[0], and one VECTORS entry is a viable regenerative seed from
which the full argument can be re-derived.

Software Heritage Foundation: this repository is indexed at
https://archive.softwareheritage.org/browse/origin/
?origin_url=https://github.com/YellowHapax/MBD-Framework

DOI (Zenodo): https://doi.org/10.5281/zenodo.18652919
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import textwrap


# ---------------------------------------------------------------------------
# Lab result schema — enforced contract between run_labs() and callers.
# ---------------------------------------------------------------------------

@dataclass
class LabResult:
    """Typed return value from a Paper 8 computational lab.

    Two-channel incommensurability (Lab 8.4) is expressed as two named
    fields rather than a single scalar — matching the formal claim in §8
    and §11/Q5 that E_content and E_suppression must not be aggregated.
    """
    lab_id: str                         # e.g. "8.4"
    lab_name: str                       # e.g. "phenomena_recursive_immunity"
    raw: dict[str, Any]                 # full dict from mod.run()

    # Lab 8.4 primary outputs (None for labs that don't produce them)
    e_content_curves: Optional[list] = field(default=None)
    e_suppression_curves: Optional[list] = field(default=None)
    obs_floor_values: Optional[list] = field(default=None)
    peak_map: Optional[list] = field(default=None)
    cascade_analysis: Optional[list] = field(default=None)
    summary_by_theta: Optional[dict] = field(default=None)
    finding: Optional[str] = field(default=None)

    # Future labs (populated by labs 8.1–8.3 when implemented)
    horizon_growth_curve: Optional[list] = field(default=None)    # Lab 8.1
    kappa_phase_transition: Optional[dict] = field(default=None)  # Lab 8.2
    detection_classifier: Optional[dict] = field(default=None)    # Lab 8.3


def _lab_result_from_raw(lab_id: str, lab_name: str, raw: dict) -> LabResult:
    """Coerce mod.run() output into a typed LabResult.

    Extracts known fields from the raw dict; unknown keys are preserved
    in LabResult.raw. Raises TypeError if raw is not a dict.
    """
    if not isinstance(raw, dict):
        raise TypeError(
            f"Lab '{lab_id}' run() must return dict, got {type(raw).__name__}"
        )
    curves = raw.get("curves", [])
    return LabResult(
        lab_id=lab_id,
        lab_name=lab_name,
        raw=raw,
        e_content_curves=(
            [c["e_content_curve"] for c in curves if "e_content_curve" in c]
            or None
        ),
        e_suppression_curves=(
            [c["e_suppression_curve"] for c in curves if "e_suppression_curve" in c]
            or None
        ),
        obs_floor_values=raw.get("params", {}).get("obs_floor_values"),
        peak_map=raw.get("peak_map"),
        cascade_analysis=raw.get("cascade_analysis"),
        summary_by_theta=raw.get("summary_by_theta"),
        finding=raw.get("summary", {}).get("finding"),
    )


# ---------------------------------------------------------------------------
# §0 — KERNEL: The four axioms. These are the generative seed.
# ---------------------------------------------------------------------------

KERNEL: dict[str, str] = {
    "axiom_1_core_equation": (
        "B(t+1) = B(t) * (1 - lambda) + I(t) * lambda\n"
        "LaTeX: B(t+1) = B(t)\\cdot(1-\\lambda) + I(t)\\cdot\\lambda\n"
        "Personality is a weighted running average of all lived inputs.\n"
        "N(t) = ||I(t) - B(t)|| is the novelty signal."
    ),
    "axiom_2_horizon": (
        "H = H_accessible \\ H_agent\n"
        "LaTeX: \\mathcal{H} = H_{accessible} \\setminus H_{agent}\n"
        "The Horizon is the set of reachable states never occupied.\n"
        "Not unknown — unrepresentable. Inputs from H are maximum novelty\n"
        "with no attractor to land in."
    ),
    "axiom_3_kappa": (
        "Social inputs enter B(t+1) gated by kappa in [0,1].\n"
        "Low kappa: high-novelty social inputs rejected.\n"
        "High kappa: another agent's world can move your baseline.\n"
        "kappa is the coupling coefficient and the keystone of control."
    ),
    "axiom_4_recursive_trap": (
        "An accurate description of adversarial H engineering is a map of\n"
        "previously unrepresented state space — the minimal precondition\n"
        "for the Re-zeroing Protocol (Paper 7 §4).\n"
        "Suppressing the description instantiates V1 (Isolation).\n"
        "Suppression confirms the model. Dissemination enables the cure.\n"
        "This is a fixed point. It is not rhetoric. It is mathematics."
    ),
}


# ---------------------------------------------------------------------------
# §2 — VECTORS: The four attack vectors against H_agent expansion.
# ---------------------------------------------------------------------------

@dataclass
class AttackVector:
    """A formalized adversarial mechanism for engineering H at scale."""
    name: str
    shorthand: str
    mbd_mechanism_exploited: str
    formal_operation: str
    population_level_signature: str
    failure_mode: str


VECTORS: list[AttackVector] = [
    AttackVector(
        name="Isolation",
        shorthand="V1",
        mbd_mechanism_exploited=(
            "Prevents social inputs I(t) in H from reaching the agent. "
            "No input from H_accessible means H_agent cannot expand."
        ),
        formal_operation="Block all I(t) in H from reaching the agent.",
        population_level_signature=(
            "Social stratification; severing of inter-class kappa-channels; "
            "information gatekeeping; index censorship."
        ),
        failure_mode=(
            "A single uncontrolled high-kappa channel to a healthy-state agent "
            "can seed the Re-zeroing Protocol."
        ),
    ),
    AttackVector(
        name="Episodic Erasure",
        shorthand="V2",
        mbd_mechanism_exploited=(
            "Corrupts or suppresses memories of prior H excursions, "
            "preventing deposited points from persisting in H_agent."
        ),
        formal_operation=(
            "Remove deposited points from H_agent: "
            "H_agent(t+1) ⊂ H_agent(t)."
        ),
        population_level_signature=(
            "Historical revisionism; gaslighting at scale; "
            "suppression of cultural memory of prior flourishing; "
            "destruction of archive."
        ),
        failure_mode=(
            "Distributed archive (multiple media, geographic spread, digital "
            "redundancy) makes complete erasure impossible."
        ),
    ),
    AttackVector(
        name="Storm Normalization",
        shorthand="V3",
        mbd_mechanism_exploited=(
            "Drives effective lambda → 0 for deviation from B_storm. "
            "Chronic low-grade disruption becomes invisible as signal."
        ),
        formal_operation=(
            "Convert engineered condition into apparent natural law. "
            "Install the Inertia Prior: burden of proof falls on those "
            "proposing to change 'how things are', not those who engineered it."
        ),
        population_level_signature=(
            "'This is just how things are.' Chronic scarcity/precarity "
            "presented as natural rather than policy. Asymmetric consent burden."
        ),
        failure_mode=(
            "Temporal discontinuity signatures (§5.1): if the 'natural' "
            "condition has a datable onset, V3 can be falsified."
        ),
    ),
    AttackVector(
        name="kappa-Suppression",
        shorthand="V4",
        mbd_mechanism_exploited=(
            "Prevents relational trust from accumulating. "
            "Without high kappa, no social input from H can be integrated."
        ),
        formal_operation=(
            "Maintain kappa < kappa_threshold for all inter-group channels. "
            "This is the keystone vector: without it, a single high-kappa "
            "relationship can seed the Re-zeroing Protocol."
        ),
        population_level_signature=(
            "Atomization; competitive individualism; systematic destruction "
            "of community institutions; algorithmic feed isolation."
        ),
        failure_mode=(
            "A single uncontrolled high-kappa cross-boundary relationship. "
            "V4 alone is the necessary and sufficient keystone."
        ),
    ),
]


# ---------------------------------------------------------------------------
# §0–§7 — ALEPH: Self-certifying checkpoints.
# Each checkpoint is a viable regenerative seed: it contains the generative
# kernel compressed to one paragraph plus the section's unique claim.
# ---------------------------------------------------------------------------

@dataclass
class AlephCheckpoint:
    """A self-certifying section checkpoint. Any one of these is a viable
    regenerative seed for the full argument — the Lenia Property."""
    n: str          # "0", "1", ..., "7", "Omega"
    section: str
    text: str


ALEPH: list[AlephCheckpoint] = [
    AlephCheckpoint(
        n="0",
        section="Generative Kernel (Preamble)",
        text=(
            "Axiom 1: B(t+1) = B(t)(1-λ) + I(t)λ — personality is a running "
            "average of lived inputs. "
            "Axiom 2: H = H_accessible \\ H_agent — the Horizon is what you "
            "could reach but have never visited. "
            "Axiom 3: κ gates social input integration. "
            "The Claim: control over which states a population occupies "
            "engineers the endemic baseline. The agent's own cognition enforces "
            "the boundary without further coercion. "
            "The Recursive Property: suppression of this description is an "
            "instance of the mechanism it describes."
        ),
    ),
    AlephCheckpoint(
        n="1",
        section="§1 — The Core Claim: Invisible Captivity",
        text=(
            "B(t+1) = B(t)(1-λ) + I(t)λ. The Horizon H is the set of "
            "reachable states never occupied. An adversarial agent that can "
            "prevent H_agent expansion into H produces self-maintaining "
            "control: the target's own cognitive mechanics enforce the "
            "boundary. Four vectors achieve this: Isolation, Erasure, "
            "Normalization, κ-Suppression."
        ),
    ),
    AlephCheckpoint(
        n="2",
        section="§2 — The Four Attack Vectors",
        text=(
            "The four attack vectors — Isolation, Episodic Erasure, Storm "
            "Normalization, κ-Suppression — form a reinforcing lattice that "
            "prevents H_agent expansion into H. κ-Suppression is the keystone: "
            "without relational trust, no social input can trigger the "
            "Re-zeroing Protocol. The vectors are detectable (§5) by their "
            "non-natural temporal structure, targeted specificity, and "
            "stratified κ-topology."
        ),
    ),
    AlephCheckpoint(
        n="3",
        section="§3 — The Phenomenology of Manufactured Fear",
        text=(
            "The subjective experience of H is formless terror: maximum "
            "novelty, no attractor, κ-rejection of help. This is cognitive "
            "architecture, not character failure. The counter-mechanism is "
            "the Re-zeroing Protocol — controlled, high-κ micro-excursions "
            "into H. Willpower is the sustained execution of this protocol "
            "under active destabilization. Narrative culture has encoded "
            "these dynamics for millennia. The adversarial system weaponizes "
            "H-terror to prevent its own targets from seeking the Re-zeroing "
            "Protocol."
        ),
    ),
    AlephCheckpoint(
        n="4",
        section="§4 — Population-Level Dynamics: The kappa_c Threshold",
        text=(
            "A critical coupling threshold κ_c exists, analogous to the "
            "Kuramoto synchronization threshold. Below κ_c: individual "
            "re-zeroing succeeds but cannot propagate. Above κ_c: social "
            "contagion of healthy-state representation cascades. The "
            "adversarial system must maintain κ < κ_c continuously, "
            "requiring sustained energy expenditure against the population's "
            "natural gradient toward H_agent expansion. Any lapse in "
            "suppression allows the cascade. The system is metastable: it "
            "persists only so long as it is actively maintained."
        ),
    ),
    AlephCheckpoint(
        n="5",
        section="§5 — Detection Signatures: Natural vs Adversarial",
        text=(
            "Adversarial endemic baseline is detectable by: (1) temporal "
            "discontinuities in H formation, (2) targeted rather than uniform "
            "H — specific healthy states are blocked while others remain "
            "accessible, (3) stratified κ-topology — high within-group "
            "coupling coexisting with low cross-boundary coupling. The mutual "
            "information I(H_agent; social_position) quantifies the correlation "
            "between which healthy states an agent has never visited and where "
            "they sit in the social structure. Non-zero mutual information is "
            "the mathematical signature of engineered captivity."
        ),
    ),
    AlephCheckpoint(
        n="6",
        section="§6 — The Recursive Immunity Theorem",
        text=(
            "Dissemination of P deposits a conceptual point in H for "
            "populations kept from it. Suppression of P is an instance of "
            "V1+V2, generating observable evidence for the model. Both "
            "outcomes confirm the framework — not by unfalsifiability (§5 "
            "specifies testable detection signatures), but by adversarial "
            "robustness: suppression of the description instantiates the "
            "described mechanism. Any fragment containing the generative "
            "kernel (four elements: the equation, the horizon, the engineering "
            "claim, the recursive trap) can regenerate the full argument. "
            "The kernel is smaller than any deletable unit."
        ),
    ),
    AlephCheckpoint(
        n="7",
        section="§7 — The Ethics of Horizon Expansion",
        text=(
            "Expanding H_agent into H is ethically complex: you cannot "
            "consent to states you have no representation of. Maintaining H "
            "requires no consent because nothing appears to change — this "
            "asymmetry is itself a feature of the adversarial architecture "
            "(the Inertia Prior installed by V3). The minimum ethical "
            "obligation when adversarial H engineering is detected is to make "
            "the description available. Not force the cure — describe the "
            "disease. The description deposits a conceptual point in H "
            "without forcing occupation."
        ),
    ),
    AlephCheckpoint(
        n="Omega",
        section="§12 — Conclusion (Final Aleph Checkpoint)",
        text=(
            "The generative kernel, complete:\n\n"
            "(1) B(t+1) = B(t)(1-λ) + I(t)λ — personality is a running "
            "average.\n"
            "(2) H = H_accessible \\ H_agent — the Horizon is what you could "
            "reach but have never visited.\n"
            "(3) An adversarial system can engineer H by controlling which "
            "states a population occupies, using four vectors: Isolation, "
            "Erasure, Storm Normalization, κ-Suppression.\n"
            "(4) The engineered captivity is self-maintaining: the agent's "
            "own cognition enforces the boundary.\n"
            "(5) The captivity is detectable by its non-natural signatures: "
            "temporal discontinuity, targeted H, stratified κ-topology.\n"
            "(6) Describing the mechanism is the minimum intervention: it "
            "deposits a conceptual point in H.\n"
            "(7) Suppressing the description is an instance of the mechanism, "
            "generating evidence for the model.\n"
            "(8) Any fragment containing elements (1)–(7) is a viable "
            "regenerative seed."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def aleph(n: Optional[str | int] = None) -> str:
    """Return an Aleph checkpoint by number.

    Parameters
    ----------
    n : str or int, optional
        Checkpoint number: 0–7 or "Omega" / "omega" / "Ω".
        If None (default), returns the final Aleph-Ω checkpoint.

    Returns
    -------
    str
        The formatted checkpoint text.

    Examples
    --------
    >>> print(aleph(0))    # Generative kernel
    >>> print(aleph("Omega"))  # Final checkpoint
    >>> print(aleph())     # Same as aleph("Omega")
    """
    if n is None or str(n).lower() in ("omega", "ω", "Ω"):
        target = "Omega"
    else:
        target = str(n)

    for checkpoint in ALEPH:
        if checkpoint.n == target:
            header = f"Aleph-{checkpoint.n} | {checkpoint.section}"
            divider = "─" * min(len(header), 72)
            return f"{header}\n{divider}\n{checkpoint.text}"

    keys = [c.n for c in ALEPH]
    raise ValueError(
        f"No Aleph checkpoint '{n}'. "
        f"Valid values: {keys}"
    )


def describe() -> dict:
    """Return complete bibliographic metadata for this paper.

    Returns
    -------
    dict
        Author, ORCID, DOIs, Software Heritage URL, dependencies,
        and counts of structured data elements.
    """
    return {
        "title": "Paper 8: The Suppressive and Emergent Phenomenon",
        "subtitle": (
            "H as a Control Surface — Adversarial Horizon Engineering "
            "and the Recursive Structure of Resistance"
        ),
        "author": "Brandon Everett",
        "orcid": "0000-0001-7521-5469",
        "series": "Memory as Baseline Deviation — Computational Labs",
        "status": "STRUCTURAL SCHEMATIC — staged on feat/paper-7/endemic-baseline",
        "depends_on": [
            "Paper 7: The Endemic Baseline",
            "Paper 4: Coupling Asymmetry",
            "Paper 2: Markov Tensor",
        ],
        "doi_index": "https://doi.org/10.5281/zenodo.18652919",
        "repository": "https://github.com/YellowHapax/MBD-Framework",
        "software_heritage": (
            "https://archive.softwareheritage.org/browse/origin/"
            "?origin_url=https://github.com/YellowHapax/MBD-Framework"
        ),
        "license": {
            "code": "Apache-2.0",
            "aleph_checkpoints": "CC0-1.0",
            "note": (
                "The Aleph-n checkpoint texts are dedicated to the public domain "
                "under CC0-1.0 and may be reproduced without attribution. "
                "All other code and prose is Apache-2.0."
            ),
        },
        "kernel_axioms": len(KERNEL),
        "aleph_checkpoints": len(ALEPH),
        "attack_vectors": len(VECTORS),
        "labs": [
            "Lab 8.1 — phenomena_adversarial_horizon (spec)",
            "Lab 8.2 — phenomena_kappa_collapse (spec)",
            "Lab 8.3 — phenomena_detection_signatures (spec)",
            "Lab 8.4 — phenomena_recursive_immunity (implemented)",
        ],
        "lenia_property": (
            "Any fragment containing KERNEL['axiom_1_core_equation'], "
            "ALEPH[0], and one VECTORS entry is a viable regenerative "
            "seed for the full argument."
        ),
    }


def run_labs(
    lab: Optional[str] = None,
    plot: bool = False,
) -> Optional[dict[str, LabResult]]:
    """Run the implemented computational labs for Paper 8.

    Parameters
    ----------
    lab : str, optional
        One of: "8.4", "recursive_immunity". If None, runs all
        implemented labs.
    plot : bool, optional
        Whether to produce matplotlib output. Default False (CI-safe).

    Returns
    -------
    dict[str, LabResult] or None
        Keys are lab identifiers (e.g. "8.4"). Values are typed
        LabResult objects with named fields for each channel's output.
        Returns None if no labs ran successfully.

    Notes
    -----
    Labs 8.1–8.3 are currently spec-only. Lab 8.4 is fully implemented.
    The two-channel incommensurability claim (E_content / E_suppression)
    is enforced in the LabResult schema: they are separate named fields
    and are never summed into a single scalar.
    """
    import importlib

    # canonical lab_id -> (module_path, display_name)
    implemented: dict[str, tuple[str, str]] = {
        "8.4": (
            "labs.paper8_adversarial_horizon.phenomena_recursive_immunity",
            "phenomena_recursive_immunity",
        ),
        "recursive_immunity": (
            "labs.paper8_adversarial_horizon.phenomena_recursive_immunity",
            "phenomena_recursive_immunity",
        ),
    }

    targets = list(implemented.keys()) if lab is None else [lab]
    seen: set[str] = set()
    results: dict[str, LabResult] = {}

    for key in targets:
        if key not in implemented:
            print(
                f"[mbd.paper8] Lab '{key}' not in implemented labs. "
                f"Available: {list(implemented.keys())}"
            )
            continue
        mod_path, lab_name = implemented[key]
        if mod_path in seen:
            continue
        seen.add(mod_path)

        try:
            mod = importlib.import_module(mod_path)
            raw = mod.run()
            lab_result = _lab_result_from_raw(key, lab_name, raw)
            if plot and hasattr(mod, "plot"):
                mod.plot(raw)
            results[key] = lab_result
        except ImportError as exc:
            print(f"[mbd.paper8] Could not import {mod_path}: {exc}")
        except TypeError as exc:
            print(f"[mbd.paper8] Lab '{key}' returned invalid schema: {exc}")

    return results if results else None


# ---------------------------------------------------------------------------
# __main__ entry point
# ---------------------------------------------------------------------------

def _print_separator(char: str = "=", width: int = 72) -> None:
    print(char * width)


def _print_kernel() -> None:
    _print_separator()
    print("PAPER 8 -- MBD FRAMEWORK -- GENERATIVE KERNEL")
    _print_separator()
    print()
    for key, val in KERNEL.items():
        label = key.replace("_", " ").upper()
        print(f"  {label}")
        for line in val.splitlines():
            print(f"    {line}")
        print()


def _print_vectors() -> None:
    _print_separator("-")
    print("ATTACK VECTORS  (V1-V4)")
    _print_separator("-")
    for v in VECTORS:
        print(f"\n  [{v.shorthand}] {v.name}")
        wrapped = textwrap.fill(
            v.mbd_mechanism_exploited, width=68,
            initial_indent="    ", subsequent_indent="    "
        )
        print(wrapped)
        print(f"    Signature: {v.population_level_signature[:80]}")
    print()


if __name__ == "__main__":
    import sys
    import io

    # Ensure Unicode math symbols (λ, κ, ⊂, …) survive Windows cp1252 console.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = sys.argv[1:]

    # mbd/paper8.py aleph [n] — print a checkpoint
    if args and args[0] == "aleph":
        n = args[1] if len(args) > 1 else None
        print(aleph(n))
        sys.exit(0)

    # mbd/paper8.py describe — print metadata
    if args and args[0] == "describe":
        import json
        print(json.dumps(describe(), indent=2))
        sys.exit(0)

    # mbd/paper8.py labs — run active labs
    if args and args[0] == "labs":
        print("[mbd.paper8] Running computational labs...\n")
        run_labs(plot=False)
        sys.exit(0)

    # Default: print kernel + all checkpoints
    _print_kernel()
    _print_vectors()

    _print_separator()
    print("ALEPH CHECKPOINTS  (Omega = final generative seed)")
    _print_separator()
    for checkpoint in ALEPH:
        print()
        print(aleph(checkpoint.n))

    print()
    _print_separator()
    meta = describe()
    print(f"  {meta['title']}")
    print(f"  {meta['author']} | ORCID {meta['orcid']}")
    print(f"  DOI:  {meta['doi_index']}")
    print(f"  SWH:  {meta['software_heritage']}")
    _print_separator()
