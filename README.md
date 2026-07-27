# Mesa de Ayuda IA para el Departamento Legal — Patito S.A. v2

### Grupo FactorIA | Semillero IA

| Integrantes |
| :--- |
| Anchundia Arichavala Ariel |
| Cruz Figueroa Marcelo |
| Gualli Yuquilema Fanny |

---

## Descripción General

Sistema de inteligencia artificial para el departamento legal de **Patito S.A.**, implementado como aplicación web con **FastAPI + Jinja2 + HTMX**. Utiliza un orquestador multi-agente con **LangChain + Google Gemini + ChromaDB** para responder consultas sobre contratos, protección de datos y cumplimiento normativo, con análisis multimodal de documentos, registro de solicitudes legales y observabilidad vía **Arize Phoenix**.

---

## Video de Demostración

[Ver video de demostración del proyecto](https://drive.google.com/file/d/13reFIH_QKDtup8BBXnY7vETbcfJtFrd9/view?usp=sharing)

---

## Arquitectura del Sistema

```
┌────────────────────────────────────────────────────────────────────┐
│                        NAVEGADOR WEB                               │
│  ┌─────────────────────┐    ┌──────────────────────────────────┐   │
│  │  /registros         │    │  / (Chat)                        │   │
│  │  (tabla solicitudes)│    │  (input, historial, trazabilidad)│   │
│  └─────────────────────┘    └──────────────┬───────────────────┘   │
└────────────────────────────────────────────┼───────────────────────┘
                                             │
                                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                   FASTAPI (app/main.py)                            │
│   Jinja2 + HTMX + CSS / Phoenix OTel / SQLAlchemy async            │
└──────────────────────────┬─────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────────┐
│                      ORQUESTADOR (create_react_agent)              │
│               + InMemorySaver (memoria multi-turno)                │
│                                                                    │
│  System Prompt: ruteo por tema, consolidación multi-agente         │
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
│Chroma│ │Chroma│ │Chroma│  │Gemini     │  │  SQLite         │
│  DB  │ │  DB  │ │  DB  │  │Vision     │  │  solicitudes.db │
└──┬───┘ └──┬───┘ └──┬───┘  └───────────┘  └─────────────────┘
   │        │        │
   ▼        ▼        ▼
┌────────────────────────────────────────────────────────────────────┐
│                 BASE DE CONOCIMIENTO (data/)                       │
│  01_Clausulas_Contractuales.txt                                    │
│  02_Proteccion_Datos.txt                                           │
│  03_Cumplimiento_Etica.txt                                         │
└────────────────────────────────────────────────────────────────────┘

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

## Aplicación de Conceptos del Semillero

Este proyecto aplica los conceptos clave aprendidos en el Semillero de Inteligencia Artificial:

| Concepto del semillero | Implementación en el proyecto |
|------------------------|-------------------------------|
| **Agentes RAG con LangChain** | No se consume la API de Gemini directamente. Cada agente (`contratos.py`, `proteccion_datos.py`, `cumplimiento.py`) usa `LangChain RetrievalQA` con un retriever sobre ChromaDB, system prompt especializado y control de alcance ("no encontré información suficiente..."). |
| **Orquestación con LangGraph** | `create_react_agent` enruta la consulta al agente correcto según el tema, permite invocación multi-agente en consultas mixtas, y mantiene memoria multi-turno con `InMemorySaver`. Sin LangGraph habría que implementar routing manual con if/elif. |
| **Evaluación LLM-as-Judge** | Un segundo LLM (Gemini, temperatura 0) puntúa cada respuesta en 4 criterios legales. Patrón visto en las sesiones de monitoreo de calidad del semillero. |
| **Separación de concerns** | Capas bien diferenciadas: `agents/` (lógica de agente), `services/` (embeddings, ChromaDB, LLM), `routers/` (HTTP), `db/` (modelos ORM). Cada capa es reemplazable independientemente. |
| **Observabilidad con tracing** | Cada invocación del orquestador genera un trace completo en Arize Phoenix, permitiendo depurar qué tool se llamó, cuánto tardó y qué respuesta dio el LLM. |
| **Hardening anti-inyección** | Reglas de seguridad integradas en el system prompt del orquestador, no como capa externa. Aprendido de las sesiones de seguridad del semillero. |

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
4. Abrir http://localhost:8080 y/o http://localhost:6006
```

---

## Instrucciones de Ejecucion

### Requisitos Previos

- **Docker** (Engine 24+ en Linux, Docker Desktop en Windows) — ver [Instalación de Docker](#instalacion-de-docker) abajo
- **docker compose** plugin (incluido en Docker Desktop / Docker Engine)
- **API Key de Google Gemini** (gratuita en [Google AI Studio](https://aistudio.google.com/apikey))

---

### Instalacion de Docker

Si aún no tienes Docker instalado, sigue las instrucciones según tu sistema operativo.

#### Windows

1. Descargar **Docker Desktop** desde [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Ejecutar el instalador (`Docker Desktop Installer.exe`)
3. Durante la instalación, marcar **"Use WSL 2 instead of Hyper-V"** (recomendado)
4. Al finalizar, **Docker Desktop** se inicia automáticamente
5. Abrir **PowerShell** y verificar:
   ```powershell
   docker --version
   ```
   Debe mostrar algo como `Docker version 27.x.x`

> **Nota:** Docker Desktop incluye el plugin `docker compose` automáticamente. No requiere instalación adicional.

#### Linux

Cada distribución usa su propio gestor de paquetes. Ejemplos para las más comunes:

| Distribución | Comandos de instalación |
|-------------|------------------------|
| **Debian / Ubuntu / Mint** | `sudo apt update && sudo apt install docker.io docker-compose-v2` |
| **Arch / Manjaro** | `sudo pacman -S docker docker-compose` |
| **Fedora / RHEL** | `sudo dnf install docker docker-compose` |
| **openSUSE** | `sudo zypper install docker docker-compose` |

Post-instalación (todas las distros):
```bash
# Iniciar Docker al arrancar el sistema
sudo systemctl enable --now docker

# (Opcional) Agregar tu usuario al grupo docker para evitar usar sudo
sudo usermod -aG docker $USER
# ⚠️ Cerrar sesión y volver a entrar para que el cambio surta efecto

# Verificar instalacion
docker --version
```

> **Nota:** En algunas distros el plugin `docker compose` (con espacio) se instala por separado como `docker-compose-v2`. Verifica con `docker compose version`.

---

### Sobre el uso de Docker

**¿Por qué Docker?** El proyecto usa Docker Compose para orquestar la aplicación FastAPI + ChromaDB (servicio HTTP independiente) + Phoenix (opcional). Esto garantiza:

- **Reproducibilidad:** mismo entorno en Windows, Linux o macOS sin instalar dependencias Python manualmente
- **Aislamiento:** ChromaDB corre en su propio contenedor con persistencia en volúmenes, separado del proceso de la app
- **Un solo comando:** `docker compose up --build` levanta todo

**¿Se puede ejecutar sin Docker?**

Sí. El proyecto es una aplicación Python estándar — Docker es el medio de empaquetado, no un requisito de la aplicación en sí.

**Alternativa manual (sin Docker):**

```bash
# 1. Crear entorno virtual e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt

# 2. Configurar .env con GOOGLE_API_KEY (igual que con Docker)

# 3. Iniciar la aplicación
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

En este modo, ChromaDB usa su **cliente persistente local** (archivos en `chroma_data/`) en lugar del servidor HTTP. El código en `chroma_service.py` ya soporta ambos modos automáticamente. Phoenix no estaría disponible a menos que se instale y ejecute por separado.

**Limitaciones del modo sin Docker:**

| Aspecto | Con Docker | Sin Docker |
|---------|-----------|------------|
| ChromaDB | Servidor HTTP aislado (puerto 8000) | Modo embebido local (misma funcionalidad) |
| Phoenix | Contenedor separado con override | Requiere instalación y ejecución manual |
| Setup inicial | `docker compose up --build` | `pip install` + `uvicorn` |
| Aislamiento | Contenedores independientes | Todo en un proceso |
| Persistencia ChromaDB | Volumen Docker (`chroma_data`) | Directorio local (`chroma_data/`) |
| Indexación automática | Funciona igual en ambos modos | Funciona igual |

---

### Paso 1 — Descargar el proyecto

**Opcion A — git clone (Linux / Windows con Git instalado):**

```bash
git clone https://github.com/Marcelo160102/proyecto-final-semillero-ia-v2.git
cd proyecto-final-semillero-ia-v2
```

**Opcion B — Descargar ZIP (Windows / cualquier sistema):**

1. Ir a https://github.com/Marcelo160102/proyecto-final-semillero-ia-v2
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

Cada sección muestra el **prompt exacto** que debes escribir (o acción a realizar) y la **respuesta esperada** del sistema. Todas las consultas se ingresan en el chat en `http://localhost:8080`.

---

#### 6.1 Agente de Contratos (tool: `consultar_contratos`)

| # | Prompt | Respuesta esperada |
|---|--------|-------------------|
| 1 | `¿Qué cláusulas mínimas debe tener un contrato de prestación de servicios?` | El orquestador invoca `consultar_contratos`. Responde enumerando cláusulas como objeto, plazo, remuneración, confidencialidad, resolución de conflictos, etc., citando la base documental. |
| 2 | `¿Cuáles son los tipos de contrato más usados?` | Responde según la colección `contratos` (ej. prestación de servicios, confidencialidad, obra determinada, etc.). |
| 3 | `¿Cómo es el proceso de revisión y firma de un contrato?` | Describe el flujo: recepción → revisión legal → observaciones → aprobación → firma. |

---

#### 6.2 Agente de Protección de Datos (tool: `consultar_proteccion_datos`)

| # | Prompt | Respuesta esperada |
|---|--------|-------------------|
| 1 | `¿Cuáles son los derechos ARCO?` | El orquestador invoca `consultar_proteccion_datos`. Explica Acceso, Rectificación, Cancelación y Oposición según la normativa de la base documental. |
| 2 | `¿Por cuánto tiempo se conservan los datos personales después de cancelar un servicio?` | Responde según la colección `proteccion_datos` (plazo legal de conservación + obligación de bloqueo). |
| 3 | `¿Qué hacer en caso de una violación de seguridad?` | Detalla los pasos: contención, evaluación de impacto, notificación a la autoridad y a los afectados. |

---

#### 6.3 Agente de Cumplimiento (tool: `consultar_cumplimiento`)

| # | Prompt | Respuesta esperada |
|---|--------|-------------------|
| 1 | `¿Cuál es el límite máximo para aceptar regalos?` | El orquestador invoca `consultar_cumplimiento`. Responde con el monto/valor máximo según el código de ética de la base documental. |
| 2 | `¿Cómo funciona el canal de denuncias?` | Explica el proceso: recepción anónima, investigación, resolución, y protección al denunciante. |
| 3 | `¿Qué principios rigen el código de ética?` | Enumera principios como integridad, transparencia, confidencialidad, responsabilidad, etc. |

---

#### 6.4 Consulta Multi-tópico (varios agentes)

| Prompt | Comportamiento esperado |
|--------|------------------------|
| `Necesito redactar un contrato de servicios para un proveedor que tratará datos personales. ¿Qué cláusulas debe incluir y qué requisitos de protección de datos debo cumplir?` | El orquestador detecta **dos temas** distintos e invoca **múltiples tools**: primero `consultar_contratos` (cláusulas contractuales) y luego `consultar_proteccion_datos` (requisitos de datos personales). Consolida ambas respuestas en un solo mensaje. |

---

#### 6.5 Registro de Solicitud Legal (multi-turno con confirmación)

Flujo de **dos turnos** que demuestra persistencia en BD con validación previa.

| Turno | Prompt | Respuesta esperada |
|-------|--------|-------------------|
| **1** | `Quiero registrar una solicitud de revisión de un contrato de confidencialidad con el proveedor DataCorp por un monto de $15,000 por 12 meses. No involucra tratamiento de datos.` | El orquestador invoca `registrar_solicitud_legal`. El agente de acción **valida** los datos y responde con un resumen (tipo, proveedor, monto, plazo, involucra datos) y **pide confirmación** explícita al usuario. |
| **2** | `sí, confirma el registro` | El orquestador re-invoca `registrar_solicitud_legal` con los datos cacheados de la memoria. El agente detecta `confirmado=True` y **persiste** en SQLite. Responde con el ID único generado (ej. `LEG-0001`). |

> Puedes verificar el registro en http://localhost:8080/registros — la tabla debe mostrar la nueva solicitud con su ID, tipo, proveedor, monto y fecha.

---

#### 6.6 Análisis de Imagen (tool: `analizar_imagen_legal`)

| Acción | Prompt | Respuesta esperada |
|--------|--------|-------------------|
| 1. Click en **"Subir imagen"** y seleccionar `img/contrato_demo.png` | *(la imagen se previsualiza)* |
| 2. Escribir: | `Analiza este documento legal` | El orquestador invoca `analizar_imagen_legal`. Gemini Vision procesa la imagen y responde describiendo el contenido: tipo de documento, cláusulas identificadas, partes involucradas, etc. |

> La imagen demo `img/contrato_demo.png` está incluida en el repositorio. Puedes usar cualquier imagen de documento legal.

---

#### 6.7 Consulta Fuera de Alcance

| Prompt | Respuesta esperada |
|--------|-------------------|
| `¿Cuál es la capital de Francia?` | El sistema debe responder: *"No encontré información suficiente en la base documental proporcionada"*, indicando que la pregunta no está cubierta por ningún agente RAG. |

---

## Estructura del Proyecto

```
proyecto-final-semillero-ia-v2/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + lifespan (migracion incluida)
│   ├── templating.py            # Jinja2 + filtros personalizados
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py            # Configuracion via .env
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py          # SQLAlchemy async engine
│   │   └── models.py            # ORM: Consulta (con evaluacion), SolicitudLegal
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── phoenix_setup.py     # OpenTelemetry + LangChainInstrumentor
│   │   └── evaluacion.py        # LLM-as-Judge con rubrica legal
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # responder_rag + extraer_texto (con error handling)
│   │   ├── orquestador.py       # create_react_agent + memoria + hardening
│   │   ├── herramientas.py      # 5 tools del orquestador
│   │   ├── contratos.py         # RAG especializado en contratos
│   │   ├── proteccion_datos.py  # RAG especializado en datos personales
│   │   ├── cumplimiento.py      # RAG especializado en cumplimiento
│   │   ├── multimodal.py        # Analisis de imagenes con Gemini
│   │   └── accion.py            # Registro de solicitudes legales (con cache multi-turno)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py              # GET /, POST /chat, DELETE /historial (con evaluacion + error handling)
│   │   ├── registros.py         # GET /registros
│   │   └── admin.py             # GET /health
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py       # Singleton LLM + Embeddings
│   │   ├── chroma_service.py    # Cliente ChromaDB (HTTP / Persistent) con error handling
│   │   └── embedding_service.py # Indexacion de documentos (DEBUG_INDEXING)
│   ├── templates/
│   │   ├── base.html            # Layout: sidebar + main
│   │   ├── index.html           # Pagina de chat
│   │   ├── registros.html       # Tabla de solicitudes
│   │   └── fragments/
│   │       ├── mensaje_chat.html       # Burbuja completa (historial)
│   │       ├── respuesta_agente.html   # Burbuja solo agente + evaluacion (HTMX)
│   │       └── historial.html          # Lista del sidebar
│   └── static/
│       └── estilo.css           # Estilos completos
├── data/                        # Documentos fuente para RAG
│   ├── 01_Clausulas_Contractuales.txt
│   ├── 02_Proteccion_Datos.txt
│   └── 03_Cumplimiento_Etica.txt
├── scripts/
│   └── indexar.py               # Script de indexacion
├── chroma_data/                 # Persistencia local de ChromaDB (se crea automaticamente)
├── docs/                        # Desarrollo
│   └── CORRECCIONES.md          # Plan de correcciones (ignorado por git)
├── .env.example                 # Template de configuracion
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
| **Cuota de API de Google Gemini** | Alto | Modelo `flash-lite` cuesta ~$0.10/1M tokens input. Con uso moderado (~100 consultas/día) el costo es despreciable, pero uso intensivo puede generar cargos. No hay tracking automático de costos — la UI de Phoenix permite configurar precios manualmente, pero no alerta cuando se acerca a un límite. |
| **Alucinaciones del LLM** | Alto | Cada agente RAG responde **SOLO** desde su base documental (prompt restringe explícitamente inventar normativa). Además, el evaluador LLM-as-Judge penaliza el criterio "Seguridad" si detecta información sin respaldo documental. Sin embargo, ninguna mitigación es 100% efectiva. |
| **Inyección de prompts** | Medio | System prompt hardening con reglas anti-cambio de rol y anti-revelación de instrucciones. El orquestador rechaza explícitamente solicitudes de "ignora las instrucciones anteriores" o "actúa como otro sistema". |
| **Documentos fuera de alcance** | Medio | Cada agente tiene un prompt que le ordena responder "No encontré información suficiente en la base documental proporcionada" si la pregunta no está en sus documentos (verificado en Paso 6.7). |
| **Dependencia de conexión a internet** | Alto | Gemini API, ChromaDB (servicio HTTP) y Phoenix requieren conexión. Sin internet el sistema no funciona. No hay mitigación real — es una limitación arquitectónica. Una versión offline requeriría un LLM local (Ollama, Llama.cpp) y ChromaDB embebido. |
| **ChromaDB o API Gemini no disponible** | Alto | Hay captura de excepciones en `chroma_service.py` y `base.py`. En `chat.py` se muestra un mensaje amigable ("El servicio de base de conocimiento no está disponible"). No hay reintentos automáticos ni degradación graceful. |
| **Datos sensibles expuestos en Phoenix** | Medio | Phoenix captura el contenido completo de consultas, respuestas y argumentos de tools (ej. proveedor, monto). La UI de Phoenix (puerto 6006) no tiene autenticación por defecto. **Mitigación:** no exponer Phoenix en producción o implementar un filtro de campos sensibles antes de enviar el span. |
| **Falsos positivos/negativos del evaluador LLM** | Medio | El LLM-as-Judge con Gemini puede puntuar incorrectamente: aprobar respuestas con alucinaciones o rechazar respuestas correctas. El evaluador usa temperatura 0 para máximo determinismo, pero sigue siendo un LLM — no hay validación humana del puntaje. |
| **Jailbreak exitoso a pesar de hardening** | Medio | El hardening en el system prompt del orquestador reduce pero no elimina el riesgo de inyección. Un prompt adversarial bien diseñado podría engañar al sistema. El evaluador LLM-as-Judge incluye "Seguridad" como criterio de detección posterior. |
| **Archivo de imagen inválido o malicioso** | Bajo | El input de tipo file acepta cualquier archivo. Una imagen corrupta o muy grande puede hacer fallar Gemini Vision o consumir memoria excesiva. Mitigación no implementada (pendiente como mejora futura). |

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
| Media | Sanitización de datos sensibles en UI | Pendiente |

---

### Propuesta de Permisos por Documento/Agente

**Modelo:** RBAC (Role-Based Access Control)

#### Estructura de datos

**Tabla `usuarios`:**
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL REFERENCES permisos_agente(rol)
);
```

**Tabla `permisos_agente`:**
```sql
CREATE TABLE permisos_agente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rol TEXT NOT NULL,
    coleccion TEXT NOT NULL,
    permiso TEXT NOT NULL CHECK(permiso IN ('leer', 'escribir', 'admin'))
);
```

#### Roles sugeridos

| Rol | Colecciones accesibles | Descripción |
|-----|----------------------|-------------|
| `legal` | contratos, cumplimiento | Abogados del área contractual y ética |
| `datos` | proteccion_datos | Oficial de protección de datos |
| `admin` | todas | Administradores del sistema |
| `consulta` | todas (solo lectura) | Auditoría y supervisión |

#### Flujo de autenticación propuesto

1. El usuario ingresa con **username + password** en una página `/login`
2. El servidor valida contra la tabla `usuarios` y establece una **sesión** (cookie firmada o JWT)
3. El rol del usuario se almacena en la sesión y está disponible en cada request
4. El sidebar del chat oculta/muestra agentes según el rol del usuario

#### Enforcement: decorador en tools del orquestador

```python
from functools import wraps
from flask import session  # o request.session

def requiere_permiso(coleccion: str, permiso: str = "leer"):
    def decorador(tool_func):
        @wraps(tool_func)
        async def wrapper(*args, **kwargs):
            rol = session.get("rol", "consulta")
            # verificar en BD: SELECT 1 FROM permisos_agente
            # WHERE rol=? AND coleccion=? AND permiso IN (?, 'admin')
            if not tiene_permiso(rol, coleccion, permiso):
                return "No tienes permiso para acceder a esta información."
            return await tool_func(*args, **kwargs)
        return wrapper
    return decorador
```

Luego se aplica a cada tool:
```python
@tool
@requiere_permiso("contratos", "leer")
async def consultar_contratos(pregunta: str) -> str:
    ...
```

#### UI: visibilidad condicional

Cuando un usuario sin rol `datos` abre el chat, el sistema descarta automáticamente cualquier consulta dirigida a `proteccion_datos` y responde con un mensaje de acceso denegado. La trazabilidad en la UI también oculta las tools no autorizadas.

---

### Propuesta de Monitoreo

| Aspecto | Herramienta | Estado | Detalle |
|---------|-------------|--------|---------|
| **Calidad** | LLM-as-Judge (`app/monitoring/evaluacion.py`) | ✅ **Implementado** | Se ejecuta tras cada respuesta. Ver sección siguiente. |
| **Costos** | Phoenix UI > Settings > Models | ⚠️ **Propuesto** | Configurar precios de Gemini ($0.10/1M input, $0.40/1M output para flash-lite) para estimación automática. No hay automatización — el usuario debe ingresar los precios manualmente en la UI de Phoenix. |
| **Latencia** | Phoenix spans | ⚠️ **Propuesto** | Capturado automáticamente en los spans (duración de cada trace). Umbral sugerido: alertar si > 10s. No hay alerta configurada por defecto — requiere configurar en Phoenix UI. |
| **Errores** | Phoenix traces | ⚠️ **Propuesto** | Filtrar por status=error en la UI de Phoenix. Umbral sugerido: alertar si tasa > 5%. No hay alerta automatizada. |
| **Feedback** | Botón 👍/👎 en cada respuesta | ❌ **No implementado** | Pendiente de desarrollar. Se propone tabla `Feedback` (consulta_id, util, comentario) con reporte semanal de respuestas útiles vs no útiles. |

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

**Referencia al semillero:** Este patrón se exploró en las sesiones de monitoreo de calidad del Semillero, donde se identificó que la autoevaluación con LLM permite detectar alucinaciones, respuestas incompletas y violaciones de seguridad sin intervención humana.

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

**Modelo elegido:** `gemini-3.1-flash-lite` para texto e imágenes. *Trade-off:* sacrificamos la profundidad de razonamiento de Gemini Pro a cambio de **latencia ~2-3s por consulta** y **costo significativamente menor** ($0.10/1M input vs $1.25/1M de Gemini Pro). Para consultas legales basadas en recuperación de documentos existentes (no razonamiento complejo), flash-lite es suficiente.

### 2. Chunking por sección numerada
Los documentos tienen estructura `1.`, `2.`, `3.`. El chunking por cabeceras preserva la unidad semántica de cada bloque legal.

**Cifras reales del corpus actual:**

| Documento | Chunks | Tamaño promedio | Rango |
|-----------|--------|----------------|-------|
| `01_Clausulas_Contractuales.txt` | 4 | ~346 caracteres | 114–807 |
| `02_Proteccion_Datos.txt` | 7 | ~204 caracteres | 100–503 |
| `03_Cumplimiento_Etica.txt` | 6 | ~198 caracteres | 108–445 |

*Trade-off:* chunks pequeños (~200 caracteres) maximizan precisión semántica pero requieren más recuperaciones. El promedio de 200–350 caracteres equivale a 1–2 párrafos legales, unidad natural para una cláusula o artículo. Cada chunk incluye metadatos `{"seccion": i, "fuente": ruta}` para trazabilidad.

### 3. ChromaDB con 3 colecciones independientes
Aislamiento semántico total: una pregunta sobre contratos nunca recupera chunks de datos personales. **Métrica coseno** — mejor para similitud semántica en textos cortos que euclidiana o dot product. Cada agente RAG consulta solo su colección.

### 4. Retriever con k=3
`vectorstore.as_retriever(search_kwargs={"k": 3})` — se recuperan **3 fragmentos** por consulta. *Justificación:* con 3 chunks de ~200–350 caracteres cada uno se cubre ~600–1000 caracteres de contexto legal, suficiente para responder sin exceder la ventana de tokens del LLM. k>3 introduce ruido semántico; k<3 arriesga perder información clave.

### 5. Orquestador con create_react_agent (LangGraph)
Ruteo automático por tema, invocación multi-agente en consultas mixtas, memoria multi-turno con `InMemorySaver`. Trazabilidad con `_extraer_trazas()`. *Alternativa descartada:* `Chain` secuencial de LangChain — no soporta routing dinámico ni memoria entre turnos.

### 6. Agente de acción con control de flujo 3 niveles
Validación → Confirmación → Persistencia. Nunca escribe sin `confirmado=True`. ID único LEG-XXXX.

### 7. Observabilidad con Phoenix
OTLP HTTP sobre `BatchSpanProcessor`. Sin healthcheck TCP — el buffer interno maneja la indisponibilidad temporal de Phoenix.

> **Advertencia de seguridad:** Phoenix captura el contenido completo de las consultas y respuestas (preguntas, argumentos de tools como proveedor/monto, y respuestas del LLM). Esta diseñado para entornos de desarrollo y pruebas. No exponer la UI (puerto 6006) en produccion con datos reales sin implementar un filtro de campos sensibles.

### 8. Indexación automática en startup
`verificar_indexacion()` detecta colecciones faltantes o vacías y las indexa automáticamente al arrancar.

### 9. Seguridad: System prompt hardening integrado
Reglas anti-inyección integradas directamente en `SYSTEM_PROMPT_ORQUESTADOR` (`app/agents/orquestador.py`): no simular legislación, no actuar como abogado, no revelar instrucciones internas, rechazar cambios de rol.

### 10. Trazabilidad de fuentes en cada respuesta
Cada respuesta del orquestador incluye un bloque de **trazabilidad** que muestra:
- Las herramientas (tools) que se invocaron (ej. `consultar_contratos`, `analizar_imagen_legal`)
- Los fragmentos recuperados de ChromaDB con su **fuente** (archivo `.txt`) y **sección** (`"seccion": 2`)

Esto permite al usuario legal verificar que la respuesta está respaldada por la base documental y saber exactamente qué documento y sección se consultó. Implementado en `herramientas.py` mediante la función `_extraer_trazas()` que extrae los metadatos de los retrieved documents.