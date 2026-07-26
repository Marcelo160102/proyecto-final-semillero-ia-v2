# Mesa de Ayuda IA para el Departamento Legal — Patito S.A. v2

**Grupo FactorIA** | Semillero Final

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
  - Evaluación: LLM-as-Judge con rúbrica legal (app/evaluacion.py)
  - Seguridad: System prompt hardening anti-inyección (app/hardening.py)
```

### Componentes Principales

| Capa | Componente | Tecnología |
|------|-----------|------------|
| **Frontend** | Jinja2 + HTMX + CSS | FastAPI |
| **Orquestador** | `create_react_agent` + `InMemorySaver` | LangChain + LangGraph |
| **Agentes RAG** | 3 agentes especializados (Contratos, Datos, Cumplimiento) | LangChain Retriever |
| **Base vectorial** | 3 colecciones Chroma independientes (métrica coseno) | ChromaDB |
| **Embeddings** | `gemini-embedding-2-preview` | Google Generative AI |
| **LLM** | `gemini-3.1-flash-lite` (texto + imágenes) | Google Generative AI |
| **Visión** | Análisis de documentos legales (imagen → Gemini) | LangChain + Gemini |
| **Acción** | Registro de solicitudes con validación y confirmación | SQLAlchemy + SQLite |
| **Observabilidad** | Tracing automático de cada invoke | Arize Phoenix + OTel |
| **Evaluación** | Juez LLM con rúbrica legal | Gemini (temperatura 0) |
| **Despliegue** | Docker Compose | Contenedores |

---

## Flujo de Ejecución

```
1. Clonar repositorio
       ↓
2. Configurar .env con GOOGLE_API_KEY
       ↓
3. docker compose up --build  (sin Phoenix)
   O docker compose -f docker-compose.yml -f docker-compose.phoenix.yml up --build
       ↓
4. Indexar documentos en ChromaDB:
   docker compose exec app python scripts/indexar.py
       ↓
5. Abrir http://localhost:8080 (App)
   O http://localhost:6006  (Phoenix)
```

---

## Instrucciones de Ejecución

### Requisitos Previos

- **Docker** (Engine 24+ o Docker Desktop)
- **docker compose** plugin (incluido en Docker Desktop / Docker Engine)
- **API Key de Google Gemini** (gratuita en [Google AI Studio](https://aistudio.google.com/apikey))

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/Marcelo_CF/proyecto-final-semillero-ia-v2.git
cd proyecto-final-semillero-ia-v2
```

### Paso 2 — Configurar la API Key

Copia el archivo de ejemplo y edítalo con tu API Key:

```bash
cp .env.example .env
```

Edita `.env` y pega tu API Key de Gemini:

```
GOOGLE_API_KEY=tu_api_key_aqui
```

### Paso 3 — Ejecutar con Docker

**Sin Phoenix (recomendado para inicio rápido):**

```bash
docker compose up --build
```

**Con Phoenix (observabilidad):**

```bash
docker compose -f docker-compose.yml -f docker-compose.phoenix.yml up --build
```

> La imagen de Phoenix (`arizephoenix/phoenix:latest`) es pública en Docker Hub — no requiere autenticación.

### Paso 4 — Indexar los documentos en ChromaDB

Con los contenedores corriendo, ejecuta el script de indexación:

```bash
docker compose exec app python scripts/indexar.py
```

Esto carga los 3 documentos de `data/` en colecciones separadas de ChromaDB (contratos, proteccion_datos, cumplimiento).

### Paso 5 — Abrir la aplicación

| Servicio | URL |
|----------|-----|
| App | http://localhost:8080 |
| Phoenix | http://localhost:6006 (solo si usas el override) |

### Paso 6 — Uso del chat

- Escribe consultas legales sobre contratos, protección de datos o cumplimiento
- Adjunta imágenes de documentos legales para análisis multimodal
- Registra solicitudes de revisión/elaboración de contratos (el sistema valida datos y pide confirmación)
- El historial y las solicitudes se persisten en SQLite

### Paso 7 — Detener y limpiar

```bash
# Detener contenedores (conserva datos)
docker compose stop

# Detener y eliminar contenedores + volúmenes (borra todo)
docker compose -f docker-compose.yml -f docker-compose.phoenix.yml down -v
```

---

## Decisiones Técnicas

### 1. Gemini como proveedor único

Se utiliza **Google Gemini** tanto para el LLM como para los embeddings, simplificando la configuración con una sola API Key.

- **LLM:** `gemini-3.1-flash-lite` — modelo ultraligero y multimodal
- **Embeddings:** `gemini-embedding-2-preview` — representación vectorial precisa

### 2. Chunking por sección numerada

Los documentos legales tienen estructura numerada (`1.`, `2.`, `3.`...). Cortar por secciones preserva la unidad semántica de cada bloque. Cada chunk mantiene referencia a su número de sección y archivo fuente.

### 3. ChromaDB con 3 colecciones independientes

Cada dominio legal tiene su propia colección Chroma. Esto garantiza aislamiento semántico y especialización de cada agente RAG. Se usa métrica coseno para similitud semántica.

