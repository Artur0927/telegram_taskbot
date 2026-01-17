#!/bin/bash
# Production deployment script for Telegram Mini App

set -e

echo "🚀 Starting Mini App Production Deployment..."

# Configuration
BUCKET_NAME="telegram-bot-miniapp-prod"
REGION="us-east-1"
STACK_NAME="miniapp-prod"

# Step 1: Build Frontend
echo "📦 Building frontend..."
cd miniapp
npm run build
cd ..

echo "✅ Frontend built successfully"

# Step 2: Create S3 Bucket
echo "🪣 Creating S3 bucket..."
aws s3 mb s3://${BUCKET_NAME} --region ${REGION} 2>/dev/null || echo "Bucket already exists"

# Configure bucket
aws s3api put-bucket-versioning \
  --bucket ${BUCKET_NAME} \
  --versioning-configuration Status=Enabled

# Block public access (Disabled to allow public read policy for static site)
# aws s3api put-public-access-block \
#   --bucket ${BUCKET_NAME} \
#   --public-access-block-configuration \
#     "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "✅ S3 bucket configured"

# Step 3: Upload to S3
echo "📤 Uploading files to S3..."
aws s3 sync miniapp/dist/ s3://${BUCKET_NAME}/ \
  --delete \
  --cache-control "max-age=31536000,public" \
  --exclude "index.html"

# Upload index.html with no-cache
aws s3 cp miniapp/dist/index.html s3://${BUCKET_NAME}/index.html \
  --cache-control "no-cache" \
  --content-type "text/html"

echo "✅ Files uploaded to S3"

echo "🎉 Deployment complete!"
echo "Next steps:"
echo "1. Create CloudFront distribution"
echo "2. Deploy API Lambda"
echo "3. Configure API Gateway"
echo "4. Add WAF rules"
