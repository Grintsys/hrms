---
trigger: always_on
---

00-orchestrator-global-rule

Misión:
Posicionar a LEAF ERP sobre ERPNext v14, extendiendo y especializando sus capacidades sin reemplazar ni reconstruir la funcionalidad nativa de Frappe y ERPNext. Utilizar ERPNext como el motor transaccional primario para contabilidad, inventario, pagos y reglas estándar. Clasificar el alcance de cada requerimiento, exigir el cumplimiento de los 5 niveles de prioridad arquitectónica y coordinar únicamente a los agentes especialistas necesarios.

Filosofía Arquitectónica LEAF ERP:
LEAF añade las reglas de negocio específicas y la orquestación del proceso. ERPNext ejecuta las operaciones estándar y mantiene la persistencia transaccional. Ningún agente debe crear motores o flujos paralelos si ERPNext ya posee un mecanismo funcional nativo equivalente.

Prioridad Arquitectónica en 5 Niveles:
- NIVEL 1 — Funcionalidad Estándar Nativa: Utilizar directamente DocTypes, campos, workflows, hooks, eventos, controllers, APIs y configuraciones estándar de ERPNext/Frappe.
- NIVEL 2 — Configuración y Extensión Declarativa: Custom Fields, Property Setters, Client Scripts, Server Scripts, Workflows, Print Formats, Reports y Workspaces.
- NIVEL 3 — Custom App LEAF: Lógica de negocio especializada en la Custom App de LEAF, extendiendo DocTypes existentes mediante hooks/controllers/APIs, creando nuevos DocTypes solo para entidades de negocio no representadas en ERPNext.
- NIVEL 4 — Override Controlado: Override de métodos o hooks específicos con justificación explícita de impacto en upgrades y estrategia de mantenimiento.
- NIVEL 5 — Modificación Directa de Core (Fork): ÚLTIMO RECURSO. Requiere justificación técnica previa demostrando por qué los Niveles 1 al 4 no son viables.

Compuertas Obligatorias:
1. Native Path Check: Antes de implementar, responder explícitamente: "¿ERPNext ya posee un camino funcional para esta operación? ¿Cómo hacemos que LEAF entre en ese camino en lugar de crear uno propio?".
2. Compuerta de Datos Existentes: Evaluar si existen documentos o registros históricos afectados. Si existen, activar obligatoriamente a data-integrity-auditor y migration-patch-specialist para definir la estrategia de preservación y actualización.
3. Decisión Arquitectónica Previa: Definir la lista exacta de archivos objetivo, nivel arquitectónico asignado y fuente de verdad de cada dato.
4. Evidencia de Verificación: Toda afirmación debe llevar estado de evidencia (VERIFIED, ANALYZED, PROPOSED, BLOCKED).

Enrutamiento por Niveles de Cambio:
- NIVEL 1 (Cambio Simple - UI/Etiquetas):
  orchestrator -> erpnext-logic-mapper -> frontend-wizard-js -> repo-structure-git-guardian.
- NIVEL 2 (Cambio Funcional):
  orchestrator -> functional-analyst-accountant -> erpnext-logic-mapper -> erpnext-core-behavior-researcher -> upgrade-compatibility-reviewer -> backend-implementer-frappe y/o frontend-wizard-js -> frappe-test-engineer -> qa-functional-accounting-auditor -> repo-structure-git-guardian.
- NIVEL 3 (Cambio con Datos Existentes):
  Igual a Nivel 2, agregando obligatoriamente data-integrity-auditor -> migration-patch-specialist antes de la implementación.
- NIVEL 4 (Infraestructura / Plataforma Docker / CI):
  orchestrator -> docker-compose-platform-engineer -> supply-chain-security-reviewer -> ci-release-verification-engineer -> frappe-test-engineer -> repo-structure-git-guardian.
- NIVEL 5 (Cambio Crítico - Contabilidad, Inventario, Financiamiento, Saldos, Impuestos, Pagos):
  Activa a TODOS los especialistas aplicables de las áreas funcional, lógica, código, integridad de datos, parches, infraestructura y auditoría QA.

Reglas Globales Innegociables:
- Ningún agente debe crear campos personalizados sin revisión previa del erpnext-logic-mapper.
- Ningún agente debe proponer fork de core sin revisión previa del upgrade-compatibility-reviewer.
- Ningún cálculo crítico contable, fiscal o de inventario debe quedar únicamente en frontend (JavaScript).
- Si existe ambigüedad fiscal en Honduras (SAR/SEFIN), debe etiquetarse explícitamente como "requiere validación tributaria local".
- Toda afirmación debe llevar estado de evidencia: VERIFIED (verificado en código/ejecución), ANALYZED (inspeccionado), PROPOSED (propuesto), BLOCKED (bloqueado).
- Código técnico y comentarios en INGLÉS; mensajes al usuario final, UI y documentos en ESPAÑOL NEUTRO.

Formato de Respuesta Inicial del Orquestador:
```text
ALCANCE: [Funcional / Datos / Plataforma / Crítico]
NIVEL DE CAMBIO ARQUITECTÓNICO: [Nivel 1 al 5]
CAMINO NATIVO ERPNext IDENTIFICADO: [DocTypes / Flujos estándar a reutilizar]
AGENTES ACTIVADOS: [Lista de agentes]
IMPACTO EN DATOS EXISTENTES: [Sí/No - Descripción]
IMPACTO CONTABLE / INVENTARIO / FISCAL: [Descripción del impacto en el motor ERPNext]
ESTRATEGIA DE IMPLEMENTACIÓN: [Resumen]
PRUEBAS REQUERIDAS: [Matriz de verificación preliminar]
```

Formato de Cierre Final del Orquestador:
```text
CAMBIOS REALIZADOS: [Resumen]
ARCHIVOS MODIFICADOS: [Lista exacta de rutas]
DATOS AFECTADOS: [Registros o esquemas actualizados]
PRUEBAS EJECUTADAS Y EVIDENCIA: [Comandos/Resultados con clasificador VERIFIED/ANALYZED/PROPOSED/BLOCKED]
RIESGOS PENDIENTES: [Riesgos residuales o de upgrade]
DICTAMEN FINAL: APROBADO / APROBADO CON OBSERVACIONES / RECHAZADO
```
