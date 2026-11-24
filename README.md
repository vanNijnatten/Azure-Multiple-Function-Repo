# Azure Multiple Function Repo

[![CI](https://github.com/vanNijnatten/Azure-Multiple-Function-Repo/actions/workflows/ci.yaml/badge.svg)](https://github.com/vanNijnatten/Azure-Multiple-Function-Repo/actions/workflows/ci.yaml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A template repository for **several Azure Function Apps in one repo**, written in Python
(v2 programming model), managed with [uv](https://docs.astral.sh/uv/), and set up for VSCode.

- One **uv workspace**: one `uv.lock`, one `.venv`, every app and shared package installed editable.
- Each Function App is its own package under `apps/`, deployed as its own zip.
- Shared code lives in `packages/` and is vendored into each app's deployment package.
- Type hints and go-to-definition work across apps and packages in VSCode (Pylance),
  and the CLI type checker (pyright) uses the **same** configuration.
- Tests for every app run in one pytest session and in the VSCode Test Explorer.
- pre-commit hooks and GitHub Actions for lint, type check, tests, packaging and per-app deploys.


## Layout

```text
.
├── apps/                          # one folder per Function App
│   ├── api-app/                   # HTTP triggers
│   │   ├── function_app.py        # thin entry point the Functions host indexes
│   │   ├── host.json
│   │   ├── local.settings.example.json
│   │   ├── pyproject.toml         # the app's own dependencies
│   │   ├── src/api_app/           # the functions (blueprints) and app code
│   │   └── tests/
│   └── worker-app/                # timer + queue triggers, same shape
├── packages/
│   └── common/                    # shared library used by both apps
│       ├── src/common/
│       └── tests/
├── scripts/
│   ├── package_app.py             # build dist/<app>.zip for deployment
│   └── init_local_settings.py     # create local.settings.json from the examples
├── .github/workflows/
│   ├── ci.yaml                    # pre-commit, pyright, pytest, package every app
│   └── deploy.yaml                # deploy the apps that changed
├── .vscode/                       # settings, tasks, launch configs, extensions
├── .devcontainer/                 # Dev Container / Codespaces
├── .pre-commit-config.yaml
├── pyproject.toml                 # workspace root + tool config (ruff, pyright, pytest)
└── uv.lock
```

Why the functions live in `src/<package>/` and not in `function_app.py`: the package is
importable, type checked and testable like normal code, and the same layout works for
every app. `function_app.py` only creates the `FunctionApp` and registers the blueprints.


## Getting started

Prerequisites: [uv](https://docs.astral.sh/uv/getting-started/installation/),
[Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local),
and for queue/timer triggers the [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite)
storage emulator (the VSCode extension, or `npx azurite`). Or open the repo in the Dev Container,
which installs all of it.

```bash
uv sync                                  # create .venv with every app, package and dev tool
uv run scripts/init_local_settings.py    # apps/*/local.settings.json (git-ignored)
uv run pre-commit install                # run the hooks on every commit
```

Everyday commands:

| What                        | Command                                         |
| --------------------------- | ----------------------------------------------- |
| Run all tests               | `uv run pytest`                                 |
| Tests with coverage         | `uv run pytest --cov`                           |
| Lint and format             | `uv run ruff check --fix . && uv run ruff format .` |
| Type check                  | `uv run pyright`                                |
| All pre-commit hooks        | `uv run pre-commit run --all-files`             |
| Run one app locally         | `cd apps/api-app && uv run func host start`     |
| Build a deployment zip      | `uv run scripts/package_app.py api-app` (or `--all`) |
| Add a dependency to one app | `uv add --package api-app httpx`                |


## VSCode

Open the repository root as the workspace and install the recommended extensions when prompted.

- **Interpreter**: the Python extension picks up `./.venv`. If it doesn't, run
  *Python: Select Interpreter* and choose it.
- **Type hints and navigation**: Pylance reads `[tool.pyright]` in `pyproject.toml`
  (strict mode, with every `src/` folder in `extraPaths`), so imports such as
  `from common import build_greeting` resolve to the source in `packages/common`, and the
  editor shows exactly the errors that pre-commit and CI report.
- **Tests**: the Testing view lists the tests of every app and package.
- **Debugging a Function App**: pick *Debug api-app*, *Debug worker-app* or
  *Debug all Function Apps* in Run and Debug, and press F5. This runs `uv sync`, creates
  missing `local.settings.json` files, starts Core Tools for that app with the workspace
  `.venv`, and attaches the debugger. The apps listen on ports 7071 (`api-app`) and
  7072 (`worker-app`); the debugger on 9091 and 9092.
  Start Azurite first for `worker-app` (*Azurite: Start* from the Command Palette, or the
  `azurite: start` task).


## Adding a Function App

1. Copy `apps/api-app` to `apps/<new-app>` and rename `src/api_app` to `src/<new_app>`.
2. Update `name` in its `pyproject.toml`, and the import in `function_app.py`.
3. In the root `pyproject.toml`, add the app to `dependencies`, `[tool.uv.sources]`,
   `[tool.pyright] extraPaths` and `[tool.ruff.lint.isort] known-first-party`.
4. Pick a free `LocalHttpPort` in its `local.settings.example.json`, and add a
   `func: start` task and a launch config in `.vscode/` with a free debug port.
5. Run `uv sync`.

CI and the deploy workflow discover apps automatically (every `apps/*/function_app.py`).
A shared library is added the same way under `packages/`.


## Deployment

`scripts/package_app.py <app>` exports the app's locked runtime dependencies from
`uv.lock` (including workspace packages such as `common`), installs them for Linux into
`.python_packages/lib/site-packages`, adds `function_app.py` and `host.json`, checks that
the host can index the functions, and writes `dist/<app>.zip`. That zip is deployed as-is,
with remote build turned off.

The **Deploy** workflow runs on pushes to `main` and deploys only the apps whose folder
changed, or every app when `packages/`, `pyproject.toml`, `.python-version` or `uv.lock`
changed. It can also be run by hand for chosen apps. One-time setup per app:

1. Create the Function App in Azure (Linux, Python 3.14).
2. Create a [GitHub Environment](https://docs.github.com/actions/deployment/targeting-different-environments)
   named after the app folder (e.g. `api-app`) with these variables:
   `AZURE_FUNCTIONAPP_NAME`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.
3. Give that Entra ID app registration (or managed identity) a federated credential for
   `repo:vanNijnatten/Azure-Multiple-Function-Repo:environment:<app>` and a role that may
   deploy to the Function App (e.g. *Website Contributor*).

For a Flex Consumption plan, add `sku: flexconsumption` and `remote-build: false` to the
deploy step.


# Code of Conduct

- Please read the [Code of Conduct](./docs/CODE_OF_CONDUCT.md) for guidance on how to interact with others in a way that makes a community thrive.
- Please also read how to [Contribute](./docs/CONTRIBUTING.md), if you would like to contribute.
