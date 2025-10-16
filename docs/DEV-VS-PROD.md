# Brain - Desarrollo vs Producción

## 🎯 Estrategia: Archivos Separados

Para evitar conflictos con git, usamos **archivos de configuración separados**:

| Archivo | Entorno | Git Tracked | Descripción |
|---------|---------|-------------|-------------|
| `docker-compose.yml` | Desarrollo | ✅ Sí | HTTP, localhost |
| `docker-compose.prod.yml` | Producción | ✅ Sí | HTTPS, dr-artificial.com |
| `nginx/nginx-dev.conf` | Desarrollo | ✅ Sí | Solo HTTP |
| `nginx/nginx-prod.conf` | Producción | ✅ Sí | HTTPS + SSL |

**Ventaja**: `git pull` nunca causa conflictos porque cada entorno usa su propio archivo.

---

## 🔧 Desarrollo Local

Para trabajar en desarrollo local:

```bash
# 1. Iniciar servicios (usa docker-compose.yml por defecto)
docker-compose up

# 2. Acceder a la aplicación
# Frontend: http://localhost
# API: http://localhost/api/insights
# Health: http://localhost/health

# 3. Detener servicios
docker-compose down
```

**Configuración de desarrollo:**
- Archivo: `docker-compose.yml`
- Nginx: `nginx-dev.conf` (HTTP únicamente, puerto 80)
- Sin certificados SSL
- CORS permisivo (`*`)
- Hot reload habilitado

---

## 🚀 Producción (dr-artificial.com)

Para deploy en servidor de producción:

```bash
# 1. Ejecutar script de deploy
chmod +x deploy-prod.sh
./deploy-prod.sh davidmunvalle@uma.es

# El script usa docker-compose.prod.yml automáticamente
```

**Configuración de producción:**
- Archivo: `docker-compose.prod.yml`
- Nginx: `nginx-prod.conf` (HTTPS + HTTP redirect)
- Certificados SSL de Let's Encrypt
- CORS restrictivo (solo dr-artificial.com)
- Security headers (HSTS, X-Frame-Options, etc.)
- Renovación SSL automática

### Comandos para gestión en producción:

```bash
# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Ver logs de nginx específicamente
docker-compose -f docker-compose.prod.yml logs -f nginx

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

# Detener servicios
docker-compose -f docker-compose.prod.yml down

# Reconstruir y desplegar
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📋 Diferencias entre docker-compose.yml vs .prod.yml

| Configuración | Desarrollo | Producción |
|---------------|------------|------------|
| Nginx config | `nginx-dev.conf` | `nginx-prod.conf` |
| Puertos | 80 | 80, 443 |
| SSL | ❌ No | ✅ Sí |
| Certbot | ❌ No | ✅ Sí (auto-renovación) |
| APP_ENV | development | production |
| CORS | `*` (todos) | Solo dominio |
| Hot reload | ✅ Sí | ❌ No |

---

## 🔄 Git Pull Sin Conflictos

Cuando hagas `git pull` en producción:

```bash
# 1. Los servicios siguen corriendo con docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml ps

# 2. Haces pull (sin conflictos porque no modifica archivos locales)
git pull

# 3. Si hay cambios, reconstruyes
docker-compose -f docker-compose.prod.yml up -d --build

# ✅ Sin conflictos porque cada entorno usa archivos diferentes
```

---

## ⚠️ Requisitos para Producción

Antes de ejecutar `deploy-prod.sh`:

### 1. DNS configurado
```bash
# Verificar que el dominio apunta al servidor
dig +short dr-artificial.com
# Debe devolver: 158.179.212.221
```

### 2. Firewall Oracle Cloud
```
Oracle Cloud Console → Networking → VCN
→ Security Lists → Default Security List
→ Add Ingress Rules:
   - Source: 0.0.0.0/0, Protocol: TCP, Port: 80
   - Source: 0.0.0.0/0, Protocol: TCP, Port: 443
```

### 3. Variables de entorno
```bash
# Archivo .env debe existir con:
ORACLE_DSN=...
ORACLE_USER=...
ORACLE_PASSWORD=...
```

---

## 🔐 Gestión de Certificados SSL

```bash
# Ver estado de certificados
sudo certbot certificates

# Renovar manualmente
sudo certbot renew

# Renovación automática (cron job diario a las 3 AM)
sudo crontab -l | grep certbot

# Tras renovar, reiniciar nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 📊 Monitoreo

```bash
# Desarrollo
docker-compose logs -f
docker-compose ps

# Producción
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml ps
```

---

## 🛠️ Troubleshooting

### HTTPS no funciona
```bash
# 1. Verificar certificados
sudo ls -la /etc/letsencrypt/live/dr-artificial.com/

# 2. Ver logs de nginx
docker-compose -f docker-compose.prod.yml logs nginx

# 3. Verificar puerto 443
ss -tulpn | grep 443

# 4. Verificar Security List en Oracle Cloud
```

### Error de permisos en /var/www/certbot
```bash
sudo chown -R $(whoami):$(whoami) /var/www/certbot
sudo chmod -R 755 /var/www/certbot
```

### Backend no conecta a base de datos
```bash
# Verificar oracle_wallet
ls -la app/oracle_wallet/

# Verificar variables .env
cat .env | grep ORACLE

# Ver logs del backend
docker-compose -f docker-compose.prod.yml logs backend
```

### Conflictos con git después de deploy
```bash
# ✅ NO DEBERÍA PASAR porque deploy-prod.sh NO modifica archivos trackeados

# Si modificaste algo manualmente, descarta cambios locales:
git checkout -- docker-compose.yml
git checkout -- nginx/nginx.conf

# Luego haz pull:
git pull
```

---

## 💡 Workflow Recomendado

### En desarrollo (tu máquina local):
```bash
# Trabajo normal
docker-compose up
# ... hacer cambios ...
git add .
git commit -m "Feature X"
git push
docker-compose down
```

### En producción (servidor Oracle):
```bash
# Pull cambios
git pull

# Redesplegar si hubo cambios
docker-compose -f docker-compose.prod.yml up -d --build

# ✅ Sin conflictos porque producción usa docker-compose.prod.yml
```
