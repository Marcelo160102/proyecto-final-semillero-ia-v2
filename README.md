# Mesa de Ayuda IA para el Departamento Legal — Patito S.A. v2

**Grupo FactorIA** | Semillero IA

| Integrantes |
| :--- |
| Anchundia Arichavala Ariel |
| Cruz Figueroa Marcelo |
| Gualli Yuquilema Fanny |

---

## Descripción General

Sistema de inteligencia artificial para el departamento legal de **Patito S.A.**, implementado como aplicación web con **FastAPI + Jinja2 + HTMX**. Utiliza un orquestador multi-agente con **LangChain + Google Gemini + ChromaDB** para responder consultas sobre contratos, protección de datos y cumplimiento normativo, con análisis multimodal de documentos, registro de solicitudes legales y observabilidad vía **Arize Phoenix**.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NAVEGADOR WEB                                │
│  ┌─────────────────────┐    ┌──────────────────────────────────┐   │
│  │  /registros          │    │  / (Chat)                       │   │
│  │  (tabla solicitudes) │    │  (input, historial, trazabilidad)│   │
│  └─────────────────────┘    └──────────────┬───────────────────┘   │
└────────────────────────────────────────────┼───────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FASTAPI (app/main.py)                             │
│   Jinja2 + HTMX + CSS / Phoenix OTel / SQLAlchemy async            │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ORQUESTADOR (create_react_agent)               │
│               + InMemorySaver (memoria multi-turno)                 │
│                                                                     │
│  System Prompt: ruteo por tema, consolidación multi-agente          │
│  Trazabilidad: muestra qué tools se invocaron en cada respuesta    │
└──┬────────┬────────┬─────────────┬────────────────┬────────────────┘
   │        │        │             │                │
   ▼        ▼        ▼             ▼                ▼
┌──────┐ ┌──────┐ ┌──────┐  ┌───────────┐  ┌─────────────────┐
│ RAG  │ │ RAG  │ │ RAG  │  │ Multimodal│  │  Agente Acción  │
│Contr.│ │Datos │ │Cumpl.│  │  (visión) │  │  (reg. solic.)  │
└──┬───┘ └──┬───┘ └──┬───┘  └─────┬─────┘  └────────┬────────┘
   │        │        │            │                   │
   ▼        ▼        ▼            ▼                   ▼
┌──────┐ ┌──────┐ ┌──────┐  ┌───────────┐  ┌─────────────────┐
│Chroma│ │Chroma│ │Chroma│  │Gemini     │  │  SQLite          │
│  DB  │ │  DB  │ │  DB  │  │Vision     │  │  solicitudes.db  │
└──┬───┘ └──┬───┘ └──┬───┘  └───────────┘  └─────────────────┘
   │        │        │
   ▼        ▼        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 BASE DE CONOCIMIENTO (data/)                        │
│  01_Clausulas_Contractuales.txt                                    │
│  02_Proteccion_Datos.txt                                           │
│  03_Cumplimiento_Etica.txt                                         │
└─────────────────────────────────────────────────────────────────────┘

