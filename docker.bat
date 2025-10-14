@echo off
REM Docker Helper Script para Windows
REM Malackathon FastAPI + Oracle Cloud

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Malackathon Docker Helper (Windows)
echo ========================================
echo.

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="build" goto :build
if "%1"=="up" goto :up
if "%1"=="down" goto :down
if "%1"=="logs" goto :logs
if "%1"=="test" goto :test
if "%1"=="shell" goto :shell
if "%1"=="restart" goto :restart
if "%1"=="rebuild" goto :rebuild
if "%1"=="health" goto :health
if "%1"=="clean" goto :clean
goto :help

:build
echo [BUILD] Construyendo imagen Docker...
docker compose -f docker/docker-compose.yml build
if %errorlevel% equ 0 (
    echo [OK] Imagen construida exitosamente
) else (
    echo [ERROR] Fallo al construir la imagen
    exit /b 1
)
goto :end

:up
echo [UP] Levantando servicios...
docker compose -f docker/docker-compose.yml up -d
if %errorlevel% equ 0 (
    echo [OK] Servicios iniciados
    echo [INFO] API disponible en: http://localhost:8000
    echo [INFO] Docs en: http://localhost:8000/docs
) else (
    echo [ERROR] Fallo al levantar servicios
    exit /b 1
)
goto :end

:down
echo [DOWN] Deteniendo servicios...
docker compose -f docker/docker-compose.yml down
if %errorlevel% equ 0 (
    echo [OK] Servicios detenidos
) else (
    echo [ERROR] Fallo al detener servicios
    exit /b 1
)
goto :end

:logs
echo [LOGS] Mostrando logs (Ctrl+C para salir)...
docker compose -f docker/docker-compose.yml logs -f api
goto :end

:test
echo [TEST] Probando conexion a Oracle Cloud...
docker compose -f docker/docker-compose.yml exec api python scripts/test_connection.py || (
    echo [WARN] El contenedor no esta listo. Probando con 'docker compose run'...
    docker compose -f docker/docker-compose.yml run --rm api python scripts/test_connection.py
)
goto :end

:shell
echo [SHELL] Abriendo shell en el contenedor...
docker compose -f docker/docker-compose.yml exec api /bin/bash
goto :end

:restart
echo [RESTART] Reiniciando servicios...
docker compose -f docker/docker-compose.yml restart api
if %errorlevel% equ 0 (
    echo [OK] Servicios reiniciados
) else (
    echo [ERROR] Fallo al reiniciar
    exit /b 1
)
goto :end

:rebuild
echo [REBUILD] Reconstruyendo desde cero...
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml build --no-cache
docker compose -f docker/docker-compose.yml up -d
if %errorlevel% equ 0 (
    echo [OK] Reconstruccion completa
) else (
    echo [ERROR] Fallo en la reconstruccion
    exit /b 1
)
goto :end

:health
echo [HEALTH] Verificando health de la API...
curl -s http://localhost:8000/health
echo.
goto :end

:clean
echo [CLEAN] Limpiando recursos Docker...
docker compose -f docker/docker-compose.yml down -v
docker system prune -f
if %errorlevel% equ 0 (
    echo [OK] Limpieza completada
) else (
    echo [ERROR] Fallo en la limpieza
    exit /b 1
)
goto :end

:help
echo Uso: docker.bat [comando]
echo.
echo Comandos disponibles:
echo   build    - Construir la imagen Docker
echo   up       - Levantar los servicios
echo   down     - Detener los servicios
echo   logs     - Ver logs en tiempo real
echo   test     - Probar conexion a Oracle Cloud
echo   shell    - Abrir shell en el contenedor
echo   restart  - Reiniciar servicios
echo   rebuild  - Reconstruir desde cero (sin cache)
echo   health   - Verificar health endpoint
echo   clean    - Limpiar recursos Docker
echo   help     - Mostrar esta ayuda
echo.
echo Ejemplos:
echo   docker.bat build      # Construir imagen
echo   docker.bat up         # Levantar API
echo   docker.bat test       # Probar conexion Oracle
echo   docker.bat logs       # Ver logs
echo.
goto :end

:end
endlocal
