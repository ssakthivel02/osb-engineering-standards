# Architecture - osb-engineering-standards

## Overview
Engineering standards, templates and governance baseline. This repository is part of the OmSaravanaBhava Learning Ecosystem Enterprise Architecture v1.0.

## Context diagram
```mermaid
graph TD
    User[User / Service] --> Repo[osb-engineering-standards]
    Repo --> Standards[osb-engineering-standards]
    Repo --> Platform[osb-platform-foundation]
```

## Architecture principles
- Secure by default
- Observable by default
- API-first where applicable
- Documentation-as-code
- ADR-controlled change

## Dependencies
See `ROADMAP.md` for implementation sequence and dependency notes.
