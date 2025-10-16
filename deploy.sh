#!/bin/bash

# =============================================================================
# Script de Deploy para Brain - Malackathon 2025
# =============================================================================
# Este script despliega la aplicación en modo PRODUCCIÓN con HTTPS
# Para desarrollo local, simplemente ejecuta: docker-compose up
# =============================================================================

set -e  # Exit on error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN="dr-artificial.com"
EMAIL="${1:-davidmunvalle@uma.es}"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║             Production Deploy (Malackathon 2025)          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# =============================================================================
# 1. Pre-deploy checks
# =============================================================================
echo -e "${YELLOW}[1/7] Verificando requisitos...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker instalado${NC}"

# Check docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ docker-compose no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker-compose instalado${NC}"

# Check .env file
if [ ! -f .env ]; then
    echo -e "${RED}✗ Archivo .env no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Archivo .env existe${NC}"

# Check nginx configs
if [ ! -f nginx/nginx-prod.conf ]; then
    echo -e "${RED}✗ nginx/nginx-prod.conf no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Configuración nginx-prod.conf existe${NC}"

echo ""

# =============================================================================
# 2. Verificar DNS
# =============================================================================
echo -e "${YELLOW}[2/7] Verificando DNS...${NC}"

SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

echo "   IP del servidor: $SERVER_IP"
echo "   IP de $DOMAIN: $DOMAIN_IP"

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    echo -e "${RED}✗ El DNS no apunta a este servidor${NC}"
    echo -e "${YELLOW}  Configurar DNS: $DOMAIN → $SERVER_IP${NC}"
    read -p "¿Continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ DNS configurado correctamente${NC}"
fi

echo ""

# =============================================================================
# 3. Configurar firewall (Oracle Cloud + UFW)
# =============================================================================
echo -e "${YELLOW}[3/7] Configurando firewall...${NC}"

# UFW (si está instalado)
if command -v ufw &> /dev/null; then
    echo "   Configurando UFW..."
    sudo ufw allow 80/tcp >/dev/null 2>&1 || true
    sudo ufw allow 443/tcp >/dev/null 2>&1 || true
    echo -e "${GREEN}✓ UFW configurado (puertos 80, 443)${NC}"
fi

# Recordatorio para Oracle Cloud
echo -e "${YELLOW}⚠  IMPORTANTE: Verificar Oracle Cloud Security List${NC}"
echo "   1. Oracle Cloud Console → Networking → VCN"
echo "   2. Security Lists → Default Security List"
echo "   3. Ingress Rules: 0.0.0.0/0, TCP, Ports 80 y 443"
echo ""
read -p "¿Has configurado Oracle Cloud Security List? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Configúralo antes de continuar${NC}"
    exit 1
fi

echo ""

# =============================================================================
# 4. Obtener certificado SSL
# =============================================================================
echo -e "${YELLOW}[4/7] Verificando certificado SSL...${NC}"

if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${GREEN}✓ Certificado SSL ya existe${NC}"
    
    # Verificar expiración
    EXPIRY=$(sudo openssl x509 -enddate -noout -in "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" | cut -d= -f2)
    echo "   Expira: $EXPIRY"
else
    echo -e "${YELLOW}Obteniendo certificado SSL...${NC}"
    
    # Crear directorio certbot
    sudo mkdir -p /var/www/certbot
    sudo chmod -R 755 /var/www/certbot
    
    # Iniciar servicios temporalmente para ACME challenge
    echo "   Iniciando servicios para validación ACME..."
    docker-compose up -d
    sleep 10
    
    # Obtener certificado
    sudo certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --non-interactive
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Certificado SSL obtenido exitosamente${NC}"
    else
        echo -e "${RED}✗ Error al obtener certificado SSL${NC}"
        echo "   Revisar logs: sudo certbot --logs"
        exit 1
    fi
fi

echo ""

# =============================================================================
# 5. Configurar renovación automática SSL
# =============================================================================
echo -e "${YELLOW}[5/7] Configurando renovación automática SSL...${NC}"

# Crear cron job para renovación
CRON_JOB="0 3 * * * certbot renew --quiet --deploy-hook 'docker-compose -f $(pwd)/docker-compose.prod.yml restart nginx'"

if ! (sudo crontab -l 2>/dev/null | grep -q "certbot renew"); then
    (sudo crontab -l 2>/dev/null; echo "$CRON_JOB") | sudo crontab -
    echo -e "${GREEN}✓ Renovación automática configurada (3 AM diario)${NC}"
else
    echo -e "${GREEN}✓ Renovación automática ya configurada${NC}"
fi

echo ""

# =============================================================================
# 6. Configurar nginx para producción
# =============================================================================
echo -e "${YELLOW}[6/7] Verificando configuración de producción...${NC}"

# Verificar que docker-compose.prod.yml existe
if [ ! -f docker-compose.prod.yml ]; then
    echo -e "${RED}✗ docker-compose.prod.yml no encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Configuración de producción lista (docker-compose.prod.yml)${NC}"

echo ""

# =============================================================================
# 7. Deploy de servicios
# =============================================================================
echo -e "${YELLOW}[7/7] Desplegando servicios...${NC}"

# Detener servicios existentes
echo "   Deteniendo servicios existentes..."
docker-compose -f docker-compose.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Rebuild y deploy con docker-compose.prod.yml
echo "   Construyendo imágenes..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "   Iniciando servicios..."
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que los servicios estén listos
echo "   Esperando a que los servicios estén listos..."
sleep 15

# Health check
echo ""
echo -e "${YELLOW}Verificando servicios...${NC}"

if docker ps | grep -q malackathon-backend; then
    echo -e "${GREEN}✓ Backend ejecutándose${NC}"
else
    echo -e "${RED}✗ Backend no está ejecutándose${NC}"
fi

if docker ps | grep -q malackathon-frontend; then
    echo -e "${GREEN}✓ Frontend ejecutándose${NC}"
else
    echo -e "${RED}✗ Frontend no está ejecutándose${NC}"
fi

if docker ps | grep -q malackathon-nginx; then
    echo -e "${GREEN}✓ Nginx ejecutándose${NC}"
else
    echo -e "${RED}✗ Nginx no está ejecutándose${NC}"
fi

# Test HTTPS
echo ""
echo -e "${YELLOW}Verificando HTTPS...${NC}"
if curl -s -f -k https://$DOMAIN/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HTTPS funcionando correctamente${NC}"
else
    echo -e "${RED}✗ HTTPS no responde${NC}"
    echo "   Revisar logs: docker-compose logs nginx"
fi

# =============================================================================
# Deploy complete
# =============================================================================
echo ""
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                  ✓ DEPLOY COMPLETADO                      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}La aplicación está disponible en:${NC}"
echo "   🌐 https://$DOMAIN"
echo "   🔗 https://$DOMAIN/api/insights"
echo "   💚 https://$DOMAIN/health"
echo ""
echo -e "${YELLOW}Comandos útiles (PRODUCCIÓN):${NC}"
echo "   Ver logs:       docker-compose -f docker-compose.prod.yml logs -f"
echo "   Ver logs nginx: docker-compose -f docker-compose.prod.yml logs -f nginx"
echo "   Reiniciar:      docker-compose -f docker-compose.prod.yml restart"
echo "   Detener:        docker-compose -f docker-compose.prod.yml down"
echo ""
echo -e "${YELLOW}Certificado SSL:${NC}"
echo "   Renovación automática: Diaria a las 3 AM"
echo "   Verificar estado: sudo certbot certificates"
echo "   Renovar manualmente: sudo certbot renew"
echo ""
