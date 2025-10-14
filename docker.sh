#!/bin/bash
# Script para facilitar operaciones con Docker Compose

set -e

echo "🐳 Malackathon FastAPI + Oracle Cloud - Docker Helper"
echo "=================================================="
echo ""

case "${1:-help}" in
  build)
    echo "🔨 Construyendo imagen Docker..."
    docker compose -f docker/docker-compose.yml build
    echo "✅ Imagen construida exitosamente"
    ;;
    
  up)
    echo "🚀 Levantando servicios..."
    docker compose -f docker/docker-compose.yml up -d
    echo "✅ Servicios iniciados"
    echo "📊 API disponible en: http://localhost:8000"
    echo "📖 Docs en: http://localhost:8000/docs"
    ;;
    
  down)
    echo "🛑 Deteniendo servicios..."
    docker compose -f docker/docker-compose.yml down
    echo "✅ Servicios detenidos"
    ;;
    
  logs)
    echo "📋 Mostrando logs (Ctrl+C para salir)..."
    docker compose -f docker/docker-compose.yml logs -f api
    ;;
    
  test)
    echo "🧪 Probando conexión a Oracle Cloud..."
    # Primero intenta contra el contenedor en ejecución
    if ! docker compose -f docker/docker-compose.yml exec api python scripts/test_connection.py; then
      echo "⚠️  El contenedor no está listo (reiniciando o no corriendo). Probando con 'docker compose run'..."
      docker compose -f docker/docker-compose.yml run --rm api python scripts/test_connection.py
    fi
    ;;
    
  shell)
    echo "🐚 Abriendo shell en el contenedor..."
    docker compose -f docker/docker-compose.yml exec api /bin/bash
    ;;
    
  restart)
    echo "🔄 Reiniciando servicios..."
    docker compose -f docker/docker-compose.yml restart api
    echo "✅ Servicios reiniciados"
    ;;
    
  rebuild)
    echo "🔨 Reconstruyendo desde cero..."
    docker compose -f docker/docker-compose.yml down
    docker compose -f docker/docker-compose.yml build --no-cache
    docker compose -f docker/docker-compose.yml up -d
    echo "✅ Reconstrucción completa"
    ;;
    
  health)
    echo "💚 Verificando health de la API..."
    curl -s http://localhost:8000/health | jq . || curl http://localhost:8000/health
    ;;
    
  clean)
    echo "🧹 Limpiando recursos Docker..."
    docker compose -f docker/docker-compose.yml down -v
    docker system prune -f
    echo "✅ Limpieza completada"
    ;;
    
  help|*)
    echo "Uso: ./docker.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  build    - Construir la imagen Docker"
    echo "  up       - Levantar los servicios"
    echo "  down     - Detener los servicios"
    echo "  logs     - Ver logs en tiempo real"
    echo "  test     - Probar conexión a Oracle Cloud"
    echo "  shell    - Abrir shell en el contenedor"
    echo "  restart  - Reiniciar servicios"
    echo "  rebuild  - Reconstruir desde cero (sin caché)"
    echo "  health   - Verificar health endpoint"
    echo "  clean    - Limpiar recursos Docker"
    echo "  help     - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./docker.sh build      # Construir imagen"
    echo "  ./docker.sh up         # Levantar API"
    echo "  ./docker.sh test       # Probar conexión Oracle"
    echo "  ./docker.sh logs       # Ver logs"
    ;;
esac
