# 🚀 Guía Rápida: Configurar Deploy Automático

## Paso 1: Configurar Secrets en GitHub

1. Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions**
2. Click en **New repository secret** y agrega los siguientes:

```
SSH_PRIVATE_KEY     → Tu clave privada SSH completa (formato PEM)
SSH_HOST            → IP de tu VM Oracle (ej: 123.45.67.89)
SSH_USER            → Usuario SSH (ubuntu o opc)
CERTBOT_EMAIL       → Email para Let's Encrypt
DOMAIN              → dr-artificial.com
```

## Paso 2: Generar Clave SSH (si no la tienes)

```bash
# En tu máquina local
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy

# Copiar clave pública a la VM
ssh-copy-id -i ~/.ssh/github_deploy.pub ubuntu@TU_IP_ORACLE

# Ver clave privada para copiar a GitHub Secret
cat ~/.ssh/github_deploy
```

## Paso 3: Preparar VM Oracle (primera vez)

```bash
# Conectar por SSH
ssh ubuntu@TU_IP_ORACLE

# Crear directorio web y clonar repositorio
mkdir -p ~/web
cd ~/web
git clone https://github.com/TU_USUARIO/malackathon25.git
cd malackathon25

# Crear archivo .env (NO se versiona)
nano .env
# Agregar: ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN

# Dar permisos
chmod +x deploy.sh
chmod 600 .env
```

## Paso 4: ¡Listo!

Ahora cada vez que hagas **push a main**, se desplegará automáticamente:

```bash
git add .
git commit -m "Deploy automático activado"
git push origin main
```

Ve el progreso en: **GitHub → Actions**

---

## Deploy Manual (sin push)

1. GitHub → **Actions**
2. **Deploy to Oracle Cloud** → **Run workflow**

---

## Verificar Deploy

```bash
# Verificar salud
curl https://dr-artificial.com/health

# Ver logs en la VM
ssh ubuntu@TU_IP_ORACLE
cd ~/web/malackathon25
docker-compose -f docker-compose.prod.yml logs -f
```

---

📖 **Documentación completa:** [docs/CI-CD-SETUP.md](../docs/CI-CD-SETUP.md)

