#!/bin/bash
#===============================================================================
# NAT INSTANCE USER DATA SCRIPT
# Enables IP forwarding and configures iptables for NAT functionality
#===============================================================================

set -e

exec > >(tee /var/log/nat-user-data.log) 2>&1
echo "Starting NAT instance configuration at $(date)"

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p

# Get primary interface
INTERFACE=$(ip route show default | awk '/default/ {print $5}' | head -n1)
echo "Primary interface: ${INTERFACE}"

# Configure iptables MASQUERADE
iptables -t nat -F POSTROUTING
iptables -t nat -A POSTROUTING -o ${INTERFACE} -j MASQUERADE
iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -s 10.0.0.0/16 -j ACCEPT

# Persist iptables
yum install -y iptables-services 2>/dev/null || true
systemctl enable iptables 2>/dev/null || true
service iptables save 2>/dev/null || true

echo "NAT configuration completed at $(date)"
