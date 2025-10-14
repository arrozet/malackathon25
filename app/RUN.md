# Guía rápida de ejecución

## Dependencias requeridas

- Python 3.12 instalado (accesible como `py -3.12`).
- Node.js 20+ (incluye npm 10+).

## Backend (desde la raíz del repo)

```powershell
cd <repo root>
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.back.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend (desde la raíz del repo)

```powershell
cd <repo root>
cd app/root
npm install
echo VITE_API_URL=http://localhost:8000 > app\front\.env   # si no existe
npm run dev
```

Mantén ambas terminales abiertas para que el backend y el frontend funcionen en conjunto.


