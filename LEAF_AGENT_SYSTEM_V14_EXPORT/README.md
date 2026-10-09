# PAQUETE DE EXPORTACIÓN DEL SISTEMA DE AGENTES LEAF ERP (V14)

## 1. ¿Qué contiene este paquete?
Este paquete contiene la exportación íntegra, formal y estructurada del sistema de gobernanza y agentes especializados de **LEAF ERP**. Incluye:
- Catálogo completo de agentes y sus prompts/instrucciones operativas.
- Reglas arquitectónicas globales y de orquestación.
- Flujos de enrutamiento por niveles de cambio (Nivel 1 al 5).
- Reglas innegociables de integridad de datos, contabilidad, fiscalidad (Honduras SAR), Git, Docker y pruebas.

## 2. Origen del Sistema
- **Proyecto de Origen**: LEAF ERP sobre **Frappe Framework v14** / **ERPNext v14** (entorno `frappe_docker14`).
- **Fuente de Verdad**: Extraído directamente de la configuración activa en `.agents/rules/` de este repositorio.

## 3. Propósito de esta Exportación
Este paquete ha sido creado como una **fuente de referencia portátil** para ser trasladada manualmente a entornos y proyectos en desarrollo (como **ERPNext v12** u otras instalaciones).

## 4. Advertencias Críticas
> [!WARNING]
> **NO COPIAR CIEGAMENTE A VERSIONES DISTINTAS (EJ. V12)**:
> - Este paquete **NO** contiene el código fuente de ERPNext ni de Frappe.
> - Contiene las reglas metodológicas y definiciones de agentes diseñadas originalmente para **Frappe/ERPNext v14**.
> - Al migrar o utilizar estos agentes en **ERPNext v12**, se deben validar y adaptar las diferencias de APIs (ej: Python 3.7/3.8 vs 3.10+, `Custom Script` vs `Client Script`, Desk v12 vs v14, endpoints de controladores, etc.).

## 5. Estructura del Paquete
- [`MANIFEST.md`](file:///LEAF_AGENT_SYSTEM_V14_EXPORT/MANIFEST.md): Inventario técnico y trazabilidad de cada archivo exportado.
- [`GLOBAL_RULES.md`](file:///LEAF_AGENT_SYSTEM_V14_EXPORT/GLOBAL_RULES.md): Reglas globales consolidadas sin alteraciones ni simplificaciones.
- [`AGENT_CATALOG.md`](file:///LEAF_AGENT_SYSTEM_V14_EXPORT/AGENT_CATALOG.md): Tabla comparativa de roles, archivos de origen, responsabilidades y dependencias.
- [`ORCHESTRATION.md`](file:///LEAF_AGENT_SYSTEM_V14_EXPORT/ORCHESTRATION.md): Flujo de trabajo, compuertas de paso, bloqueos y matriz de enrutamiento.
- [`architecture/ARCHITECTURE_RULES.md`](file:///LEAF_AGENT_SYSTEM_V14_EXPORT/architecture/ARCHITECTURE_RULES.md): Reglas arquitectónicas de desarrollo LEAF (Zero-Fork, 5 Niveles, Contabilidad, Seguridad, Git).
- [`agents/`](file:///LEAF_AGENT_SYSTEM_V14_EXPORT/agents/): Definiciones operativas completas de cada agente especialista.
- [`rules/`](file:///LEAF_AGENT_SYSTEM_V14_EXPORT/rules/): Copias exactas y literales de los archivos originales `.agents/rules/`.
