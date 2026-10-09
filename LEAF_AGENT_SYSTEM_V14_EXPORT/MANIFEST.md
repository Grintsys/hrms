# MANIFEST — Inventario del Sistema de Agentes LEAF ERP (v14)

A continuación se detalla la lista exacta de todos los archivos que componen este paquete de exportación, su tipo, clasificación, origen y propósito operativo dentro de la arquitectura LEAF ERP.

| Archivo | Tipo | Clasificación | Origen | Propósito |
| :--- | :--- | :--- | :--- | :--- |
| `README.md` | Documentación | Información General | Raíz del Export | Guía del paquete, contexto v14 y advertencias de no clonar a v12 sin adaptación. |
| `MANIFEST.md` | Documentación | Inventario Técnico | Raíz del Export | Registro y trazabilidad de todos los archivos contenidos en el paquete. |
| `GLOBAL_RULES.md` | Arquitectura | Gobernanza Global | `.agents/rules/00-orchestrator-global-rule.md` | Reglas innegociables, niveles de cambio, compuertas obligatorias y clasificación de evidencia. |
| `AGENT_CATALOG.md` | Catálogo | Especificación de Agentes | `.agents/rules/*.md` | Matriz detallada de los 15 agentes, archivos fuente, responsabilidades y dependencias. |
| `ORCHESTRATION.md` | Proceso | Protocolo de Coordinación | `.agents/rules/00-orchestrator-global-rule.md` | Secuencia de análisis, desarrollo, compuertas de bloqueo, auditoría y enrutamiento. |
| `architecture/ARCHITECTURE_RULES.md` | Arquitectura | Normas de Desarrollo | Consolidación de `.agents/rules/` | Directrices de desarrollo: Zero-Fork, 5 Niveles, Contabilidad, Testing, Git, Seguridad. |
| `rules/00-orchestrator-global-rule.md` | Regla Original | Orquestador / Global | `.agents/rules/00-orchestrator-global-rule.md` | Archivo original de regla global y orquestación. |
| `rules/backend-implementer-frappe.md` | Regla Original | Implementación Backend | `.agents/rules/backend-implementer-frappe.md` | Archivo original de directrices para desarrollo Python/Frappe. |
| `rules/ci-release-verification-engineer.md` | Regla Original | CI / CD / Release | `.agents/rules/ci-release-verification-engineer.md` | Archivo original de directrices para verificación de builds y workflows. |
| `rules/data-integrity-auditor.md` | Regla Original | Auditoría de Datos | `.agents/rules/data-integrity-auditor.md` | Archivo original de directrices para preservación de registros e integridad en BD. |
| `rules/docker-compose-platform-engineer.md` | Regla Original | Infraestructura / Docker | `.agents/rules/docker-compose-platform-engineer.md` | Archivo original de directrices para plataforma `frappe_docker14`. |
| `rules/erpnext-core-behavior-researcher.md` | Regla Original | Investigación de Core | `.agents/rules/erpnext-core-behavior-researcher.md` | Archivo original de directrices para inspección del código nativo ERPNext. |
| `rules/erpnext-logic-mapper.md` | Regla Original | Mapeo Funcional Nativo | `.agents/rules/erpnext-logic-mapper.md` | Archivo original de directrices para encontrar caminos nativos ("ERPNext como Motor"). |
| `rules/frappe-test-engineer.md` | Regla Original | Pruebas y QA | `.agents/rules/frappe-test-engineer.md` | Archivo original de directrices para la matriz de pruebas en 7 dimensiones. |
| `rules/frontend-wizard-js.md` | Regla Original | Implementación Frontend | `.agents/rules/frontend-wizard-js.md` | Archivo original de directrices para Frappe Desk, Client Scripts y UI. |
| `rules/functional-analyst-accountant.md` | Regla Original | Análisis Funcional/SAR | `.agents/rules/functional-analyst-accountant.md` | Archivo original de directrices funcionales y fiscales para Honduras (SAR). |
| `rules/migration-patch-specialist.md` | Regla Original | Migraciones y Parches | `.agents/rules/migration-patch-specialist.md` | Archivo original de directrices para parches idempotentes y migraciones. |
| `rules/qa-functional-accounting-auditor.md` | Regla Original | Auditoría Final QA | `.agents/rules/qa-functional-accounting-auditor.md` | Archivo original de compuerta final y criterios de rechazo estricto. |
| `rules/repo-structure-git-guardian.md` | Regla Original | Git / Estructura | `.agents/rules/repo-structure-git-guardian.md` | Archivo original de directrices para higiene de Git y estructura de repositorios. |
| `rules/supply-chain-security-reviewer.md` | Regla Original | Seguridad de Suministro | `.agents/rules/supply-chain-security-reviewer.md` | Archivo original de directrices para dependencias, imágenes y secretos. |
| `rules/upgrade-compatibility-reviewer.md` | Regla Original | Compatibilidad Upstream | `.agents/rules/upgrade-compatibility-reviewer.md` | Archivo original de directrices para evaluación de impacto en upgrades (A -> E). |
| `agents/00-orchestrator-global-rule.md` | Agente | Orquestador | `.agents/rules/00-orchestrator-global-rule.md` | Definición completa e instrucciones del Agente Orquestador. |
| `agents/backend-implementer-frappe.md` | Agente | Backend Developer | `.agents/rules/backend-implementer-frappe.md` | Definición completa e instrucciones del Agente Backend Implementer. |
| `agents/ci-release-verification-engineer.md` | Agente | CI/CD Engineer | `.agents/rules/ci-release-verification-engineer.md` | Definición completa e instrucciones del Agente CI/Release Engineer. |
| `agents/data-integrity-auditor.md` | Agente | Auditor de Datos | `.agents/rules/data-integrity-auditor.md` | Definición completa e instrucciones del Agente Data Integrity Auditor. |
| `agents/docker-compose-platform-engineer.md` | Agente | Platform Engineer | `.agents/rules/docker-compose-platform-engineer.md` | Definición completa e instrucciones del Agente Docker Platform Engineer. |
| `agents/erpnext-core-behavior-researcher.md` | Agente | Core Researcher | `.agents/rules/erpnext-core-behavior-researcher.md` | Definición completa e instrucciones del Agente Core Researcher. |
| `agents/erpnext-logic-mapper.md` | Agente | Logic Mapper | `.agents/rules/erpnext-logic-mapper.md` | Definición completa e instrucciones del Agente ERPNext Logic Mapper. |
| `agents/frappe-test-engineer.md` | Agente | QA / Test Engineer | `.agents/rules/frappe-test-engineer.md` | Definición completa e instrucciones del Agente Test Engineer. |
| `agents/frontend-wizard-js.md` | Agente | Frontend Developer | `.agents/rules/frontend-wizard-js.md` | Definición completa e instrucciones del Agente Frontend Wizard. |
| `agents/functional-analyst-accountant.md` | Agente | Functional Analyst | `.agents/rules/functional-analyst-accountant.md` | Definición completa e instrucciones del Agente Functional Analyst & Accountant. |
| `agents/migration-patch-specialist.md` | Agente | Patch Specialist | `.agents/rules/migration-patch-specialist.md` | Definición completa e instrucciones del Agente Migration & Patch Specialist. |
| `agents/qa-functional-accounting-auditor.md` | Agente | QA Final Auditor | `.agents/rules/qa-functional-accounting-auditor.md` | Definición completa e instrucciones del Agente QA Accounting Auditor. |
| `agents/repo-structure-git-guardian.md` | Agente | Git Guardian | `.agents/rules/repo-structure-git-guardian.md` | Definición completa e instrucciones del Agente Repo Structure & Git Guardian. |
| `agents/supply-chain-security-reviewer.md` | Agente | Security Reviewer | `.agents/rules/supply-chain-security-reviewer.md` | Definición completa e instrucciones del Agente Supply Chain Security Reviewer. |
| `agents/upgrade-compatibility-reviewer.md` | Agente | Upgrade Reviewer | `.agents/rules/upgrade-compatibility-reviewer.md` | Definición completa e instrucciones del Agente Upgrade Compatibility Reviewer. |
