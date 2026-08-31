# Terraform Search And Import

Use when bringing unmanaged infrastructure under Terraform control. Prefer this workflow when Terraform is `>= 1.14` and the provider supports list resources.

This reference is based on HashiCorp's official `terraform-search-import` skill.

## Decision Rules

1. Confirm the Terraform version is `>= 1.14`.
2. Confirm the provider supports list resources for the target type.
3. If both are true, use Terraform Search and generated import configuration.
4. Otherwise, fall back to manual discovery plus `import` blocks.

## Check Provider Support

Run this from a directory with initialized provider configuration:

```bash
terraform providers schema -json | jq '.provider_schemas | to_entries | map({provider: (.key | split("/")[-1]), list_resources: (.value.list_resource_schemas // {} | keys)})'
```

If the target resource type is not present in `list_resources`, do not use Terraform Search for that resource.

## Search Workflow

1. Create or verify provider configuration.
2. Run `terraform init`.
3. Write a `.tfquery.hcl` file with one or more `list` blocks.
4. Run `terraform query` to inspect results.
5. Run `terraform query -generate-config-out=generated.tf`.
6. Clean the generated configuration before planning or applying.
7. Run `terraform plan` and review the import carefully.

## Minimal Query Example

```hcl
terraform {
  required_version = ">= 1.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

list "aws_instance" "team_instances" {
  provider = aws

  config {
    filter {
      name   = "tag:Owner"
      values = ["platform"]
    }
  }

  limit = 50
}
```

## Commands

```bash
terraform init
terraform query
terraform query -generate-config-out=generated.tf
terraform plan
```

## Generated Config Cleanup

Never apply generated configuration blindly. Clean it up first:

- remove computed or read-only attributes
- replace hardcoded values with variables or locals
- rename resources to meaningful Terraform names
- move final code into normal files such as `main.tf`, `variables.tf`, and `outputs.tf`
- keep generated `import` blocks when they express the import clearly

## Import Guidance

- Prefer identity-based `import` blocks when Terraform supports them.
- Start with a narrow query and a `limit` before widening the search.
- Review whether imported resources belong in the current root module or a reusable child module.
- After import, refactor incrementally and use `moved` blocks if resource addresses change.

## When To Fall Back

Use a manual import workflow when:

- Terraform is older than `1.14`
- the provider lacks list resource support
- the generated configuration is incomplete or unusable
- the environment needs custom discovery logic outside Terraform Search

## Common Mistakes

- Assuming every provider resource supports list queries.
- Importing large sets of resources without first testing a small sample.
- Keeping generated names like `all_0` instead of refactoring them into stable addresses.
- Applying generated code without checking for computed fields or deprecated arguments.