### 4. Orquestador con create_react_agent

Se usa `create_react_agent` de LangChain con `InMemorySaver` para ruteo automático, invocación multi-agente en consultas mixtas, memoria multi-turno y trazabilidad.

### 5. Agente de acción con control de flujo

Registro de solicitudes en 3 niveles: validación de campos obligatorios, confirmación con resumen y persistencia solo con `confirmado=True`.

### 6. Observabilidad con Phoenix

Phoenix captura automáticamente cada invocación al orquestador. Se inicializa en el `lifespan` de FastAPI usando OpenTelemetry + LangChainInstrumentor. No requiere healthcheck TCP — el `BatchSpanProcessor` bufferiza los spans internamente.

### 7. Frontend con Jinja2 + HTMX

Sin framework JS pesado. HTMX maneja la interactividad (envío de formularios, actualización del historial, scroll automático) con atributos HTML. El indicador de carga usa la clase `.htmx-request` que HTMX añade automáticamente durante las peticiones.

### 8. Seguridad: System prompt hardening

Reglas anti-inyección en el system prompt: no cambiar de rol, no revelar instrucciones internas, responder únicamente sobre temas legales.

---

## Estructura del Proyecto

```
proyecto-final-semillero-ia-v2/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + lifespan
│   ├── config.py                # Configuración vía .env
│   ├── database.py              # SQLAlchemy async engine
│   ├── models.py                # ORM: Consulta, SolicitudLegal
│   ├── schemas.py               # Pydantic schemas
│   ├── templating.py            # Jinja2 + filtros personalizados
│   ├── phoenix_setup.py         # OpenTelemetry + LangChainInstrumentor
│   ├── hardening.py             # Orquestador con system prompt hardening
│   ├── evaluacion.py            # LLM-as-Judge con rúbrica legal
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # responder_rag + extraer_texto
│   │   ├── orquestador.py       # create_react_agent + memoria
│   │   ├── herramientas.py      # 5 tools del orquestador
│   │   ├── contratos.py         # RAG especializado en contratos
│   │   ├── proteccion_datos.py  # RAG especializado en datos personales
│   │   ├── cumplimiento.py      # RAG especializado en cumplimiento
│   │   ├── multimodal.py        # Análisis de imágenes con Gemini
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
│   │   └── embedding_service.py # Indexación de documentos
│   ├── templates/
│   │   ├── base.html            # Layout: sidebar + main
│   │   ├── index.html           # Página de chat
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
│   └── indexar.py               # Script de indexación
├── chroma_data/                 # Persistencia local de ChromaDB
├── docs/
│   └── README.md                # Documentación original del notebook
├── solicitudes.db               # SQLite (se crea automáticamente)
├── .env.example                 # Template de configuración
├── docker-compose.yml           # App + ChromaDB
├── docker-compose.phoenix.yml   # Override con Phoenix
├── Dockerfile
├── .dockerignore
└── requirements.txt
```

---

## Riesgos y Limitaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| **Cuota de API de Google Gemini** | Alto | Modelo `flash-lite` tiene costos bajos; Phoenix trackea uso por consulta |
| **Alucinaciones del LLM** | Alto | Cada agente RAG responde SOLO desde su base documental; prompts con instrucciones estrictas |
| **Inyección de prompts** | Medio | System prompt hardening con reglas anti-cambio de rol |
| **Documentos fuera de alcance** | Medio | Agentes responden "No tengo esa información" cuando la consulta no está en sus bases |
| **Latencia de la API** | Bajo | Modelo `flash-lite` es ultrarrápido; chunking por sección reduce contexto |
| **Pérdida de memoria entre sesiones** | Bajo | `InMemorySaver` mantiene contexto dentro de la sesión; se pierde al cerrar |
| **Dependencia de conexión a internet** | Alto | Gemini, ChromaDB y Phoenix requieren conexión |
| **Tamaño de documentos** | Bajo | Chunking por sección maneja documentos de cualquier tamaño |

---

## Stack Tecnológico

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Python | 3.12 (imagen Docker: 3.12-slim) | Lenguaje principal |
| FastAPI | >=0.115.0 | Framework web |
| Uvicorn | >=0.30.0 | Servidor ASGI |
| Jinja2 | >=3.1.0 | Motor de plantillas |
| HTMX | 2.0.4 | Interactividad frontend |
| LangChain | >=1.3.0 | Framework de agentes |
| LangGraph | >=1.0.0 | Checkpointing y memoria |
| Google Gemini | `gemini-3.1-flash-lite` | LLM (texto + imágenes) |
| Google Gemini | `gemini-embedding-2-preview` | Generación de embeddings |
| ChromaDB | >=0.5.0 | Base de datos vectorial |
| SQLAlchemy | >=2.0.0 | ORM asíncrono |
| Arize Phoenix | >=13.21.0 | Observabilidad y tracing |
| OpenInference | >=0.1.0 | Instrumentación LangChain |
| Docker | 24+ | Contenedores |

---

## Licencia

Proyecto académico — Semillero FactorIA