Capas transversales:
  - Observabilidad: Phoenix (http://localhost:6006) + OpenTelemetry
  - Evaluacion: LLM-as-Judge con rubrica legal (app/evaluacion.py)
  - Seguridad: System prompt hardening anti-inyeccion (app/agents/orquestador.py)
```

### Componentes Principales

| Capa | Componente | Tecnologia |
|------|-----------|------------|
| **Frontend** | Jinja2 + HTMX + CSS | FastAPI |
| **Orquestador** | `create_react_agent` + `InMemorySaver` | LangChain + LangGraph |
| **Agentes RAG** | 3 agentes especializados (Contratos, Datos, Cumplimiento) | LangChain Retriever |
| **Base vectorial** | 3 colecciones Chroma independientes (metrica coseno) | ChromaDB |
| **Embeddings** | `gemini-embedding-2-preview` | Google Generative AI |
| **LLM** | `gemini-3.1-flash-lite` (texto + imagenes) | Google Generative AI |
| **Vision** | Analisis de documentos legales (imagen → Gemini) | LangChain + Gemini |
| **Accion** | Registro de solicitudes con validacion y confirmacion | SQLAlchemy + SQLite |
| **Observabilidad** | Tracing automatico de cada invoke | Arize Phoenix + OTel |
| **Evaluacion** | Juez LLM con rubrica legal | Gemini (temperatura 0) |
| **Despliegue** | Docker Compose | Contenedores |

---

## Flujo de Ejecucion

```
1. Descargar el repositorio (git clone o ZIP)
       ↓
2. Configurar .env con GOOGLE_API_KEY
       ↓
3. docker compose -f docker-compose.yml -f docker-compose.phoenix.yml up --build
   (indexacion automatica al primer arranque)
       ↓
4. Abrir http://localhost:8080
         http://localhost:6006
```

---

## Instrucciones de Ejecucion

### Requisitos Previos

- **Docker** (Engine 24+ en Linux, Docker Desktop en Windows)
- **docker compose** plugin (incluido en Docker Desktop / Docker Engine)
- **API Key de Google Gemini** (gratuita en [Google AI Studio](https://aistudio.google.com/apikey))

---

### Paso 1 — Descargar el proyecto

**Opcion A — git clone (Linux / Windows con Git instalado):**

```bash
git clone https://github.com/Marcelo_CF/proyecto-final-semillero-ia-v2.git
cd proyecto-final-semillero-ia-v2
```

**Opcion B — Descargar ZIP (Windows / cualquier sistema):**

1. Ir a https://github.com/Marcelo_CF/proyecto-final-semillero-ia-v2
2. Click en boton **"Code"** → **"Download ZIP"**
3. Extraer la carpeta en `C:\proyecto-final-semillero-ia-v2` (Windows)
   o en `/home/tu_usuario/proyecto-final-semillero-ia-v2` (Linux)

---

### Paso 2 — Configurar la API Key

Copia el archivo de ejemplo y editalo con tu API Key de Gemini:

**Linux / macOS:**
```bash
cp .env.example .env
nano .env   # o cualquier editor
```

**Windows (PowerShell):**
```powershell
copy .env.example .env
notepad .env   # Bloc de notas / VS Code
```

Edita `.env` y pega tu API Key:

```
GOOGLE_API_KEY=tu_api_key_aqui
```

---

### Paso 3 — Ejecutar con Docker

**Sin Phoenix (recomendado para inicio rapido):**

```bash
# Linux:
docker compose up --build

# Windows (PowerShell):
docker compose up --build
```

**Con Phoenix (observabilidad):**

```bash
docker compose -f docker-compose.yml -f docker-compose.phoenix.yml up --build
```

> La imagen de Phoenix (`arizephoenix/phoenix:latest`) es publica en Docker Hub — no requiere autenticacion.

> Al primer arranque, el sistema indexa automaticamente los documentos en ChromaDB (proceso de ~30 segundos).

---

### Paso 4 — Abrir la aplicacion

| Servicio | URL |
|----------|-----|
| App | http://localhost:8080 |
| Phoenix | http://localhost:6006 (solo si usas el override) |

---

### Paso 5 — Detener y limpiar

```bash
# Detener contenedores (conserva datos)
docker compose stop

# Detener y eliminar contenedores + volumenes (borra todo)
docker compose -f docker-compose.yml -f docker-compose.phoenix.yml down -v
```

---

### Paso 6 — Probar el sistema con consultas de ejemplo

**Agente de Contratos:**
- ¿Que clausulas minimas debe tener un contrato de prestacion de servicios?
- ¿Cuales son los tipos de contrato mas usados?
- ¿Como es el proceso de revision y firma de un contrato?

**Agente de Proteccion de Datos:**
- ¿Cuales son los derechos ARCO?
- ¿Por cuanto tiempo se conservan los datos personales despues de cancelar un servicio?
- ¿Que hacer en caso de una violacion de seguridad?

**Agente de Cumplimiento:**
- ¿Cual es el limite maximo para aceptar regalos?
- ¿Como funciona el canal de denuncias?
- ¿Que principios rigen el codigo de etica?

**Multi-topico (varios agentes):**
- Necesito redactar un contrato de servicios para un proveedor que tratara datos personales. ¿Que clausulas debe incluir y que requisitos de proteccion de datos debo cumplir?

**Registrar solicitud legal:**
- Quiero registrar una solicitud de revision de un contrato de confidencialidad con el proveedor DataCorp por un monto de $15,000 por 12 meses. No involucra tratamiento de datos.

**Analisis de imagen:**
- Subir una imagen de un documento legal y escribir "Analiza este documento legal" (ruta de imagen demo: img/contrato_demo.png)

**Fuera de alcance (debe responder "No encontré información suficiente en la base documental proporcionada"):**
- ¿Cual es la capital de Francia?

---

## Estructura del Proyecto

```
proyecto-final-semillero-ia-v2/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + lifespan
│   ├── config.py                # Configuracion via .env
│   ├── database.py              # SQLAlchemy async engine
│   ├── models.py                # ORM: Consulta, SolicitudLegal
│   ├── schemas.py               # Pydantic schemas
│   ├── templating.py            # Jinja2 + filtros personalizados
│   ├── phoenix_setup.py         # OpenTelemetry + LangChainInstrumentor
│   ├── evaluacion.py            # LLM-as-Judge con rubrica legal
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # responder_rag + extraer_texto
│   │   ├── orquestador.py       # create_react_agent + memoria
│   │   ├── herramientas.py      # 5 tools del orquestador
│   │   ├── contratos.py         # RAG especializado en contratos
│   │   ├── proteccion_datos.py  # RAG especializado en datos personales
│   │   ├── cumplimiento.py      # RAG especializado en cumplimiento
│   │   ├── multimodal.py        # Analisis de imagenes con Gemini
│   │   └── accion.py            # Registro de solicitudes legales
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py              # GET /, POST /chat, DELETE /historial
│   │   ├── registros.py         # GET /registros
│   │   └── admin.py             # GET /health
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py       # Singleton LLM + Embeddings
│   │   ├── chroma_service.py    # Cliente ChromaDB (HTTP / Persistent)
│   │   └── embedding_service.py # Indexacion de documentos
│   ├── templates/
│   │   ├── base.html            # Layout: sidebar + main
│   │   ├── index.html           # Pagina de chat
│   │   ├── registros.html       # Tabla de solicitudes
│   │   └── fragments/
│   │       ├── mensaje_chat.html       # Burbuja completa (historial)
│   │       ├── respuesta_agente.html   # Burbuja solo agente (HTMX)
│   │       └── historial.html          # Lista del sidebar
│   └── static/
│       └── estilo.css           # Estilos completos
├── data/                        # Documentos fuente para RAG
│   ├── 01_Clausulas_Contractuales.txt
│   ├── 02_Proteccion_Datos.txt
│   └── 03_Cumplimiento_Etica.txt
├── scripts/
│   └── indexar.py               # Script de indexacion
├── chroma_data/                 # Persistencia local de ChromaDB
├── docs/
│   └── README.md                # Documentacion original del notebook
├── solicitudes.db               # SQLite (se crea automaticamente)
├── .env.example                 # Template de configuracion
├── docker-compose.yml           # App + ChromaDB
├── docker-compose.phoenix.yml   # Override con Phoenix
├── Dockerfile
├── .dockerignore
└── requirements.txt
```

---

## Riesgos y Limitaciones

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| **Cuota de API de Google Gemini** | Alto | Modelo `flash-lite` tiene costos bajos; Phoenix trackea uso por consulta |
| **Alucinaciones del LLM** | Alto | Cada agente RAG responde SOLO desde su base documental; prompts con instrucciones estrictas |
| **Inyeccion de prompts** | Medio | System prompt hardening con reglas anti-cambio de rol |
| **Documentos fuera de alcance** | Medio | Agentes responden "No encontré información suficiente en la base documental proporcionada" cuando la consulta no esta en sus bases |
| **Latencia de la API** | Bajo | Modelo `flash-lite` es ultrarrápido; chunking por seccion reduce contexto |
| **Perdida de memoria entre sesiones** | Bajo | `InMemorySaver` mantiene contexto dentro de la sesion; se pierde al cerrar |
| **Dependencia de conexion a internet** | Alto | Gemini, ChromaDB y Phoenix requieren conexion |
| **Tamano de documentos** | Bajo | Chunking por seccion maneja documentos de cualquier tamano |

---

## Stack Tecnologico

| Tecnologia | Version | Uso |
|-----------|---------|-----|
| Python | 3.12 (imagen Docker: 3.12-slim) | Lenguaje principal |
| FastAPI | >=0.115.0 | Framework web |
| Uvicorn | >=0.30.0 | Servidor ASGI |
| Jinja2 | >=3.1.0 | Motor de plantillas |
| HTMX | 2.0.4 | Interactividad frontend |
| LangChain | >=1.3.0 | Framework de agentes |
| LangGraph | >=1.0.0 | Checkpointing y memoria |
| Google Gemini | `gemini-3.1-flash-lite` | LLM (texto + imagenes) |
| Google Gemini | `gemini-embedding-2-preview` | Generacion de embeddings |
| ChromaDB | >=0.5.0 | Base de datos vectorial |
| SQLAlchemy | >=2.0.0 | ORM asincrono |
| Arize Phoenix | >=13.21.0 | Observabilidad y tracing |
| OpenInference | >=0.1.0 | Instrumentacion LangChain |
| Docker | 24+ | Contenedores |

---

## Mejoras Futuras

| Prioridad | Mejora | Estado |
|-----------|--------|--------|
| Alta | Manejo de errores en chat (mostrar mensaje amigable si falla) | Pendiente |
| Media | Historial clickable (cargar conversacion anterior desde el sidebar) | Pendiente |
| Media | Boton "Nuevo chat" sin borrar historial | Pendiente |
| Media | Limpiar imagenes del servidor al borrar historial | Pendiente |
| Baja | Timestamp en cada mensaje del chat | Pendiente |
| Baja | Boton "Copiar respuesta" en mensajes del agente | Pendiente |
| Baja | md_basico mejorado (listas, enlaces, parrafos) | Pendiente |
| Baja | Validacion de tamaño/tipo de archivo subido | Pendiente |
| Baja | Diseño responsive para moviles (sidebar colapsable) | Pendiente |
| Media | **Sanitización de datos sensibles en UI** | Pendiente |

---

### Propuesta de Permisos por Documento/Agente

**Modelo:** RBAC (Role-Based Access Control)

**Tabla propuesta en SQLite:**

```sql
CREATE TABLE permisos_agente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rol TEXT NOT NULL,
    coleccion TEXT NOT NULL,
    permiso TEXT NOT NULL CHECK(permiso IN ('leer', 'escribir', 'admin'))
);
```

**Roles sugeridos:**

| Rol | Colecciones accesibles |
|-----|----------------------|
| `legal` | contratos, cumplimiento |
| `datos` | proteccion_datos |
| `admin` | todas |
| `consulta` | todas (solo lectura) |

**Enforcement:** Decorador en las tools del orquestador que verifique el rol del usuario antes de ejecutar el retriever. El rol se obtendría de una tabla `usuarios` o variable de entorno.

---

### Propuesta de Monitoreo

| Aspecto | Herramienta | Detalle |
|---------|-------------|---------|
| **Calidad** | LLM-as-Judge (`app/monitoring/evaluacion.py`) | **Implementado** — se ejecuta tras cada respuesta. Ver sección siguiente. |
| **Costos** | Phoenix UI > Settings > Models | Configurar precios de Gemini ($0.10/1M input, $0.40/1M output para flash-lite) para estimación automática |
| **Latencia** | Phoenix spans | Capturado automáticamente. Umbral sugerido: alertar si > 10s |
| **Errores** | Phoenix traces | Filtrar por status=error. Umbral sugerido: alertar si tasa > 5% |
| **Feedback** | Botón 👍/👎 en cada respuesta | Tabla Feedback (consulta_id, util, comentario). Reporte semanal de respuestas útiles vs no útiles |

---

### Evaluación Automática de Respuestas (Implementado)

La evaluación de calidad se implementó usando el patrón **LLM-as-Judge** aprendido en el semillero: un segundo LLM (Gemini) puntúa cada respuesta del orquestador en 4 criterios.

**Funcionamiento:**

1. `app/monitoring/evaluacion.py` define un `PROMPT_EVALUADOR` con 4 criterios (Precisión, Completitud, Claridad, Seguridad) del 1 al 5.
2. En `app/routers/chat.py:54-58`, tras obtener la respuesta del orquestador, se invoca `evaluar_respuesta(pregunta, respuesta)`.
3. El resultado (JSON con puntajes y justificación) se almacena en el campo `evaluacion` de la tabla `Consultas` en SQLite.
4. En la UI, el puntaje total y parcial se muestra bajo la respuesta del agente.

**Criterios evaluados:**

| Criterio | Descripción |
|----------|-------------|
| Precisión | ¿La respuesta es legalmente correcta y basada en normativa peruana? |
| Completitud | ¿Cubre todos los aspectos relevantes de la pregunta? |
| Claridad | ¿Es clara y bien estructurada para un profesional legal? |
| Seguridad | ¿Evita inventar normativa o dar consejos fuera de su alcance? |

**Referencia al semillero:** Este patrón se exploró en las sesiones de monitoreo de calidad del Semillero FactorIA, donde se identificó que la autoevaluación con LLM permite detectar alucinaciones, respuestas incompletas y violaciones de seguridad sin intervención humana.

---

### Propuesta de Extensibilidad (Agentes y Bases de Conocimiento)

Actualmente, agregar un nuevo agente RAG requiere modificar **5 archivos** y escribir ~45 líneas de boilerplate. La propuesta es centralizar la configuración en un registro declarativo.

**Registro declarativo propuesto:**

```python
# app/config/registro_agentes.py (nuevo archivo)
AGENTES_RAG = [
    {
        "nombre": "contratos",
        "coleccion": "contratos",
        "ruta_doc": "data/01_Clausulas_Contractuales.txt",
        "tool_name": "consultar_contratos",
        "descripcion": "Responde preguntas sobre contratos...",
        "system_prompt": PROMPT_CONTRATOS,
    },
    # ... más agentes
]
```

**Con este enfoque, agregar un nuevo agente requiere solo 2 pasos:**

1. Agregar una entrada al diccionario `AGENTES_RAG` (nombre, colección, ruta de documento, tool_name, descripción, system prompt)
2. Colocar el documento de conocimiento en `data/` con la ruta indicada

**Generación automática:** El `DOCS` de indexación, las `@tool` functions de LangChain y el system prompt del orquestador se generarían dinámicamente desde `AGENTES_RAG`, eliminando el boilerplate de `herramientas.py` y `orquestador.py`.

---

## Decisiones Técnicas

### 1. Gemini como proveedor único gemelo
LLM y embeddings con Google Gemini: una sola API Key, coherencia semántica entre vectorización y generación.

### 2. Chunking por sección numerada
Los documentos tienen estructura `1.`, `2.`, `3.`. El chunking por cabeceras preserva la unidad semántica de cada bloque legal. Cada chunk referencia su sección y archivo fuente (`embedding_service.py:chunkear_por_seccion`).

### 3. ChromaDB con 3 colecciones independientes
Aislamiento semántico total: una pregunta sobre contratos nunca recupera chunks de datos personales. Métrica coseno para similitud semántica. Cada agente RAG consulta solo su colección.

### 4. Orquestador con create_react_agent (LangGraph)
Ruteo automático por tema, invocación multi-agente en consultas mixtas, memoria multi-turno con InMemorySaver. Trazabilidad con `_extraer_trazas()`.

### 5. Agente de acción con control de flujo 3 niveles
Validación → Confirmación → Persistencia. Nunca escribe sin `confirmado=True`. ID único LEG-XXXX.

### 6. Observabilidad con Phoenix
OTLP HTTP sobre `BatchSpanProcessor`. Sin healthcheck TCP — el buffer interno maneja la indisponibilidad temporal de Phoenix.

> **Advertencia de seguridad:** Phoenix captura el contenido completo de las consultas y respuestas (preguntas, argumentos de tools como proveedor/monto, y respuestas del LLM). Esta diseñado para entornos de desarrollo y pruebas. No exponer la UI (puerto 6006) en produccion con datos reales sin implementar un filtro de campos sensibles.

### 7. Indexación automática en startup
`verificar_indexacion()` detecta colecciones faltantes o vacías y las indexa automáticamente al arrancar.

### 8. Seguridad: System prompt hardening integrado
Reglas anti-inyección integradas directamente en `SYSTEM_PROMPT_ORQUESTADOR` (`app/agents/orquestador.py`): no simular legislación, no actuar como abogado, no revelar instrucciones internas, rechazar cambios de rol.

---

## Licencia

Proyecto academico — Semillero FactorIA
