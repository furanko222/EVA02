# Contribuir a EVA02

Esta guía resume las reglas de contribution, branching y requisitos mínimos para PRs.

## Estrategia de ramas
- `main` / `master`: rama protegida, siempre deployable.
- `develop` (opcional): integración diaria.
- `feature/*`: nuevas funcionalidades.
- `hotfix/*`: correcciones urgentes en producción.

Estilo: ramas con nombres cortos y descriptivos, p. ej. `feature/add-healthcheck`.

## Pull Requests
- Todo PR debe apuntar a `main` o `develop` según la política del proyecto.
- Incluir descripción clara y link a issue si aplica.
- Incluir lista de cambios y pasos para reproducir/testear localmente.

## Requisitos del CI
- Tests pasan (pytest) y cobertura aceptable.
- SCA/SAST: pip-audit/bandit/Trivy no deben informar vulnerabilidades HIGH/CRITICAL.
- Flake8 y linters preferibles; arreglar warnings relevantes.

## Revisión de código
- Al menos 1 revisor debe aprobar el PR.
- Evitar merges sin revisión a menos que sea hotfix crítico.

## Secretos y configuración
- NO subir secretos en el repositorio.
- Usar `secrets` de GitHub Actions para tokens/credenciales.

## Despliegue
- Seguir el runbook en `RUNBOOKS/DEPLOY_RUNBOOK.md`.

Gracias por contribuir.