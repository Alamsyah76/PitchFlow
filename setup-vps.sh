#!/bin/bash
# PitchFlow VPS Setup — jalankan di VPS sebagai root
set -e

echo "PitchFlow — VPS Setup"
echo "======================"

# 1. Update system
apt-get update && apt-get upgrade -y

# 2. Install Docker + Docker Compose
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose-plugin

# 3. Install Certbot untuk SSL
apt-get install -y certbot

# 4. Clone repo
cd /opt
git clone https://github.com/Alamsyah76/PitchFlow.git
cd PitchFlow

# 5. Minta input OpenAI API Key
read -p "Masukkan OPENAI_API_KEY: " openai_key
export OPENAI_API_KEY=$openai_key

# 6. Setup SSL Certificate
echo ""
echo "Setup SSL untuk pitchflow.digital..."
echo "Pastikan DNS sudah pointing ke IP VPS ini!"
read -p "Press Enter setelah DNS pointing..."

certbot certonly --standalone -d pitchflow.digital -d www.pitchflow.digital -d api.pitchflow.digital

# 7. Jalankan semua service
docker compose up -d

# 8. Setup auto-renew SSL
crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && docker compose restart nginx" | crontab -

echo ""
echo "✅ SELESAI! Akses:"
echo "   https://pitchflow.digital"
echo "   https://api.pitchflow.digital"
echo ""
echo "Untuk update: cd /opt/PitchFlow && git pull && docker compose up -d --build"
