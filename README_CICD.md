# 🚀 Production CI/CD Pipeline

This repository includes a robust, security-focused CI/CD pipeline using **GitHub Actions** and **AWS SAM**.

## 🏗️ Architecture

### 1. Continuous Integration (CI) - `ci.yml`
Runs on every Pull Request to the `main` branch.
- **Goal:** Prevent broken code from merging.
- **Stages:**
  - **Lint:** Checks code style using `ruff` (fails on errors).
  - **Test:** Runs unit tests using `pytest` with 100% isolation.
  - **Validate:** Checks `template.yaml` validity using `sam validate`.

### 2. Continuous Deployment (CD) - `cd.yml`
Runs on every push to `main`.
- **Goal:** Safe, idempotent production deployments.
- **Stages:**
  - **Build:** Compiles Lambda functions in a containerized environment.
  - **Deploy:** Updates the CloudFormation stack via `sam deploy`.
- **Gatekeeper:** Requires manual approval in the **GitHub Environment** (`production`) before executing.

## 🛠️ Setup Instructions

### 1. Configure GitHub Environments
1. Go to **Settings > Environments**.
2. Create a new environment named `production`.
3. Enable **Required reviewers** and add your team leads.

### 2. Configure Secrets
Add the following credentials in **Settings > Secrets and variables > Actions**:

| Secret Name | Description |
|---|---|

| `AWS_DEPLOY_ROLE_ARN` | The IAM Role ARN for OIDC deployment: `arn:aws:iam::577713924485:role/GitHubDeployRole-TelegramBot` |

*(Note: The `BOT_TOKEN_SECRET` and `GEMINI_API_KEY` are retrieved by Lambda at runtime from AWS Secrets Manager, not GitHub Secrets).*

## 🛡️ Security Features
- **Deterministic Builds:** Uses specific Python versions.
- **Idempotency:** `sam deploy` only applies changes if drift is detected.
- **Least Privilege:** Lambda functions use IAM Roles to access DynamoDB/Secrets, not hardcoded keys.
- **Fail Fast:** Pipeline stops immediately if linting or tests fail.
