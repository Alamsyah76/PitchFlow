# Domain Guardrail Matrix.md

# Domain Guardrail Matrix

This matrix defines:

* allowed semantic directions,
* forbidden stale-domain contamination,
* expected business framing.

The purpose is to prevent semantic drift.

---

# ERP / Business Operations Domain

## Allowed Concepts

* ERP
* fulfilment
* purchasing
* inventory
* finance
* accounting
* warehouse
* branch operations
* sales visibility
* distributor workflow
* margin protection
* operational efficiency
* business process automation
* procurement
* invoicing
* payment integration

## Allowed Framing

* operational coordination
* business visibility
* workflow optimization
* cashflow management
* branch synchronization

## Forbidden Contamination

* sensor monitoring
* traffic monitoring
* network packet
* firewall automation
* FortiManager
* NGFW
* infrastructure monitoring
* Dell hardware
* workstation deployment

---

# Hardware / Device / Workstation Domain

## Allowed Concepts

* desktop
* workstation
* processor
* memory
* storage
* endpoint deployment
* business PC lifecycle
* productivity hardware
* manageability
* device standardization
* office hardware refresh
* endpoint security
* deployment efficiency

## Allowed Framing

* employee productivity
* hardware lifecycle
* operational readiness
* deployment simplicity
* IT asset management

## Forbidden Contamination

* sensor monitoring
* traffic monitoring
* ERP workflow
* Fortinet automation
* firewall orchestration
* NGFW
* automation stitches

Forbidden weak tokens:

* mouse
* wired
* chassis
  as standalone business insights.

---

# Network / Security / Fortinet Domain

## Allowed Concepts

* FortiManager
* NGFW
* policy automation
* firewall orchestration
* hybrid mesh firewall
* centralized security
* zero-touch provisioning
* API connectors
* automation stitches
* configuration consistency
* threat response
* network visibility

## Allowed Framing

* reducing misconfiguration
* improving security consistency
* automating network operations
* reducing operational blind spots

## Forbidden Contamination

* ERP One
* Dell
* OptiPlex
* Klipboard
* fulfilment
* purchasing workflow
* accounting process

---

# Alerting / Notification Domain

## Allowed Concepts

* operational alerts
* SMS notification
* alert escalation
* security notification
* incident response
* message routing
* operational messaging
* monitoring notification
* alert delivery

## Allowed Framing

* faster incident awareness
* notification coordination
* operational responsiveness

## Forbidden Contamination

* ERP inventory
* desktop hardware
* workstation deployment
* purchasing workflow

---

# Universal Forbidden Patterns

These must never appear in final output.

## Generic Template Openers

* “Tekanan kerja tim biasanya naik...”
* “Bukti yang dipilih menunjukkan perlunya...”

## Raw Keyword Dumps

* X, Y, Z token lists without interpretation

## Weak Semantic Tokens

* built
* reduce
* they
* other
* large
* normaliz
* wired

## Generic Monitoring Bias

Do not force:

* monitoring
* sensor
* traffic
* visibility platform

unless directly grounded in evidence.

---

# Confidence Rule

If semantic confidence is low:

* reduce topic count
* avoid hallucination
* prefer narrower grounded interpretation

1 grounded topic is preferred over 2 blended topics.
