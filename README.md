# MetroFlow

![Status](https://img.shields.io/badge/estado-production-success)
![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-3776AB)
![React](https://img.shields.io/badge/react-19-61DAFB)
![License](https://img.shields.io/badge/licencia-propietaria-lightgrey)
![Deploy](https://img.shields.io/badge/deploy-Vercel%20%7C%20Render-000000)

MetroFlow estima la ocupación en andén y vagón mediante visión artificial en el borde y expone el resultado en un panel operativo en la nube. Resuelve el monitoreo de aforo sin sensores dedicados ni transmisión de video. Está orientado a operación de transporte masivo, equipos de integración y evaluación de arquitecturas IaaS, PaaS y SaaS.

## Overview

El sistema separa inferencia local (edge), lógica de negocio (API) y visualización (dashboard). El ingestor envía telemetría anonimizada (`headcount`, estado de aforo) al backend; el frontend consulta la API cada seis segundos durante la detención del tren en andén.

| Capa | Componente | Producción |
|------|------------|------------|
| SaaS | Dashboard | https://frontend-green-xi-68.vercel.app |
| PaaS | API / OpenAPI | https://ocupacion-api.onrender.com · `/docs` |
| IaaS | PostgreSQL | Render (acceso interno) |
| Edge | YOLO + ingestor | Estación / `ai/` |

En Vercel: directorio raíz `frontend`, variable `VITE_API_URL` apuntando al API de Render (sin barra final).

## Core Features

- Detección y seguimiento de personas (YOLO11, ByteTrack) con línea virtual de cruce
- Ingestor edge hacia `POST /api/v1/analyze` (modo demo o inferencia en video)
- API REST: ocupación actual, historial y documentación OpenAPI
- Dashboard con KPIs, densidad referenciada a frecuencia EFE y estado de telemetría activa
- Persistencia en PostgreSQL con respaldo en memoria
- Despliegue en Vercel y Render

## Tech Stack

| Tecnología | Propósito |
|------------|-----------|
| Python, Ultralytics, OpenCV | Inferencia e ingestor edge |
| FastAPI, SQLAlchemy, asyncpg | API y persistencia |
| React, TypeScript, Vite, Tailwind | Panel operativo |
| PostgreSQL | Historial de ocupación |
| Docker Compose | Entorno local |
| Vercel / Render | SaaS y PaaS / IaaS |

## Getting Started

**Requisitos:** Node.js 20+, Python 3.10+, Docker (opcional).

```powershell
docker compose up -d

cd backend
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

cd ..\frontend
npm install
npm run dev
```

Local: API `http://localhost:8000` · UI `http://localhost:5173`

```powershell
.\scripts\verify-rubric.ps1 -ApiUrl http://localhost:8000

cd ai
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python edge_ingestor.py --preset efe --api https://ocupacion-api.onrender.com
```

Modo `--live` ejecuta inferencia real sobre el video EFE; por defecto el preset envía un guión de abordaje aleatorio (POST cada 6 s, ventana 20–40 s). Overlay y exportación: `metro_demo_video.py --preset efe`.

## Environment Variables

| Variable | Capa | Descripción |
|----------|------|-------------|
| `DATABASE_URL` | Backend | `postgresql+asyncpg://...` |
| `CORS_EXTRA_ORIGIN` | Backend | Origen del dashboard (Vercel) |
| `VITE_API_URL` | Frontend | URL del API en build |

Ver [`.env.example`](.env.example).

## Project Structure

```
├── ai/           # Inferencia, ingestor, presets de video
├── backend/      # API FastAPI
├── frontend/     # Dashboard (raíz de Vercel)
├── docs/         # Documentación técnica y evidencias
├── scripts/      # Verificación y demos
└── render.yaml   # Blueprint Render
```

## Roadmap

- Ingesta RTSP y procesamiento por lote en edge
- Campo de última actualización en la API de ocupación
- Exportación ONNX en el servicio de API (opcional)

## License

Todos los derechos reservados. Uso y redistribución restringidos sin autorización escrita de los titulares.

## Authors

Proyecto académico — Infraestructura TI.

<table>
  <tr>
    <td align="center" width="20%">
      <img src="https://avatars.githubusercontent.com/u/105559567?v=4" width="96" height="96" style="border-radius:50%" alt="Andres Tapia" /><br>
      <strong>Andrés Tapia</strong><br>
      <sub>Technical Lead</sub><br>
      <a href="mailto:a.tapialopez@uandresbello.edu">Email</a>
    </td>
    <td align="center" width="20%">
      <img src="https://avatars.githubusercontent.com/u/128178198?v=4" width="96" height="96" style="border-radius:50%" alt="Lukas Flores" /><br>
      <strong>Lukas Flores</strong><br>
      <sub>ML Developer</sub><br>
      <a href="mailto:l.floreszuiga@uandresbello.edu">Email</a>
    </td>
    <td align="center" width="20%">
      <img src="https://avatars.githubusercontent.com/u/190417123?v=4" width="96" height="96" style="border-radius:50%" alt="Gonzalo Jara" /><br>
      <strong>Gonzalo Jara</strong><br>
      <sub>Backend Developer</sub><br>
      <a href="mailto:g.jaravrsalovic@uandresbello.edu">Email</a>
    </td>
    <td align="center" width="20%">
      <img src="https://avatars.githubusercontent.com/u/128172645?v=4" width="96" height="96" style="border-radius:50%" alt="Felipe Figueroa" /><br>
      <strong>Felipe Figueroa</strong><br>
      <sub>Frontend Developer</sub><br>
      <a href="mailto:f.figueroadaz2@uandresbello.edu">Email</a>
    </td>
    <td align="center" width="20%">
      <img src="https://avatars.githubusercontent.com/u/207567094?v=4" width="96" height="96" style="border-radius:50%" alt="Jose Maraboli" /><br>
      <strong>Jose Maraboli</strong><br>
      <sub>Documentation & QA</sub><br>
      <a href="mailto:j.marabolileal@uandresbello.edu">Email</a>
    </td>
  </tr>
</table>
