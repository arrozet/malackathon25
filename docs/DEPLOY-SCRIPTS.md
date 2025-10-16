# Scripts de Deploy - Brain

## Descripción General

El proyecto cuenta con **dos scripts de deploy** diseñados para diferentes escenarios de uso.

---

## 📋 Comparación de Scripts

| Característica | `deploy.sh` | `deploy_auto.sh` |
|---------------|-------------|------------------|
| **Uso principal** | Deploy manual por DevOps Engineer | Deploy automático en CI/CD |
| **Interactividad** | ✅ Requiere confirmaciones del usuario | ❌ Completamente no interactivo |
| **Verificación DNS** | Pregunta si continuar en caso de error | Continúa automáticamente con warning |
| **Oracle Security List** | Requiere confirmación manual | Asume configuración correcta |
| **GitHub Actions** | ❌ No compatible | ✅ Compatible |
| **Deploy local** | ✅ Recomendado | ⚠️ Posible pero innecesario |

---

## 🔧 `deploy.sh` - Deploy Manual

### Uso
```bash
./deploy.sh [email@ejemplo.com]
```

### Características
- **Interactivo:** Solicita confirmaciones en pasos críticos
- **Seguro:** Verifica DNS y configuración antes de continuar
- **Informativo:** Proporciona warnings y espera confirmación del operador
- **Educativo:** Ideal para entender el proceso de deploy paso a paso

### Casos de Uso
- ✅ Primer deploy en un servidor nuevo
- ✅ Deploy manual por parte del DevOps Engineer
- ✅ Debugging de problemas de deploy
- ✅ Verificación de configuración de infraestructura

### Puntos de Confirmación
1. **DNS Mismatch:** Si la IP del servidor no coincide con el DNS
2. **Oracle Cloud Security List:** Confirma que los puertos 80/443 están abiertos

---

## 🤖 `deploy_auto.sh` - Deploy Automático (CI/CD)

### Uso
```bash
./deploy_auto.sh [email@ejemplo.com]
```

### Características
- **No interactivo:** Ejecuta sin pausas ni confirmaciones
- **Resiliente:** Continúa ante warnings no críticos
- **CI/CD-ready:** Diseñado para GitHub Actions y pipelines
- **Rápido:** Sin esperas por input del usuario

### Casos de Uso
- ✅ GitHub Actions (push a main)
- ✅ Deploy automático en CI/CD
- ✅ Scripts de automatización
- ✅ Cron jobs de deploy programados

### Diferencias Clave
1. **DNS Mismatch:** Muestra warning pero continúa
2. **Oracle Cloud Security List:** Asume configuración correcta sin preguntar
3. **Logs:** Formato optimizado para logs de CI/CD

---

## 🎯 ¿Cuál Usar?

### Usa `deploy.sh` si:
- 🔧 Estás haciendo el primer deploy
- 👨‍💻 Quieres control manual del proceso
- 🐛 Estás debuggeando problemas
- 📚 Estás aprendiendo el proceso de deploy

### Usa `deploy_auto.sh` si:
- 🚀 Estás configurando CI/CD
- 🤖 Necesitas deploy automático sin interacción
- ⏱️ Quieres deploy rápido sin confirmaciones
- 🔄 El servidor ya está configurado correctamente

---

## 📝 Proceso de Deploy (ambos scripts)

Ambos scripts siguen el mismo flujo de 7 pasos:

```
[1/7] Verificando requisitos...
      ├── Docker instalado
      ├── docker-compose instalado
      ├── Archivo .env existe
      └── nginx-prod.conf existe

[2/7] Verificando DNS...
      ├── Obtener IP del servidor
      ├── Obtener IP del dominio
      └── Comparar IPs
          ├── deploy.sh: Pregunta si continuar ❓
          └── deploy_auto.sh: Continúa automáticamente ✓

[3/7] Configurando firewall...
      ├── Configurar UFW (puertos 80, 443)
      └── Verificar Oracle Cloud Security List
          ├── deploy.sh: Requiere confirmación ❓
          └── deploy_auto.sh: Asume configuración correcta ✓

[4/7] Verificando certificado SSL...
      ├── Si existe: Verificar expiración
      └── Si no existe: Obtener con Certbot
          ├── Crear directorio /var/www/certbot
          ├── Iniciar servicios temporales
          └── Ejecutar certbot (modo no interactivo)

[5/7] Configurando renovación automática SSL...
      └── Crear cron job (3 AM diario)

[6/7] Verificando configuración de producción...
      └── docker-compose.prod.yml existe

[7/7] Desplegando servicios...
      ├── Detener servicios existentes
      ├── Rebuild imágenes (--no-cache)
      ├── Iniciar servicios
      ├── Health checks (backend, frontend, nginx)
      └── Verificar HTTPS
```

---

## 🔒 Requisitos Previos (ambos scripts)

### En la VM
- ✅ Docker y docker-compose instalados
- ✅ Archivo `.env` configurado con credenciales de Oracle DB
- ✅ Repositorio clonado en `~/web/malackathon25`
- ✅ Usuario con permisos sudo

### Infraestructura
- ✅ DNS configurado: `dr-artificial.com` → IP de la VM
- ✅ Oracle Cloud Security List: Ingress Rules para puertos 80 y 443
- ✅ UFW (Uncomplicated Firewall) configurado

### Certificado SSL
- ✅ Email válido para Let's Encrypt
- ✅ Puerto 80 accesible (para ACME challenge)
- ✅ Dominio apuntando a la VM antes de obtener certificado

---

## 🚨 Troubleshooting

### Error: "Archivo .env no encontrado"
**Causa:** El archivo `.env` no se versiona en Git

**Solución:**
```bash
cd ~/web/malackathon25
cat > .env << 'EOF'
ORACLE_USER=admin
ORACLE_PASSWORD=<tu_password>
ORACLE_DSN=<tu_dsn>
EOF
chmod 600 .env
```

### Error: "certbot: command not found"
**Causa:** Certbot no está instalado

**Solución:**
```bash
sudo apt update
sudo apt install certbot -y
```

### Error: Exit code 1 en paso [3/7] (deploy.sh)
**Causa:** No se confirmó la configuración de Oracle Cloud Security List

**Solución:**
- Responder "y" cuando el script pregunte
- O usar `deploy_auto.sh` que no requiere confirmación

### Error: HTTPS no responde
**Causa:** Certificado SSL no se obtuvo correctamente o nginx no inició

**Solución:**
```bash
# Ver logs de nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Verificar certificado
sudo certbot certificates

# Reiniciar nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 📚 Referencias

- [Documentación CI/CD](./CI-CD-SETUP.md)
- [Guía rápida de deploy](../.github/DEPLOY_SETUP.md)
- [Let's Encrypt - Certbot](https://certbot.eff.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## 🔄 Mantenimiento

### Actualizar Scripts
Si necesitas modificar la lógica de deploy:

1. **Modifica `deploy.sh` primero** (versión de referencia)
2. **Replica cambios en `deploy_auto.sh`** removiendo interactividad
3. **Prueba localmente** con `deploy.sh`
4. **Prueba en CI/CD** con `deploy_auto.sh` mediante push a una rama de prueba

### Versionado
Ambos scripts deben mantenerse sincronizados en su lógica core, solo difiriendo en:
- Puntos de confirmación/interacción
- Manejo de errores no críticos
- Formato de mensajes (manual vs automatizado)

