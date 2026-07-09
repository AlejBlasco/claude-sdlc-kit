<div align="center">

# 🔄 SDLC Kit for Claude Code

**Slash commands + subagents that turn Claude Code into an end-to-end software delivery pipeline.**

![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-6E56CF?logo=anthropic&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-10-512BD4?logo=dotnet&logoColor=white)
![Blazor](https://img.shields.io/badge/Blazor-Ready-512BD4?logo=blazor&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-Ready-0078D4?logo=microsoftazure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Agile](https://img.shields.io/badge/Process-Agile-3DDC97)
![Version](https://img.shields.io/badge/version-2.0-blue)
![No Git Autopilot](https://img.shields.io/badge/git%20commit%2Fpush-never%20automatic-critical)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-ff69b4)

**[English](#-english)** • **[Español](#-español)**

</div>

---

## 🇬🇧 English

A set of six `sdlc-*` slash commands, each backed by a dedicated subagent, that walk a feature through the full software development lifecycle — from a raw idea to tested, documented code — while leaving every `git commit`/`git push` decision in your hands.

### 📋 Pipeline at a glance

| # | Phase | Command | Agent |
|---|---|---|---|
| 1 | Requirements Analysis | `/sdlc-analysis` | 🧑‍💼 Business Analyst |
| 2 | Design | `/sdlc-design` | 🏗️ Software Architect |
| 3 | Development & Programming | `/sdlc-development` | 👨‍💻 Software Developer |
| 4 | Documentation | `/sdlc-documentation` | ✍️ Technical Writer |
| 5 | Testing | `/sdlc-testing` | 🧪 QA Engineer |
| 6 | Implementation & Maintenance | `/sdlc-implementation` | 🚢 DevOps Engineer *(reserved)* |

### 🧢 Interactive-only agents

Some agents in this kit are **not** wired to any `sdlc-*` slash command —
they exist purely for direct, ad hoc conversations with the user, invoked
on demand (e.g. by asking Claude to use them) rather than as a pipeline
step.

| Agent | Purpose |
|---|---|
| 🦆 **Rubber Duck** | A Socratic debugging partner. Explain your problem, approach, and assumptions; it only replies with short probing questions ("What else?", "Are you sure?") — never code, never the answer — until you say you've figured it out. |

### 📦 Installation

Copy the `.claude/` folder from this kit into the root of your target repository, merging with any existing `.claude/` folder you already have (don't overwrite unrelated files):

```
your-repo/
└── .claude/
    ├── sdlc.config.yaml
    ├── agents/
    │   ├── business-analyst.md
    │   ├── software-architect.md
    │   ├── software-developer.md
    │   ├── technical-writer.md
    │   ├── qa-engineer.md
    │   └── devops-engineer.md
    ├── commands/
    │   ├── sdlc-analysis.md
    │   ├── sdlc-design.md
    │   ├── sdlc-development.md
    │   ├── sdlc-documentation.md
    │   ├── sdlc-testing.md
    │   └── sdlc-implementation.md
    └── skills/
        ├── business-analyst/...
        ├── software-architect/...
        ├── software-developer/...
        ├── technical-writer/...
        ├── qa-engineer/...
        └── devops-engineer/...
```

Restart/reload Claude Code in that repo so it picks up the new agents and commands.

### ⚙️ Configuration

Edit `.claude/sdlc.config.yaml`:

| Key | Default | Meaning |
|---|---|---|
| `xmlDocComments` | `es` | Language for in-code documentation comments (XMLDoc/JSDoc/docstrings/etc.) written by the Software Developer agent. |
| `documentation` | `es` | Language for all generated markdown documentation (requirements, design, implementation summaries, technical/functional docs, testing summaries). |
| `testingCoverage` | `70` | Minimum desired test coverage percentage (0-100) the QA Engineer agent aims for. |
| `paths.requirements` | `docs/sdlc/requirements` | Output folder for `sdlc-analysis`. |
| `paths.design` | `docs/sdlc/design` | Output folder for `sdlc-design`. |
| `paths.development` | `docs/sdlc/development` | Output folder for `sdlc-development`'s implementation summary. |
| `paths.technicalDocs` | `docs/technical` | Output folder for the technical document from `sdlc-documentation`. |
| `paths.functionalDocs` | `docs/functional` | Output folder for the functional document from `sdlc-documentation`. |
| `paths.testing` | `docs/sdlc/testing` | Output folder for `sdlc-testing`'s summary. |

### 🚀 Usage

Each command accepts either:

- 📄 a path to a markdown file produced by a previous phase (chaining the pipeline),
- 🔗 a URL to a work item (Azure DevOps, GitHub/GitLab Issue, Jira, etc.), or
- 💬 a free-text description typed directly after the command.

```
/sdlc-analysis Users should be able to reset their password via email
/sdlc-design docs/sdlc/requirements/password-reset.md
/sdlc-development docs/sdlc/design/password-reset.md
/sdlc-documentation docs/sdlc/development/password-reset.md
/sdlc-testing docs/sdlc/development/password-reset.md
```

The natural flow is **analysis → design → development → (documentation and testing, in either order)**. `sdlc-implementation` is reserved for a future version of this kit.

### 🧠 Ecosystem skills (.NET 10 / Azure / Blazor)

Pre-loaded skill files tuned for a Microsoft-stack team, auto-loaded by each agent when relevant:

- **🧑‍💼 Business Analyst** — Agile requirements framing (INVEST, DoR/DoD).
- **🏗️ Software Architect** — .NET + Azure architecture choices, CQRS/Mediator decision-making, .NET solution structure & naming.
- **👨‍💻 Software Developer** — .NET 10 conventions, EF Core patterns, Blazor components, CQRS/Mediator implementation, Docker for .NET, Microsoft naming conventions, SOLID principles.
- **🧪 QA Engineer** — .NET testing with xUnit (+ Moq, WebApplicationFactory, Testcontainers), Blazor component testing with bUnit.
- **🚢 DevOps Engineer** — Azure CI/CD reference (reserved — the agent stays a stub until this phase is activated).

### 🔒 Hard invariant — no commit, no push

Every agent, command, and skill in this kit is explicitly instructed to **never** run `git commit`, `git push`, or any equivalent action — under any circumstance, even mid-session user requests. Committing and pushing is always a deliberate, manual action performed by **you**, after reviewing what was generated.

### 🧩 Extending the kit

- Add more skill files under `.claude/skills/<agent>/` as plain markdown — each agent reads the ones relevant to its current task automatically.
- `devops-engineer` / `sdlc-implementation` is intentionally a stub. Define its scope (target environments, CI/CD tooling, rollback strategy) before fleshing it out.

---

## 🇪🇸 Español

Un conjunto de seis slash commands `sdlc-*`, cada uno respaldado por un subagente dedicado, que acompañan a una funcionalidad a través de todo el ciclo de vida del desarrollo software — desde una idea en bruto hasta código probado y documentado — dejando siempre en tus manos la decisión de hacer `git commit`/`git push`.

### 📋 El pipeline de un vistazo

| # | Fase | Comando | Agente |
|---|---|---|---|
| 1 | Análisis de Requisitos | `/sdlc-analysis` | 🧑‍💼 Business Analyst |
| 2 | Diseño | `/sdlc-design` | 🏗️ Software Architect |
| 3 | Desarrollo y Programación | `/sdlc-development` | 👨‍💻 Software Developer |
| 4 | Documentación | `/sdlc-documentation` | ✍️ Technical Writer |
| 5 | Testing | `/sdlc-testing` | 🧪 QA Engineer |
| 6 | Implementación y Mantenimiento | `/sdlc-implementation` | 🚢 DevOps Engineer *(reservado)* |

### 🧢 Agentes solo interactivos

Algunos agentes de este kit **no** están conectados a ningún slash command
`sdlc-*` — existen únicamente para conversaciones directas y puntuales con
el usuario, invocados a demanda (por ejemplo pidiéndole a Claude que los
use) en lugar de como paso del pipeline.

| Agente | Propósito |
|---|---|
| 🦆 **Rubber Duck** | Compañero de debugging socrático. Le explicas tu problema, tu enfoque y tus suposiciones; solo responde con preguntas cortas ("¿Qué más?", "¿Seguro?") — nunca código, nunca la respuesta — hasta que dices que ya lo has resuelto. |

### 📦 Instalación

Copia la carpeta `.claude/` de este kit a la raíz de tu repositorio, fusionándola con cualquier `.claude/` que ya tengas (sin sobrescribir ficheros que no pertenezcan a este kit):

```
tu-repo/
└── .claude/
    ├── sdlc.config.yaml
    ├── agents/
    │   ├── business-analyst.md
    │   ├── software-architect.md
    │   ├── software-developer.md
    │   ├── technical-writer.md
    │   ├── qa-engineer.md
    │   └── devops-engineer.md
    ├── commands/
    │   ├── sdlc-analysis.md
    │   ├── sdlc-design.md
    │   ├── sdlc-development.md
    │   ├── sdlc-documentation.md
    │   ├── sdlc-testing.md
    │   └── sdlc-implementation.md
    └── skills/
        ├── business-analyst/...
        ├── software-architect/...
        ├── software-developer/...
        ├── technical-writer/...
        ├── qa-engineer/...
        └── devops-engineer/...
```

Reinicia/recarga Claude Code en ese repositorio para que reconozca los nuevos agentes y comandos.

### ⚙️ Configuración

Edita `.claude/sdlc.config.yaml`:

| Clave | Por defecto | Significado |
|---|---|---|
| `xmlDocComments` | `es` | Idioma de los comentarios de documentación en código (XMLDoc/JSDoc/docstrings/etc.) que escribe el Software Developer. |
| `documentation` | `es` | Idioma de toda la documentación markdown generada (requisitos, diseño, resúmenes de implementación, documentación técnica/funcional, resúmenes de testing). |
| `testingCoverage` | `70` | Porcentaje mínimo de cobertura de tests (0-100) al que aspira el QA Engineer. |
| `paths.requirements` | `docs/sdlc/requirements` | Carpeta de salida de `sdlc-analysis`. |
| `paths.design` | `docs/sdlc/design` | Carpeta de salida de `sdlc-design`. |
| `paths.development` | `docs/sdlc/development` | Carpeta de salida del resumen de implementación de `sdlc-development`. |
| `paths.technicalDocs` | `docs/technical` | Carpeta de salida del documento técnico de `sdlc-documentation`. |
| `paths.functionalDocs` | `docs/functional` | Carpeta de salida del documento funcional de `sdlc-documentation`. |
| `paths.testing` | `docs/sdlc/testing` | Carpeta de salida del resumen de `sdlc-testing`. |

### 🚀 Uso

Cada comando acepta:

- 📄 una ruta a un fichero markdown generado por una fase anterior (encadenando el pipeline),
- 🔗 una URL a un elemento de trabajo (Azure DevOps, GitHub/GitLab Issue, Jira, etc.), o
- 💬 una descripción en texto libre escrita directamente tras el comando.

```
/sdlc-analysis Los usuarios deben poder resetear su contraseña por email
/sdlc-design docs/sdlc/requirements/password-reset.md
/sdlc-development docs/sdlc/design/password-reset.md
/sdlc-documentation docs/sdlc/development/password-reset.md
/sdlc-testing docs/sdlc/development/password-reset.md
```

El flujo natural es **análisis → diseño → desarrollo → (documentación y testing, en cualquier orden)**. `sdlc-implementation` queda reservado para una futura versión del kit.

### 🧠 Skills del ecosistema (.NET 10 / Azure / Blazor)

Skills precargados y orientados a un equipo con stack Microsoft, que cada agente carga automáticamente cuando es relevante:

- **🧑‍💼 Business Analyst** — enfoque Agile de requisitos (INVEST, DoR/DoD).
- **🏗️ Software Architect** — decisiones de arquitectura .NET + Azure, criterio para adoptar CQRS/Mediator, estructura y naming de soluciones .NET.
- **👨‍💻 Software Developer** — convenciones de .NET 10, patrones de EF Core, componentes Blazor, implementación de CQRS/Mediator, Docker para .NET, naming conventions de Microsoft, principios SOLID.
- **🧪 QA Engineer** — testing .NET con xUnit (+ Moq, WebApplicationFactory, Testcontainers), testing de componentes Blazor con bUnit.
- **🚢 DevOps Engineer** — referencia de CI/CD en Azure (reservado — el agente sigue siendo un stub hasta que se active esta fase).

### 🔒 Invariante — nunca commit, nunca push

Todos los agentes, comandos y skills de este kit tienen la instrucción explícita de **no ejecutar nunca** `git commit`, `git push` ni ninguna acción equivalente, bajo ninguna circunstancia, ni siquiera si se pide durante la sesión. Hacer commit y push es siempre una acción manual y deliberada de **la persona usuaria**, tras revisar lo generado.

### 🧩 Ampliar el kit

- Añade más skills en `.claude/skills/<agente>/` como markdown plano — cada agente ya está instruido para leer los que sean relevantes para su tarea.
- `devops-engineer` / `sdlc-implementation` es un stub intencionado. Define su alcance (entornos objetivo, herramientas de CI/CD, estrategia de rollback) antes de desarrollarlo.

