# MetroFlow

![Status](https://img.shields.io/badge/estado-en%20desarrollo-neutral)
![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-3776AB)
![React](https://img.shields.io/badge/react-19-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11+-009688)
![Deploy](https://img.shields.io/badge/despliegue-Vercel%20%7C%20Render-000000)

Sistema de monitoreo de aforo para transporte masivo basado en visión artificial en el borde, API REST y panel operativo en la nube. Estima la ocupación por vagón sin sensores físicos dedicados y transmite únicamente métricas agregadas. Dirigido a equipos de operación, integración TI y evaluación de arquitecturas cloud en capas (SaaS, PaaS, IaaS).

## Overview

MetroFlow separa inferencia (edge), lógica de negocio (API) y visualización (dashboard). Un ingestor local ejecuta YOLOv8 sobre video o cámara y envía conteos anonimizados al backend; el frontend consulta el estado cada cinco segundos.

## Core Features

- Detección de personas con YOLOv8n (clase COCO, umbral de confianza configurable).
- Ingesta edge con muestreo de frames y `POST` hacia `/api/v1/analyze`.
- API FastAPI con ocupación actual, historial y OpenAPI en `/docs`.
- Dashboard React con KPIs, esquema de vagón, alertas por umbral y gráfico de historial.
- Persistencia opcional en PostgreSQL; degradación a memoria si la base no está disponible.
- Despliegue documentado en Vercel (UI) y Render (API + base de datos).

## Tech Stack

| Tecnología | Propósito |
|------------|-----------|
| Python 3.11+, Ultralytics, OpenCV | Inferencia y edge ingestor |
| FastAPI, Uvicorn, SQLAlchemy, asyncpg | API y persistencia |
| React 19, TypeScript, Vite, Tailwind, Recharts | Panel operativo |
| PostgreSQL 16 | Series de tiempo de ocupación |
| Docker Compose | Entorno local API + base de datos |
| Vercel / Render | SaaS y PaaS/IaaS en producción |

## Getting Started

**Requisitos:** Node.js 20+, Python 3.11+, Docker (opcional, recomendado para historial).

```powershell
# API y PostgreSQL (Docker)

docker compose up -d

# API sin Docker

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Dashboard

cd frontend
npm install
npm run dev
```

URLs locales: API `http://localhost:8000`, 
documentación `http://localhost:8000/docs`, 
UI `http://localhost:5173`.

```powershell
# Verificación de endpoints

.\scripts\verify-rubric.ps1 -ApiUrl http://localhost:8000

# Demo edge → API (requiere venv en ai/ y video en ai/videos/sample.mp4)

cd ai
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
python edge_ingestor.py --api http://localhost:8000 --max-frames 90 --stride 10
```

## Environment Variables

| Variable | Capa | Descripción |
|----------|------|-------------|
| `DATABASE_URL` | Backend | URL async (`postgresql+asyncpg://...`). En Render, convertir `postgres://` al prefijo indicado. |
| `CORS_EXTRA_ORIGIN` | Backend | Origen del dashboard en producción (URL de Vercel). |
| `VITE_API_URL` | Frontend | URL pública del API en build (Vercel). |

Plantilla: [`.env.example`](.env.example).

## Project Structure

```
├── ai/           # YOLO, ingestor edge, contratos JSON
├── backend/      # FastAPI, modelos, repositorio
├── frontend/     # Dashboard React
├── docs/         # Arquitectura, API, despliegue, guías
└── scripts/      # Arranque local, verificación, demo integrada
```

## Roadmap

- Inferencia ONNX en el contenedor de API.
- Tracking persistente (DeepSORT) en servidor.
- Ingesta RTSP e imágenes por lote en el ingestor edge.

## Authors
Proyecto académico — Infraestructura TI. 

<table>
  <tr>
    <td align="center" width="20%">
      <img src="https://avatars.githubusercontent.com/u/105559567?v=4" width="96" height="96" style="border-radius:50%" alt="Andres Tapia" /><br>
      <strong>Andrés Tapia</strong><br>
      <sub>Technical Lead</sub><br>
      <a href="mailto:a.tapialpez@uandresbello.edu">Email</a>
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
      <img src="https://avatars.githubusercontent.com/u/207567094?v=4" width="96" height="96" style="border-radius:50%" alt="Fernando Salazar" /><br>
      <strong>Jose Maraboli</strong><br>
      <sub>Documentation & QA</sub><br>
      <a href="mailto:f.salazarcartes@uandresbello.edu">Email</a>
    </td>
  </tr>
</table>

## License

All rights reserved.

This project is proprietary. No part of this repository may be copied, modified, distributed, sublicensed, or used for commercial purposes without prior written permission from the project owners.