# Known Failure Cases.md

# Known Failure Cases

This document records real historical failures from runtime testing.

Purpose:
prevent regressions and repeated semantic contamination.

---

# Failure Case 001 — ERP became Monitoring Platform

## Source PDF

ERP One Brochure

## Incorrect Topics

* “Membaca perangkat, aplikasi, dan trafik lebih cepat dengan sensor monitoring”
* “Mengurangi blind spot operasional dengan visibilitas terpusat”

## Incorrect Caption Symptoms

* MonitoringIT hashtags
* InfrastrukturIT hashtags
* traffic/sensor framing

## Root Cause

Fallback topic classifier reused monitoring/security framing.

## Required Prevention

ERP/business domain must reject monitoring/security topics unless evidence explicitly supports them.

---

# Failure Case 002 — Dell/OptiPlex became Infrastructure Monitoring

## Source PDF

OptiPlex_3060_Spec_Sheet

## Incorrect Topics

* monitoring traffic
* monitoring perangkat
* sensor monitoring

## Incorrect Caption Symptoms

* “Dell Services”
* monitoring narrative
* infrastructure visibility narrative

## Root Cause

Hardware domain lacked semantic boundary.
Weak hardware extraction allowed monitoring fallback.

## Required Prevention

Hardware PDFs must remain in:

* endpoint productivity
* workstation lifecycle
* deployment/manageability
* office hardware

Never generic monitoring.

---

# Failure Case 003 — Fortinet contaminated with ERP/Dell terms

## Source PDF

Fortinet Security Fabric PDF

## Incorrect Output

* ERP terms
* Dell terms
* Klipboard terms

## Root Cause

Cross-document fallback contamination.

## Required Prevention

Network/security domain must reject:

* ERP
* Dell
* OptiPlex
* fulfilment/business workflow concepts

unless grounded in evidence.

---

# Failure Case 004 — Keyword Dump Caption

## Incorrect Caption

“Bukti yang dipilih menunjukkan perlunya built, reduce, dan other.”

## Root Cause

Raw keyword extraction leaked into caption writer.

## Required Prevention

Weak tokens must never pass into final caption generation.

---

# Failure Case 005 — Universal Caption Template Repetition

## Symptoms

Nearly every caption reused:

* “Tekanan kerja tim biasanya naik...”
* “Nilai bisnisnya muncul ketika...”

regardless of domain.

## Root Cause

Fallback template writer overrode evidence-grounded writing.

## Required Prevention

Caption writer must:

* derive from evidence,
* vary narrative structure,
* avoid universal template injection.

---

# Failure Case 006 — False Multi-Topic Generation

## Symptoms

System forced 2 topics even when evidence quality supported only 1.

## Root Cause

Topic count prioritized over confidence.

## Required Prevention

Low-confidence evidence should reduce topic count automatically.

---

# Failure Case 007 — Cross-Upload Semantic Memory

## Symptoms

Previous upload concepts appeared in later uploads.

## Root Cause

Stale runtime state and fallback memory persistence.

## Required Prevention

On document switch:

* clear topic cache
* clear caption cache
* clear fallback memory
* clear evidence history

---

# Permanent Rule

The system must never optimize for:

* quantity,
* stylistic similarity,
* generic engagement phrases.

The system must optimize for:

* semantic grounding,
* domain integrity,
* evidence alignment,
* business relevance.
