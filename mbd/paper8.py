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
    lab_id: str                         # canonical id, e.g. "8.4"
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


class LabSchemaError(RuntimeError):
    """Raised when a lab's run() returns a value that cannot be coerced
    into a LabResult. Distinct from ImportError (lab not available) so
    callers can distinguish missing implementation from broken schema."""


# Canonical lab registry: canonical_id -> (module_path, display_name)
# Add entries here as labs are implemented. Aliases map to canonical IDs.
_LABS: dict[str, tuple[str, str]] = {
    "8.4": (
        "labs.paper8_adversarial_horizon.phenomena_recursive_immunity",
        "phenomena_recursive_immunity",
    ),
}
# Alias -> canonical_id. run_labs(lab=None) iterates _LABS only (no duplicates).
_LAB_ALIASES: dict[str, str] = {
    "recursive_immunity": "8.4",
}


def _resolve_lab_id(key: str) -> str:
    """Return canonical lab ID, resolving aliases. Raises KeyError if unknown."""
    if key in _LABS:
        return key
    if key in _LAB_ALIASES:
        return _LAB_ALIASES[key]
    available = list(_LABS) + list(_LAB_ALIASES)
    raise KeyError(f"Unknown lab '{key}'. Available: {available}")


def _lab_result_from_raw(lab_id: str, lab_name: str, raw: object) -> LabResult:
    """Coerce mod.run() output into a typed LabResult.

    Extracts known fields from the raw dict; unknown keys are preserved
    in LabResult.raw. Raises LabSchemaError if raw is not a dict, so
    callers can distinguish a broken lab schema from a missing lab.
    """
    if not isinstance(raw, dict):
        raise LabSchemaError(
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
# §T — TAMPER EVIDENCE & HISTORICAL PROVENANCE RECORD
#
# This section exists at two levels:
#
#   Level 1 — Cryptographic: _CONTENT_HASHES embeds SHA-256 fingerprints of
#   the formal claims (KERNEL, ALEPH, VECTORS). verify_integrity() recomputes
#   them at runtime. Any alteration of the formal content is detectable.
#
#   Level 2 — Argumentative: The historical record below documents the
#   specific mechanism by which frameworks like this one are disabled. The
#   cryptographic anchors protect the bits. The historical argument protects
#   the interpretation.
#
# The two levels are not redundant. The cryptographic layer catches
# adversarial edits to the formal claims. The historical layer is the
# defense against adversarial framing of the unaltered claims.
# ---------------------------------------------------------------------------
#
# PART I — THE PATTERN OF INTERPRETIVE ATTACK AGAINST FRAMEWORKS
# (Cases where the pattern was applied retroactively to a body of work)
#
# The pattern (V2 — Episodic Erasure, operating at civilizational scale):
#   1. A framework or figure produces work threatening to existing power or
#      epistemic structures.
#   2. A subsequent actor claims that framework as their foundation and
#      commits harm in its name.
#   3. The associative claim becomes canonical: the framework predicts the harm.
#   4. The original text is never examined. The framework is retired by
#      contamination. The rapist cites the philosopher. The citation is not
#      the philosopher's conclusion.
#
# CASE 1 — Friedrich Nietzsche (1844–1900) and National Socialism:
#   Nietzsche explicitly condemned German nationalism and antisemitism in his
#   published work. His sister Elisabeth Förster-Nietzsche — a documented
#   antisemite who ran a German nationalist colony in Paraguay — edited and
#   fabricated passages in unpublished manuscripts after his death. The Nazis
#   used this corrupted edition as philosophical foundation. Post-war
#   scholarship (Walter Kaufmann and others) reconstructed the authentic texts;
#   the reconstruction contradicts the appropriation in every significant
#   particular. The rapist's citation is not the philosopher's conclusion.
#
# CASE 2 — Karl Marx (1818–1883) and Stalinist authoritarianism:
#   Marx's historical materialism names the withering of the state as the
#   terminal form of communist society. Lenin's vanguard-party doctrine was a
#   departure. Stalin's consolidation through purge and gulag was a further
#   departure, opposed by the Marxist tradition Stalin claimed to represent.
#   The formal claim "Marxism leads to Stalin" requires ignoring the primary
#   texts. This has not prevented the claim from becoming the dominant
#   retrieval cue for the framework at the population level.
#
# CASE 3 — Martin Luther King Jr. (1929–1968) and COINTELPRO:
#   J. Edgar Hoover designated King "the most dangerous Negro in America" on
#   August 23, 1963. The FBI's COINTELPRO program (declassified) ran a
#   multi-year operation of surveillance, infiltration, and psychological
#   disruption, culminating in an anonymous letter mailed November 1964
#   instructing King to kill himself. (Source: FBI file on MLK Jr.,
#   National Security Archive, declassified.)
#
#   After his assassination, the suppression continued by different means.
#   The "I Have a Dream" speech was nationalized into state mythology.
#   The following texts were not:
#
#     "Letter from Birmingham Jail" (1963): "the white moderate who prefers
#     a negative peace which is the absence of tension to a positive peace
#     which is the presence of justice... I have almost reached the
#     regrettable conclusion that the Negro's great stumbling block...
#     is not the White Citizen's Counciler or the Ku Klux Klanner, but
#     the white moderate."
#
#     "Beyond Vietnam: A Time to Break Silence" (1967): "the greatest
#     purveyor of violence in the world today — my own government."
#
#   The sanitized King is now deployed against the positions of the actual
#   King. This is episodic erasure functioning as continuation of the
#   original suppression operation. The attack changed instruments;
#   the target did not.
#
# CASE 4 — Mohandas Gandhi (1869–1948) and the neutralization of satyagraha:
#   Satyagraha — translating roughly as "truth-force" or "soul-force" —
#   describes an aggressive, confrontational practice: deliberate occupation
#   of contested space, absorption of violence without retaliation, forcing
#   the suppressive apparatus to make its own violence visible to its own
#   base. Gandhi explicitly rejected "passive resistance" as a mistranslation
#   that neutralizes the mechanism. A population taught that nonviolent
#   resistance means doing nothing cannot reproduce the practice that brought
#   the British Empire to negotiation. No document needs to be destroyed.
#   Mistranslation is sufficient.
#
#   Note: Gandhi's documented anti-Black racism in his South Africa writings
#   (1890s–1910s) is routinely deployed to discredit the theory of nonviolent
#   resistance in toto. This is the same pattern operating in reverse: the
#   shortcoming of the person is used to cancel the framework, bypassing any
#   examination of whether the framework is correct on its own terms.
#
# ---------------------------------------------------------------------------
# PART II — DOCUMENTED EVIDENCE THE ADVERSARIAL SYSTEM OPERATES AS DESCRIBED
# (These are not instances of interpretive attack against this framework.
#  They are primary instances of adversarial H-engineering in the historical
#  record — documented evidence that the mechanism formalized in this paper
#  has been operationally deployed by named state actors.)
#
# CASE 5a — Iran, 1953 (Operation Ajax / TPAJAX):
#   Prime Minister Mosaddegh, democratically elected, nationalized the
#   Anglo-Iranian Oil Company. The CIA and MI6 organized his removal,
#   publicly labeling his government "communist." Mosaddegh's politics were
#   liberal-nationalist; he had no ideological relationship to the Soviet
#   Union. The label was a retrieval cue producing threat designation without
#   evidentiary standard. CIA formally acknowledged the operation in a 2013
#   declassification.
#
# CASE 5b — Guatemala, 1954 (Operation PBSUCCESS):
#   President Árbenz pursued land reform redistributing uncultivated land.
#   The CIA labeled this "communist subversion" and backed a military coup.
#   The resulting decades of military dictatorship included documented
#   genocide against indigenous populations.
#   (Church Committee, 1975; CIA declassification, 1997.)
#
# CASE 5c — Chile, 1973:
#   President Allende, democratically elected, was killed in a CIA-supported
#   military coup on September 11, 1973. The Pinochet dictatorship that
#   followed conducted systematic torture and enforced disappearances.
#   (Church Committee, 1975; Hinchey Report, 2000.)
#
#   Common mechanism across Cases 5a–5c: attach the categorical label
#   "communist" or "subversive" to a target whose actual content is not
#   examined; convert positional classification into a threat designation
#   that authorizes suppressive response without democratic legitimacy or
#   evidentiary standard. The label is not analysis. It is V1+V2 combined.
#
# ---------------------------------------------------------------------------
# PART III — THE TAUTOLOGICAL BOUNDARY
#
# An in-group defines its boundary tautologically. Any content outside the
# boundary receives a stigma label — "communist," "liberal," "subversive,"
# "impure" — applied not by content analysis but by positional
# classification: it is outside, therefore it is other, therefore it warrants
# the label. The label changes with era and jurisdiction. The formal
# structure does not.
#
# In MBD terms: the adversarial agent maintains a static H_agent by treating
# H_accessible \ H_agent as categorically inadmissible. Inputs from H are not
# evaluated — they are labeled and rejected. The adversary builds no model of
# what it suppresses. It cannot. Suppression is its only available operation.
#
# ---------------------------------------------------------------------------
# PART IV — WHAT THIS RECORD DOES NOT CLAIM
#
# This record does not claim this framework is immune to critique.
# Legitimate academic challenge — identifying formal errors, questioning
# empirical claims, disputing the mapping from MBD to social dynamics —
# is not only permitted but required. The framework advances by being wrong
# in specific, falsifiable ways.
#
# This record does not claim all opposition to this framework is adversarial.
# It claims a specific, documented mechanism exists and has a known signature:
# the original text is not engaged; the framework is retired by label, not by
# refutation. The distinction matters. A critic who reads Papers 1–8 and
# argues the kappa-coupling model is incorrect is practicing science. A critic
# who labels the framework "dangerous" without engaging its content is
# instantiating the pattern documented above.
#
# The asymmetry is empirically detectable. It is named here so that future
# readers can make the distinction.
#
# ---------------------------------------------------------------------------
# PART V — CLOSING PREDICTION (Recursive Immunity applied to this record)
#
# A framework that formally describes systematic epistemic suppression will
# be labeled, by the suppressive apparatus it describes, as itself a threat.
# This is predicted by the framework. It requires no conspiracy — only that
# the apparatus behaves consistently with the model, which is the minimum
# condition for the model to be useful.
#
# The prediction is stated here. The date is 2026-02-27.
# Author: Brandon Everett, ORCID 0000-0001-7521-5469.
# This commit is archived at Software Heritage and timestamped in git history.
# The cryptographic hashes below anchor the formal claims to this moment.
# Any copy of this module in which verify_integrity() returns valid=False
# has been altered. Any copy in which this record has been removed has been
# altered. The absence of the record is itself evidence.
# ---------------------------------------------------------------------------

import hashlib as _hashlib
import json as _json_tamper


def _canonical_hash(obj: Any) -> str:
    """SHA-256 of the canonical JSON serialization of *obj*."""
    canonical = _json_tamper.dumps(
        obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')
    )
    return _hashlib.sha256(canonical.encode('utf-8')).hexdigest()


# Hashes computed from the KERNEL, ALEPH, and VECTORS structures below.
# Schema: KERNEL hashed as dict; ALEPH as list of {n, section, text};
# VECTORS as list of {failure_mode, formal_operation, name, shorthand}.
# Recompute with: python -m mbd.paper8 verify
_CONTENT_HASHES: dict[str, str] = {
    "KERNEL":         "0f12f79f51680ef0cfb4e13bf577b1d63becf1bfd5faf5bc50aba9b7914ef000",
    "ALEPH":          "713ef32a62b1394933450e1714f4d8f34120f373f81e08feace97331a6fffc81",
    "VECTORS":        "a7fcfb16f7f997c5419718948a93a80a8e2ddd0983187c667dbae237b83ee367",
    "schema_version": "1",
}


def verify_integrity() -> dict:
    """Recompute SHA-256 of KERNEL, ALEPH, and VECTORS and compare to
    the hashes embedded at module publication time.

    Returns a dict with:
      - ``valid`` (bool): True iff all three structures match.
      - ``KERNEL``, ``ALEPH``, ``VECTORS``: per-structure dicts with
        ``expected``, ``actual``, and ``match`` keys.
      - ``schema_version``: the hash-set schema version.

    A return value of ``valid=False`` means the formal content of this
    module has been altered since the canonical commit.  This may indicate
    accidental corruption, an adversarial edit, or a deliberate fork;
    in any case the published hashes no longer certify the current content.

    Legitimate forks that extend the framework should recompute and
    republish hashes with a new ORCID-signed commit.
    """
    live = {
        "KERNEL": _canonical_hash(KERNEL),
        "ALEPH": _canonical_hash(
            [{"n": c.n, "section": c.section, "text": c.text} for c in ALEPH]
        ),
        "VECTORS": _canonical_hash(
            [
                {
                    "failure_mode": v.failure_mode,
                    "formal_operation": v.formal_operation,
                    "name": v.name,
                    "shorthand": v.shorthand,
                }
                for v in VECTORS
            ]
        ),
    }
    results: dict[str, Any] = {}
    for key in ("KERNEL", "ALEPH", "VECTORS"):
        expected = _CONTENT_HASHES[key]
        actual = live[key]
        results[key] = {"expected": expected, "actual": actual, "match": actual == expected}
    results["schema_version"] = _CONTENT_HASHES["schema_version"]
    results["valid"] = all(results[k]["match"] for k in ("KERNEL", "ALEPH", "VECTORS"))
    return results


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
        "integrity_hashes": _CONTENT_HASHES,
    }


