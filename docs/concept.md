# LearnOnline.cc — Product Concept

LearnOnline.cc is a gamified, student-facing vocational training platform built on Australian Quality Training Framework (AQTF) data. It is designed to be self-hosted by individual teachers who load only the units they teach.

## The Core Loop

A student picks a unit → plays through it as a card-based game → earns XP and badges for demonstrating competency against each Element and Performance Criteria → teacher sees class progress and knowledge gaps.

## Why AQTF?

The AQTF hierarchy (Training Package → Qualification → Unit → Element → Performance Criteria → Knowledge Evidence) is a natural game structure. Each Knowledge Evidence item is a scenario the student must respond to. Each Element is a competency domain. Passing all scenarios in a unit = demonstrated competency — exactly mirroring how RTOs assess students.

## Deployment

Teachers self-host: free Supabase account + Docker. No central hosting. No subscriptions.

## Milestones

| # | Name | Description |
|---|------|-------------|
| M1 | Clean Slate | Delete dead code, fix schema, working 15-min setup |
| M2 | Quiz MVP | Units → quizzes → XP/badges |
| M3 | Game Engine Alpha | Card-based competency game |
| M4 | Adaptive Loop + SCORM | Gap analysis + SCORM 1.2 export |

Full roadmap spec: `docs/superpowers/specs/2026-05-17-learnonline-roadmap-design.md`
