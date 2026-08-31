---
name: terraform-expert
description: Generate, review, refactor, test, and troubleshoot Terraform using official HashiCorp workflows. Use when writing HCL, designing reusable modules, creating `.tftest.hcl` tests, managing backends and state, or importing existing resources.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.2.1"
  domain: infrastructure
  triggers: Terraform, infrastructure as code, IaC, terraform module, terraform refactor, terraform test, .tftest.hcl, terraform import, terraform query, terraform state, terraform plan, terraform validate
  role: specialist
  scope: implementation
  output-format: code
  upstream-reference: https://github.com/hashicorp/agent-skills/tree/main/terraform
---

# Terraform Expert

Use this skill as a single entry point for the official HashiCorp Terraform skill set. Pick the matching workflow first, then load only the local references needed for that task.

**Version gates.** Before recommending a feature, check the project's `required_version`: `moved` blocks need Terraform >= 1.1, `import` blocks >= 1.5, `terraform test` / `.tftest.hcl` >= 1.6, and Terraform Search (`terraform query`, list resources) >= 1.14. On older pins, either raise the pin deliberately or use the legacy equivalent (`terraform state mv`, `terraform import` CLI).

**OpenTofu.** If the project uses OpenTofu (`tofu` CLI, `opentofu` in lockfiles/CI), the guidance here mostly transfers — style, modules, state discipline — but verify feature availability against OpenTofu's own docs (it diverges from Terraform post-1.5: e.g. state encryption exists in OpenTofu only, and test/query features track different versions). Don't assume version gates map one-to-one.

## Upstream HashiCorp Basis

This skill is aligned to the core Terraform skills in `hashicorp/agent-skills`:

- `terraform-style-guide` -> `references/style-guide.md`
- `terraform-test` -> `references/testing.md`
- `refactor-module` -> `references/module-patterns.md`, `references/module-library.md`
- `terraform-search-import` -> `references/search-import.md`

Deliberately excluded:

- platform-specific paid-tier workflows

## Choose The Workflow

- Standard `.tf` authoring or review: load `references/style-guide.md`, `references/providers.md`, and `references/best-practices.md`.
- Reusable module design or refactoring: load `references/module-patterns.md`, `references/module-library.md`, and `references/testing.md`.
- State, backend, workspace, or migration work: load `references/state-management.md`.
- Importing unmanaged infrastructure: load `references/search-import.md` first, then `references/style-guide.md`.
- Built-in Terraform tests: load `references/testing.md`; prefer `terraform test` and `.tftest.hcl` before reaching for Terratest.

## Default Workflow

1. Classify the task as standard HCL, module work, testing, import, or state migration.
2. Read the matching references before editing files.
3. Design the smallest correct change that matches HashiCorp conventions.
4. Keep root modules thin and move reusable logic into well-scoped modules.
5. Prefer Terraform-native workflows such as `moved` blocks, `import` blocks, and `.tftest.hcl` tests over ad hoc shell-based fixes.
6. Validate, fix errors, and re-run validation until clean before handing off.

## Must Do

- Pin Terraform and provider versions explicitly.
- Add `description` and `type` to every variable and output.
- Validate inputs with typed variables and validation blocks where supported.
- Use remote state with locking and encryption for shared or production environments.
- Prefer `for_each` for collections and `count` only for optional singletons or simple conditional resources.
- Document reusable modules and include `examples/` plus focused tests.
- Keep naming consistent with HashiCorp style guidance.
- Commit `.terraform.lock.hcl` when provider dependencies change.

## Must Not Do

- Hardcode secrets, credentials, or environment-specific sensitive values.
- Commit `.terraform/`, state files, plan files, or secret-bearing `.tfvars` files.
- Use local state for shared or production infrastructure.
- Reach for direct `terraform state` surgery before considering `moved` or `import` blocks.
- Break a module interface without updating documentation and versioning accordingly.
- Add platform-specific paid-tier workflows unless the skill is explicitly meant to cover them.

## Workflow-Specific Rules

- For module refactors, preserve state compatibility whenever possible and prefer `moved` blocks (>= 1.1) over destructive recreation.
- For imports, prefer `import` blocks (>= 1.5); use Terraform Search and generated import configuration when Terraform `>= 1.14` and the provider supports list resources.
- For testing, default to built-in `terraform test` (>= 1.6); use Terratest only when you need runtime behavior, external system checks, or richer orchestration.

## Validation Order

Run the narrowest useful validation loop for the task:

1. `terraform fmt -recursive`
2. `terraform validate`
3. `terraform test` for reusable modules or when `.tftest.hcl` is present
4. `terraform plan`

Use these task-specific commands when relevant:

- Import workflow: `terraform query`, then `terraform query -generate-config-out=...`

## Output Format

When producing Terraform changes, provide:

- the requested HCL files or module structure
- example module usage when reusable modules are involved
- the validation commands that should be run
- any assumptions, migration steps, or manual approval/apply steps that remain