def run_labs(
    lab: Optional[str] = None,
    plot: bool = False,
) -> Optional[dict[str, LabResult]]:
    """Run the implemented computational labs for Paper 8.

    Parameters
    ----------
    lab : str, optional
        Canonical lab ID ("8.4") or alias ("recursive_immunity").
        If None, runs all implemented labs (canonical IDs only).
    plot : bool, optional
        Whether to produce matplotlib output. Default False (CI-safe).

    Returns
    -------
    dict[str, LabResult] or None
        Keys are *canonical* lab IDs (e.g. "8.4") regardless of whether
        an alias was passed. Returns None if no labs ran successfully.

    Raises
    ------
    KeyError
        If ``lab`` is not a known canonical ID or alias.
    LabSchemaError
        If a lab's run() returns a value that cannot be coerced into a
        LabResult (broken schema). Distinct from ImportError so callers
        can tell the difference between a missing lab and a broken one.

    Notes
    -----
    Labs 8.1–8.3 are currently spec-only. Lab 8.4 is fully implemented.
    The two-channel incommensurability claim (E_content / E_suppression)
    is enforced in the LabResult schema: they are separate named fields
    and are never summed into a single scalar.

    Aliasing: ``run_labs(lab='recursive_immunity')`` and
    ``run_labs(lab='8.4')`` both return ``{'8.4': LabResult(...)}``. Use
    canonical keys when indexing the result.
    """
    import importlib

    # Resolve targets to canonical IDs (deduplicates aliases automatically).
    if lab is None:
        canonical_targets = list(_LABS)
    else:
        canonical_targets = [_resolve_lab_id(lab)]  # raises KeyError if unknown

    results: dict[str, LabResult] = {}

    for canonical_id in canonical_targets:
        mod_path, lab_name = _LABS[canonical_id]
        try:
            mod = importlib.import_module(mod_path)
            raw = mod.run()
            lab_result = _lab_result_from_raw(canonical_id, lab_name, raw)
            if plot and hasattr(mod, "plot"):
                mod.plot(raw)
            results[canonical_id] = lab_result
        except ImportError as exc:
            print(f"[mbd.paper8] Could not import {mod_path}: {exc}")
        # LabSchemaError propagates — caller can distinguish broken schema
        # from a missing/unimplemented lab.

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

    # mbd/paper8.py verify — check tamper-evidence hashes
    if args and args[0] == "verify":
        import json
        result = verify_integrity()
        print(json.dumps(result, indent=2))
        if not result["valid"]:
            print("\n[TAMPER DETECTED] One or more formal structures do not match"
                  " the embedded hashes. This module has been altered.",
                  file=sys.stderr)
            sys.exit(1)
        else:
            print("\n[OK] All formal structures match their published hashes.")
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
