# Configuración CI/CD - GitHub Actions

## Descripción General

El proyecto utiliza **GitHub Actions** para automatizar el despliegue en Oracle Cloud Infrastructure (OCI). Tras cada push a la rama `main`, el workflow ejecuta automáticamente el script `deploy.sh` en la VM de producción mediante SSH.

## Workflow: `deploy.yml`

**Ubicación:** `.github/workflows/deploy.yml`

**Triggers:**
- Push a la rama `main`
- Ejecución manual desde GitHub UI (`workflow_dispatch`)

**Jobs:**
1. **Checkout:** Descarga el código del repositorio
2. **Setup SSH:** Configura las credenciales SSH para conectar a Oracle VM
3. **Deploy:** Se conecta por SSH, actualiza el código y ejecuta `deploy_auto.sh`
4. **Health Check:** Verifica que la aplicación responde correctamente tras el despliegue

**Scripts de Deploy:**
- `deploy.sh` - Versión interactiva para deploy manual (requiere confirmación del usuario)
- `deploy_auto.sh` - Versión automática para CI/CD (sin interacción, usado por GitHub Actions)

---

## Configuración de Secrets en GitHub

Para que el workflow funcione, debes configurar los siguientes **secrets** en GitHub:

### Acceso al Repositorio
1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**

### Secrets Requeridos

| Secret Name | Descripción | Ejemplo |
|------------|-------------|---------|
| `SSH_PRIVATE_KEY` | Clave privada SSH para acceder a la VM de Oracle (formato PEM completo) | `-----BEGIN OPENSSH PRIVATE KEY-----\nMIIE...` |
| `SSH_HOST` | IP pública o hostname de la VM de Oracle | `123.45.67.89` |
| `SSH_USER` | Usuario SSH en la VM (generalmente `ubuntu` o `opc`) | `ubuntu` |
| `CERTBOT_EMAIL` | Email para notificaciones de Let's Encrypt | `davidmunvalle@uma.es` |
| `DOMAIN` | Dominio de producción | `dr-artificial.com` |

---

## Generación de Claves SSH

Si aún no tienes una clave SSH dedicada para CI/CD:

```bash
# En tu máquina local
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key

# Copiar clave pública a la VM de Oracle
ssh-copy-id -i ~/.ssh/github_deploy_key.pub ubuntu@<SSH_HOST>

# Copiar el contenido de la clave PRIVADA y agregarlo a GitHub Secrets
cat ~/.ssh/github_deploy_key
```

⚠️ **Importante:** 
- Guarda la clave privada completa incluyendo `-----BEGIN OPENSSH PRIVATE KEY-----` y `-----END OPENSSH PRIVATE KEY-----`
- **NUNCA** subas la clave privada al repositorio

---

## Configuración en Oracle VM

### 1. Clonar el repositorio (primera vez)

```bash
ssh ubuntu@<SSH_HOST>
cd ~
mkdir -p web
cd web
git clone https://github.com/<tu-usuario>/malackathon25.git
cd malackathon25
```

### 2. Configurar archivo `.env`

El archivo `.env` NO se versiona por seguridad. Créalo manualmente en la VM:

```bash
# Crear .env con las credenciales de Oracle DB
cat > .env << 'EOF'
ORACLE_USER=admin
ORACLE_PASSWORD=<tu_password>
ORACLE_DSN=<tu_dsn>
EOF
```

### 3. Asegurar permisos

```bash
chmod +x deploy.sh
chmod 600 .env
```

---

## Ejecución Manual del Workflow

Si necesitas forzar un despliegue sin hacer push:

1. Ve a tu repositorio en GitHub
2. Click en **Actions**
3. Selecciona el workflow **Deploy to Oracle Cloud**
4. Click en **Run workflow** → **Run workflow**

---

## Verificación Post-Deploy

Después de cada despliegue, el workflow ejecuta un health check:

```bash
curl -f https://dr-artificial.com/health
```

Si falla, el workflow marca el job como fallido y puedes revisar los logs en GitHub Actions.

---

## Monitoreo de Deploys

### Ver logs en tiempo real

```bash
# Desde la VM de Oracle
docker-compose -f docker-compose.prod.yml logs -f
```

### Ver logs del workflow

1. GitHub → **Actions**
2. Click en el workflow que quieres inspeccionar
3. Expande los pasos para ver logs detallados

---

## Troubleshooting

### Error: "Permission denied (publickey)"

**Causa:** La clave SSH no está configurada correctamente.

**Solución:**
1. Verifica que `SSH_PRIVATE_KEY` en GitHub Secrets tenga el formato correcto
2. Asegúrate de que la clave pública esté en `~/.ssh/authorized_keys` de la VM
3. Verifica permisos: `chmod 600 ~/.ssh/authorized_keys`

### Error: "deploy.sh: command not found"

**Causa:** El repositorio no está clonado en la VM o la ruta es incorrecta.

**Solución:**
1. Clona el repositorio: `mkdir -p ~/web && cd ~/web && git clone https://github.com/<usuario>/malackathon25.git`
2. Verifica la ruta en el workflow (por defecto: `~/web/malackathon25`)

### Error: "Health check failed"

**Causa:** Los servicios no están respondiendo tras el despliegue.

**Solución:**
1. SSH a la VM: `ssh ubuntu@<SSH_HOST>`
2. Verifica logs: `docker-compose -f docker-compose.prod.yml logs`
3. Verifica que los puertos 80/443 estén abiertos en Oracle Cloud Security Lists

### Error: "git reset --hard failed"

**Causa:** Cambios locales en la VM que impiden el pull.

**Solución:**
```bash
# En la VM
cd ~/web/malackathon25
git stash  # Guarda cambios locales
git fetch origin
git reset --hard origin/main
```

---

## Seguridad

### Rotación de Claves SSH

Se recomienda rotar las claves cada 90 días:

1. Genera nueva clave: `ssh-keygen -t ed25519 -f ~/.ssh/github_deploy_key_new`
2. Agrega nueva clave pública a la VM: `ssh-copy-id -i ~/.ssh/github_deploy_key_new.pub ubuntu@<SSH_HOST>`
3. Actualiza el secret `SSH_PRIVATE_KEY` en GitHub
4. Elimina la clave antigua de `authorized_keys`

### Protección de la Rama Main

Para evitar deploys accidentales:

1. GitHub → **Settings** → **Branches**
2. Add rule para `main`
3. Habilita **Require pull request reviews before merging**

---

## Próximas Mejoras

- [ ] Agregar notificaciones a Slack/Discord tras cada deploy
- [ ] Implementar rollback automático si el health check falla
- [ ] Agregar tests automáticos antes del deploy
- [ ] Configurar despliegues a entornos de staging/preview

---

## Referencias

- [GitHub Actions SSH Deploy](https://github.com/marketplace/actions/ssh-remote-commands)
- [Oracle Cloud Infrastructure Docs](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [Let's Encrypt - Certbot](https://certbot.eff.org/)

