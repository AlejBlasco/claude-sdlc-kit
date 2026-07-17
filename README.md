<div align="center">

# 🔄 SDLC Kit for Claude Code

**Slash commands + subagents that turn Claude Code into an end-to-end software delivery pipeline.**

![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-6E56CF?logo=anthropic&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-10-512BD4?logo=dotnet&logoColor=white)
![Blazor](https://img.shields.io/badge/Blazor-Ready-512BD4?logo=blazor&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-Ready-0078D4?logo=microsoftazure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Agile](https://img.shields.io/badge/Process-Agile-3DDC97)
![Version](https://img.shields.io/badge/version-2.4-blue)
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
| 6 | Implementation & Maintenance | `/sdlc-implementation` | 🚢 DevOps Engineer |

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
├── .claude/
│   ├── sdlc.config.yaml
│   ├── agents/
│   │   ├── business-analyst.md
│   │   ├── software-architect.md
│   │   ├── software-developer.md
│   │   ├── technical-writer.md
│   │   ├── qa-engineer.md
│   │   └── devops-engineer.md
│   ├── commands/
│   │   ├── sdlc-analysis.md
│   │   ├── sdlc-design.md
│   │   ├── sdlc-development.md
│   │   ├── sdlc-documentation.md
│   │   ├── sdlc-testing.md
│   │   └── sdlc-implementation.md
│   └── skills/
│       ├── business-analyst/...
│       ├── software-architect/...
│       ├── software-developer/...
│       ├── technical-writer/...
│       ├── qa-engineer/...
│       └── devops-engineer/...
└── .github/
    └── ISSUE_TEMPLATE/
        ├── feature_request.md
        └── bug_report.md
```

Restart/reload Claude Code in that repo so it picks up the new agents and commands.

### ⚙️ Configuration

Edit `.claude/sdlc.config.yaml`:

| Key | Default | Meaning |
|---|---|---|
| `xmlDocComments` | `es` | Language for in-code documentation comments (XMLDoc/JSDoc/docstrings/etc.) written by the Software Developer agent. |
| `documentation` | `es` | Language for all generated markdown documentation (requirements, design, implementation summaries, technical/functional docs, testing summaries). |
| `issueTemplates` | `en` | Language used in the static GitHub issue templates under `.github/ISSUE_TEMPLATE/` (not read by any agent at runtime — just documents what language they were written in; `feature_request.md` follows the user's own real-world template). |
| `testingCoverage` | `70` | Minimum desired test coverage percentage (0-100) the QA Engineer agent aims for. |
| `paths.requirements` | `docs/sdlc/requirements` | Output folder for `sdlc-analysis`. |
| `paths.design` | `docs/sdlc/design` | Output folder for `sdlc-design`. |
| `paths.development` | `docs/sdlc/development` | Output folder for `sdlc-development`'s implementation summary. |
| `paths.technicalDocs` | `docs/technical` | Output folder for the technical document from `sdlc-documentation`. |
| `paths.functionalDocs` | `docs/functional` | Output folder for the functional document from `sdlc-documentation`. |
| `paths.testing` | `docs/sdlc/testing` | Output folder for `sdlc-testing`'s summary. |
| `paths.deployment` | `docs/sdlc/deployment` | Output folder for `sdlc-implementation`'s deployment runbook. |

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

The natural flow is **analysis → design → development → (documentation and testing, in either order) → implementation**. `sdlc-implementation` prepares/reviews deployment artifacts (Compose stacks, CI/CD pipeline, runbooks) — it never deploys anything itself.

### 🐛 Issue templates

`.github/ISSUE_TEMPLATE/feature_request.md` and `bug_report.md` ship with
the kit so that raw input filed on GitHub is already structured enough to
feed straight into `/sdlc-analysis` (context, actors, expected behavior for
features; repro steps, expected vs. actual for bugs). They're plain static
Markdown templates filled in by humans — no agent reads them at runtime.

**How this GitHub feature actually works:** GitHub scans
`.github/ISSUE_TEMPLATE/` on the repository's default branch. If it finds
files there, clicking **New issue** shows a template chooser instead of a
blank issue. Each `.md` template needs a YAML front matter block —
`name`, `about`, `title`, `labels`, `assignees` — followed by the
Markdown body; `name` must be longer than 3 characters or GitHub won't
list it. The `labels` field auto-applies existing repo labels to the
issue (it won't create a label that doesn't exist yet). You can drop an
optional `config.yml` in the same folder to disable the blank-issue
option for external contributors (`blank_issues_enabled: false`) or add
external `contact_links`. There's also a newer, structured alternative —
`.yml` "issue forms" with typed fields (dropdowns, checkboxes, file
uploads) — which we didn't use here since a Markdown template already
matches the user's existing workflow. Full reference: [GitHub Docs —
Configuring issue templates for your
repository](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository).

### 🔁 Closing the loop on open questions

`sdlc-analysis` and `sdlc-design` don't just drop open questions/risks into
the document and move on. Once the document is written, the command reads
its "Dependencies" (analysis — looking for `Open question:` bullets) or
"Risks & Open Decisions" (design) section:

- **Nothing open?** It just points you to the next command, as usual.
- **Something open?** It rephrases each item as a direct question, lists
  them for you right there in the conversation, and **waits for your
  answers** instead of leaving them buried in the file. Once you answer,
  it delegates back to the same agent to update the document in place —
  resolving those items and adjusting any section your answers affect —
  before pointing you to the next phase.

This closes a gap where those documents used to come out "done" but full
of loose threads the user had to notice and chase down manually.

### 🧠 Ecosystem skills (.NET 10 / Azure / Blazor)

Pre-loaded skill files tuned for a Microsoft-stack team, auto-loaded by each agent when relevant:

- **🧑‍💼 Business Analyst** — Agile requirements framing (INVEST, DoR/DoD).
- **🏗️ Software Architect** — .NET + Azure architecture choices, CQRS/Mediator decision-making, .NET solution structure & naming.
- **👨‍💻 Software Developer** — .NET 10 conventions, EF Core patterns, Blazor components, CQRS/Mediator implementation, Docker for .NET, Microsoft naming conventions, SOLID principles.
- **🧪 QA Engineer** — .NET testing with xUnit (+ Moq, WebApplicationFactory, Testcontainers), Blazor component testing with bUnit.
- **🚢 DevOps Engineer** — Azure CI/CD reference, plus self-hosted custom server deployment with Docker, GHCR and Portainer.

### 🚢 Self-hosted deployment (Docker + Portainer)

For teams running a custom, self-hosted server instead of a cloud
provider, `sdlc-implementation` knows how to wire up a full release flow:
build and push images to GitHub Container Registry (GHCR) from `cd.yaml`,
then apply them to a single Portainer node running multiple stacks, via
whichever mechanism fits the setup:

- **Portainer webhook** triggered from the last step of `cd.yaml` (needs
  Portainer's free Business Edition tier, available forever for up to 3
  nodes — CE alone doesn't support this).
- **Git polling** on the Portainer side, if you'd rather not store a
  webhook secret.
- **Self-hosted GitHub Actions runner** on the custom server itself, if you want
  to stay on Portainer CE with no GitOps dependency at all.
- **Manual pull-and-redeploy** in the Portainer UI, always documented as
  the fallback regardless of which automation is chosen.

It never connects to the custom server itself — it only edits Compose/pipeline
files and documents the one-time manual setup (e.g. enabling the webhook
in Portainer, adding the secret to GitHub) that the user performs outside
the repo.

### 🔒 Hard invariant — no commit, no push

Every agent, command, and skill in this kit is explicitly instructed to **never** run `git commit`, `git push`, or any equivalent action — under any circumstance, even mid-session user requests. Committing and pushing is always a deliberate, manual action performed by **you**, after reviewing what was generated.

### 🧩 Extending the kit

- Add more skill files under `.claude/skills/<agent>/` as plain markdown — each agent reads the ones relevant to its current task automatically.
- `devops-engineer` / `sdlc-implementation` now prepares real deployment artifacts (Azure or self-hosted Docker/Portainer) but still never executes anything against a remote host — extend its skills under `.claude/skills/devops-engineer/` for other targets (e.g. a different cloud, Kubernetes) the same way.

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
| 6 | Implementación y Mantenimiento | `/sdlc-implementation` | 🚢 DevOps Engineer |

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
├── .claude/
│   ├── sdlc.config.yaml
│   ├── agents/
│   │   ├── business-analyst.md
│   │   ├── software-architect.md
│   │   ├── software-developer.md
│   │   ├── technical-writer.md
│   │   ├── qa-engineer.md
│   │   └── devops-engineer.md
│   ├── commands/
│   │   ├── sdlc-analysis.md
│   │   ├── sdlc-design.md
│   │   ├── sdlc-development.md
│   │   ├── sdlc-documentation.md
│   │   ├── sdlc-testing.md
│   │   └── sdlc-implementation.md
│   └── skills/
│       ├── business-analyst/...
│       ├── software-architect/...
│       ├── software-developer/...
│       ├── technical-writer/...
│       ├── qa-engineer/...
│       └── devops-engineer/...
└── .github/
    └── ISSUE_TEMPLATE/
        ├── feature_request.md
        └── bug_report.md
```

Reinicia/recarga Claude Code en ese repositorio para que reconozca los nuevos agentes y comandos.

### ⚙️ Configuración

Edita `.claude/sdlc.config.yaml`:

| Clave | Por defecto | Significado |
|---|---|---|
| `xmlDocComments` | `es` | Idioma de los comentarios de documentación en código (XMLDoc/JSDoc/docstrings/etc.) que escribe el Software Developer. |
| `documentation` | `es` | Idioma de toda la documentación markdown generada (requisitos, diseño, resúmenes de implementación, documentación técnica/funcional, resúmenes de testing). |
| `issueTemplates` | `en` | Idioma de las plantillas estáticas de GitHub Issues en `.github/ISSUE_TEMPLATE/` (ningún agente la lee en tiempo real — solo documenta en qué idioma están escritas; `feature_request.md` sigue la plantilla real que ya usa el usuario). |
| `testingCoverage` | `70` | Porcentaje mínimo de cobertura de tests (0-100) al que aspira el QA Engineer. |
| `paths.requirements` | `docs/sdlc/requirements` | Carpeta de salida de `sdlc-analysis`. |
| `paths.design` | `docs/sdlc/design` | Carpeta de salida de `sdlc-design`. |
| `paths.development` | `docs/sdlc/development` | Carpeta de salida del resumen de implementación de `sdlc-development`. |
| `paths.technicalDocs` | `docs/technical` | Carpeta de salida del documento técnico de `sdlc-documentation`. |
| `paths.functionalDocs` | `docs/functional` | Carpeta de salida del documento funcional de `sdlc-documentation`. |
| `paths.testing` | `docs/sdlc/testing` | Carpeta de salida del resumen de `sdlc-testing`. |
| `paths.deployment` | `docs/sdlc/deployment` | Carpeta de salida del runbook de despliegue de `sdlc-implementation`. |

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

El flujo natural es **análisis → diseño → desarrollo → (documentación y testing, en cualquier orden) → implementación**. `sdlc-implementation` prepara/revisa artefactos de despliegue (stacks de Compose, pipeline de CI/CD, runbooks) — nunca despliega nada por sí mismo.

### 🐛 Plantillas de Issues

`.github/ISSUE_TEMPLATE/feature_request.md` y `bug_report.md` vienen
incluidas en el kit para que lo que se abra en GitHub ya llegue
suficientemente estructurado para alimentar `/sdlc-analysis` directamente
(contexto, actores, comportamiento esperado en features; pasos de
reproducción y comportamiento esperado/actual en bugs). Son plantillas
Markdown estáticas que rellenan personas — ningún agente las lee en
tiempo real.

**Cómo funciona esta funcionalidad de GitHub:** GitHub escanea
`.github/ISSUE_TEMPLATE/` en la rama por defecto del repositorio. Si
encuentra ficheros ahí, al pulsar **New issue** aparece un selector de
plantillas en vez de un issue en blanco. Cada plantilla `.md` necesita una
cabecera YAML — `name`, `about`, `title`, `labels`, `assignees` — seguida
del cuerpo en Markdown; `name` debe tener más de 3 caracteres o GitHub no
la listará. El campo `labels` aplica automáticamente etiquetas que ya
existan en el repo (no crea una etiqueta nueva si no existe). Se puede
añadir un `config.yml` opcional en la misma carpeta para desactivar la
opción de issue en blanco para colaboradores externos
(`blank_issues_enabled: false`) o añadir `contact_links` externos. Existe
también una alternativa más nueva y estructurada — "issue forms" en
`.yml` con campos tipados (dropdowns, checkboxes, subida de ficheros) —
que no hemos usado aquí porque una plantilla Markdown ya encajaba con el
flujo de trabajo real del usuario. Referencia completa: [GitHub Docs —
Configuring issue templates for your
repository](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository).

### 🔁 Cierre de puntos abiertos

`sdlc-analysis` y `sdlc-design` no se limitan a dejar preguntas o riesgos
abiertos dentro del documento y seguir adelante. Una vez escrito el
documento, el comando lee su sección "Dependencies" (análisis — buscando
bullets `Open question:`) o "Risks & Open Decisions" (diseño):

- **¿No hay nada abierto?** Simplemente te indica el siguiente comando,
  como siempre.
- **¿Hay algo abierto?** Reformula cada punto como una pregunta directa,
  te las lista ahí mismo en la conversación y **espera tus respuestas** en
  lugar de dejarlas enterradas en el fichero. En cuanto respondes, vuelve a
  delegar en el mismo agente para actualizar el documento en el sitio
  —resolviendo esos puntos y ajustando cualquier sección afectada— antes de
  indicarte la siguiente fase.

Esto cierra un hueco donde estos documentos salían "terminados" pero
llenos de cabos sueltos que el usuario tenía que detectar y perseguir a
mano.

### 🧠 Skills del ecosistema (.NET 10 / Azure / Blazor)

Skills precargados y orientados a un equipo con stack Microsoft, que cada agente carga automáticamente cuando es relevante:

- **🧑‍💼 Business Analyst** — enfoque Agile de requisitos (INVEST, DoR/DoD).
- **🏗️ Software Architect** — decisiones de arquitectura .NET + Azure, criterio para adoptar CQRS/Mediator, estructura y naming de soluciones .NET.
- **👨‍💻 Software Developer** — convenciones de .NET 10, patrones de EF Core, componentes Blazor, implementación de CQRS/Mediator, Docker para .NET, naming conventions de Microsoft, principios SOLID.
- **🧪 QA Engineer** — testing .NET con xUnit (+ Moq, WebApplicationFactory, Testcontainers), testing de componentes Blazor con bUnit.
- **🚢 DevOps Engineer** — referencia de CI/CD en Azure, además de despliegue self-hosted en servidor propio con Docker, GHCR y Portainer.

### 🚢 Despliegue self-hosted (Docker + Portainer)

Para equipos con un servidor propio en vez de un proveedor cloud,
`sdlc-implementation` sabe montar un flujo de release completo: construir
y subir imágenes a GitHub Container Registry (GHCR) desde `cd.yaml`, y
aplicarlas a un único nodo de Portainer con varios stacks, según el
mecanismo que mejor encaje:

- **Webhook de Portainer** disparado desde el último paso de `cd.yaml`
  (requiere la Business Edition gratuita de Portainer, disponible para
  siempre hasta 3 nodos — la CE por sí sola no lo soporta).
- **Polling de Git** en el lado de Portainer, si prefieres no guardar un
  secreto de webhook.
- **Runner autoalojado de GitHub Actions** en el propio servidor, si
  quieres quedarte en Portainer CE sin depender de GitOps.
- **Pull y redeploy manual** en la UI de Portainer, siempre documentado
  como alternativa de respaldo sea cual sea la automatización elegida.

Nunca se conecta al servidor directamente — solo edita ficheros de
Compose/pipeline y documenta la configuración manual puntual (activar el
webhook en Portainer, añadir el secreto en GitHub) que el usuario realiza
fuera del repositorio.

### 🔒 Invariante — nunca commit, nunca push

Todos los agentes, comandos y skills de este kit tienen la instrucción explícita de **no ejecutar nunca** `git commit`, `git push` ni ninguna acción equivalente, bajo ninguna circunstancia, ni siquiera si se pide durante la sesión. Hacer commit y push es siempre una acción manual y deliberada de **la persona usuaria**, tras revisar lo generado.

### 🧩 Ampliar el kit

- Añade más skills en `.claude/skills/<agente>/` como markdown plano — cada agente ya está instruido para leer los que sean relevantes para su tarea.
- `devops-engineer` / `sdlc-implementation` ahora prepara artefactos de despliegue reales (Azure o Docker/Portainer self-hosted), pero sigue sin ejecutar nunca nada contra un host remoto — amplía sus skills en `.claude/skills/devops-engineer/` para otros destinos (otra nube, Kubernetes...) de la misma forma.

