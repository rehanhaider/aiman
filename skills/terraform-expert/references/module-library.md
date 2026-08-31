# Terraform Module Library

## Purpose

Create and maintain a shared Terraform module library with consistent structure, documentation, versioning, and tests.

Use this when you are designing an org-wide `modules/` repository, standardizing provisioning patterns, or publishing reusable IaC components.

## Recommended Repository Layout

Choose one of these and keep it consistent:

### Option A: Monorepo by provider

```
modules/
├── aws/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   └── s3/
├── azure/
│   ├── vnet/
│   ├── aks/
│   └── storage/
├── gcp/
│   ├── vpc/
│   ├── gke/
│   └── cloud-sql/
└── oci/
    ├── vcn/
    ├── oke/
    └── object-storage/
```

### Option B: Single-cloud repo

```
modules/
├── networking/
├── compute/
├── databases/
└── security/
```

## Standard Module Contract

Every module should follow the same internal shape.
For code examples, see `references/module-patterns.md`.

```
<module>/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── README.md
├── examples/
│   └── complete/
│       ├── main.tf
│       └── variables.tf
└── tests/
```

### Documentation Requirements

- Document all inputs/outputs with clear descriptions (and sensible defaults where safe).
- Provide at least one complete example.
- Keep a short “upgrade notes” section for breaking changes.

## Versioning and Releases

- Use semantic versioning (MAJOR.MINOR.PATCH).
- Treat any input removal/rename, output changes, or behavior changes as a breaking change → bump MAJOR.
- Prefer immutable references in consumers:
  - Registry modules: pin `version`
  - Git modules: pin tags (`?ref=vX.Y.Z`) rather than branches

## Testing and Quality Gates

Minimum module gates:

- `terraform fmt -check`
- `terraform validate`
- `tflint` (rulesets as appropriate)

For module tests:

- Prefer `terraform test` (Terraform 1.6+) for fast unit/integration checks.
- Use Terratest for higher-confidence integration tests when module behavior depends on real cloud APIs.

See `references/testing.md` for concrete examples and CI patterns.

