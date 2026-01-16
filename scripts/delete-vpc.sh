#!/bin/bash
# Script to delete VPC and all associated resources

VPC_ID=$1

if [ -z "$VPC_ID" ]; then
    echo "Usage: $0 <VPC_ID>"
    exit 1
fi

echo "Deleting VPC: $VPC_ID"

# Delete NAT Gateways
echo "Deleting NAT Gateways..."
NAT_GATEWAYS=$(aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$VPC_ID" --query 'NatGateways[*].NatGatewayId' --output text --region us-east-1)
for NAT in $NAT_GATEWAYS; do
    echo "  Deleting NAT Gateway: $NAT"
    aws ec2 delete-nat-gateway --nat-gateway-id $NAT --region us-east-1
done

# Wait for NAT gateways to delete
if [ ! -z "$NAT_GATEWAYS" ]; then
    echo "Waiting for NAT Gateways to delete (60s)..."
    sleep 60
fi

# Delete Elastic IPs associated with NAT Gateways
echo "Releasing Elastic IPs..."
EIPS=$(aws ec2 describe-addresses --filters "Name=domain,Values=vpc" --query 'Addresses[*].AllocationId' --output text --region us-east-1)
for EIP in $EIPS; do
    echo "  Releasing EIP: $EIP"
    aws ec2 release-address --allocation-id $EIP --region us-east-1 2>/dev/null || true
done

# Delete subnets
echo "Deleting Subnets..."
SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text --region us-east-1)
for SUBNET in $SUBNETS; do
    echo "  Deleting Subnet: $SUBNET"
    aws ec2 delete-subnet --subnet-id $SUBNET --region us-east-1
done

# Delete route table associations and route tables
echo "Deleting Route Tables..."
ROUTE_TABLES=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" --query 'RouteTables[?Associations[0].Main != `true`].RouteTableId' --output text --region us-east-1)
for RT in $ROUTE_TABLES; do
    echo "  Deleting Route Table: $RT"
    aws ec2 delete-route-table --route-table-id $RT --region us-east-1
done

# Delete Internet Gateways
echo "Deleting Internet Gateways..."
IGWS=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VPC_ID" --query 'InternetGateways[*].InternetGatewayId' --output text --region us-east-1)
for IGW in $IGWS; do
    echo "  Detaching IGW: $IGW"
    aws ec2 detach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC_ID --region us-east-1
    echo "  Deleting IGW: $IGW"
    aws ec2 delete-internet-gateway --internet-gateway-id $IGW --region us-east-1
done

# Delete Security Groups (except default)
echo "Deleting Security Groups..."
SGS=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" --query 'SecurityGroups[?GroupName != `default`].GroupId' --output text --region us-east-1)
for SG in $SGS; do
    echo "  Deleting Security Group: $SG"
    aws ec2 delete-security-group --group-id $SG --region us-east-1 2>/dev/null || true
done

# Delete VPC
echo "Deleting VPC: $VPC_ID"
aws ec2 delete-vpc --vpc-id $VPC_ID --region us-east-1

echo "✅ VPC $VPC_ID deleted successfully!"
