# Docker Helper Script para Windows PowerShell
# Malackathon FastAPI + Oracle Cloud

param(
    [Parameter(Position=0)]
    [ValidateSet('build','up','down','logs','test','shell','restart','rebuild','health','clean','help')]
    [string]$Command = 'help'
)

$ErrorActionPreference = "Stop"

function Show-Header {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Malackathon Docker Helper (PowerShell)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Help {
    Write-Host "Uso: .\docker.ps1 [comando]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Comandos disponibles:" -ForegroundColor Green
    Write-Host "  build    - Construir la imagen Docker"
    Write-Host "  up       - Levantar los servicios"
    Write-Host "  down     - Detener los servicios"
    Write-Host "  logs     - Ver logs en tiempo real"
    Write-Host "  test     - Probar conexión a Oracle Cloud"
    Write-Host "  shell    - Abrir shell en el contenedor"
    Write-Host "  restart  - Reiniciar servicios"
    Write-Host "  rebuild  - Reconstruir desde cero (sin caché)"
    Write-Host "  health   - Verificar health endpoint"
    Write-Host "  clean    - Limpiar recursos Docker"
    Write-Host "  help     - Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Yellow
    Write-Host "  .\docker.ps1 build      # Construir imagen"
    Write-Host "  .\docker.ps1 up         # Levantar API"
    Write-Host "  .\docker.ps1 test       # Probar conexión Oracle"
    Write-Host "  .\docker.ps1 logs       # Ver logs"
    Write-Host ""
}

Show-Header

switch ($Command) {
    'build' {
        Write-Host "[BUILD] Construyendo imagen Docker..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Imagen construida exitosamente" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Fallo al construir la imagen" -ForegroundColor Red
            exit 1
        }
    }
    
    'up' {
        Write-Host "[UP] Levantando servicios..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Servicios iniciados" -ForegroundColor Green
            Write-Host "[INFO] API disponible en: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "[INFO] Docs en: http://localhost:8000/docs" -ForegroundColor Cyan
        } else {
            Write-Host "[ERROR] Fallo al levantar servicios" -ForegroundColor Red
            exit 1
        }
    }
    
    'down' {
        Write-Host "[DOWN] Deteniendo servicios..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml down
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Servicios detenidos" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Fallo al detener servicios" -ForegroundColor Red
            exit 1
        }
    }
    
    'logs' {
        Write-Host "[LOGS] Mostrando logs (Ctrl+C para salir)..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml logs -f api
    }
    
    'test' {
        Write-Host "[TEST] Probando conexión a Oracle Cloud..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml exec api python scripts/test_connection.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARN] El contenedor no está listo. Probando con 'docker compose run'..." -ForegroundColor Yellow
            docker compose -f docker/docker-compose.yml run --rm api python scripts/test_connection.py
        }
    }
    
    'shell' {
        Write-Host "[SHELL] Abriendo shell en el contenedor..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml exec api /bin/bash
    }
    
    'restart' {
        Write-Host "[RESTART] Reiniciando servicios..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml restart api
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Servicios reiniciados" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Fallo al reiniciar" -ForegroundColor Red
            exit 1
        }
    }
    
    'rebuild' {
        Write-Host "[REBUILD] Reconstruyendo desde cero..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml down
        docker compose -f docker/docker-compose.yml build --no-cache
        docker compose -f docker/docker-compose.yml up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Reconstrucción completa" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Fallo en la reconstrucción" -ForegroundColor Red
            exit 1
        }
    }
    
    'health' {
        Write-Host "[HEALTH] Verificando health de la API..." -ForegroundColor Yellow
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
            Write-Host $response.Content -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] No se pudo conectar a la API" -ForegroundColor Red
            Write-Host $_.Exception.Message -ForegroundColor Red
        }
    }
    
    'clean' {
        Write-Host "[CLEAN] Limpiando recursos Docker..." -ForegroundColor Yellow
        docker compose -f docker/docker-compose.yml down -v
        docker system prune -f
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Limpieza completada" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Fallo en la limpieza" -ForegroundColor Red
            exit 1
        }
    }
    
    'help' {
        Show-Help
    }
    
    default {
        Show-Help
    }
}
