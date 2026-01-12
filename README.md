# Telegram Bot on AWS ECS 🚀

![Status](https://img.shields.io/badge/Status-Live-green)
![CI/CD](https://gitlab.com/Artur0927/telegram-bot-aws/badges/main/pipeline.svg)

**Bot Username:** [@assistentv01Bot](https://t.me/assistentv01Bot)  
**Webhook URL:** `https://dyqkwcu5hg4ug.cloudfront.net/webhook`  

A production-ready Telegram Bot platform deployed on AWS ECS (EC2 Launch Type) using Terraform and GitLab CI/CD.

## 🏗 Architecture

- **AWS ECS:** Orchestrates the Dockerized bot application on EC2 instances (`t3.micro`).
- **AWS CloudFront:** Provides a free managed HTTPS endpoint for the Telegram Webhook.
- **AWS ALB:** Internal load balancing.
- **AWS ECR:** Stores Docker images.
- **Terraform:** Infrastructure as Code (IaC) for reproducible deployments.
- **GitLab CI:** Automated pipeline for Testing, Building, and Deploying.

## 🚀 Features

- **Zero-Trust Security:** OIDC Authentication (No long-lived AWS keys).
- **Zero Cost (Free Tier):** Designed to fit within AWS Free Tier limits.
- **HTTPS Webhook:** Secure communication with Telegram API.
- **AI Powered:** Integrates with Google Gemini API.

## 🛠 Commands

**Local Development:**
```bash
pip install -r app/requirements.txt
python app/main.py
```

**Terraform:**
```bash
cd terraform
terraform apply
```

**View Logs:**
```bash
aws logs tail /ecs/telegram-bot --follow
```
