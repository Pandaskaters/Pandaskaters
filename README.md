# 🚗 PandaSkaters – Plataforma de Ridesharing

> Aplicación móvil de transporte inteligente tipo Uber/InDrive construida con FastAPI + HTML/CSS/JS + Leaflet Maps

---

## 🌟 Características

| Módulo | Descripción |
|--------|-------------|
| 🔐 Auth JWT | Registro y login para pasajeros, conductores y admins |
| 🗺️ Mapa en tiempo real | Leaflet + OpenStreetMap, geolocalización, rutas |
| 🚗 Solicitud de viajes | Selección de servicio, estimación de precio, tracking |
| 💰 Tarifas dinámicas | Cálculo por km + tarifa base según tipo de servicio |
| 📡 WebSockets | Notificaciones en tiempo real conductor ↔ pasajero |
| 📊 Admin Dashboard | Estadísticas, gestión de conductores, viajes activos |
| 📱 PWA | Instalable en Android/iPhone como app nativa |

---

## 🎨 Diseño

- **Tema oscuro** con colores Negro profundo / Gris oscuro / Verde Lima
- **Tipografía** Poppins
- **Animaciones** fluidas y transiciones suaves
- **Optimizado** exclusivamente para dispositivos móviles
- Inspirado visualmente en Uber, InDrive, Cabify

---

## 🏗️ Estructura del Proyecto

```
pandaskaters/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + lifespan
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy async + init_db
│   │   ├── models/          # User, Driver, Vehicle, Ride
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # auth, rides, drivers, admin, websocket
│   │   ├── services/        # auth_service, fare_service
│   │   ├── middleware/       # JWT auth dependency
│   │   └── utils/           # jwt_handler, password_handler
│   ├── run.py               # Uvicorn entrypoint
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html           # Splash + Login + Registro
│   ├── passenger/
│   │   ├── home.html        # Mapa principal + solicitud viaje
│   │   ├── history.html     # Historial de viajes
│   │   └── profile.html     # Perfil usuario
│   ├── driver/
│   │   ├── home.html        # Panel conductor + mapa
│   │   ├── earnings.html    # Ganancias y estadísticas
│   │   └── profile.html     # Perfil conductor
│   ├── admin/
│   │   └── dashboard.html   # Dashboard administrativo completo
│   ├── css/
│   │   └── main.css         # Design system completo
│   ├── js/
│   │   ├── api.js           # HTTP client + helpers
│   │   ├── auth.js          # Login/Registro logic
│   │   ├── map.js           # Leaflet map module
│   │   ├── passenger.js     # Lógica pasajero
│   │   └── driver.js        # Lógica conductor
│   └── manifest.json        # PWA manifest
├── database/
│   ├── init.sql             # Schema PostgreSQL
│   └── seed.sql             # Datos de prueba
└── .gitignore
```

---

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Python 3.11+
- PostgreSQL 15+ (o SQLite para desarrollo)

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd pandaskaters
```

### 2. Configurar el backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
cp .env.example .env
# Edita .env con tu DATABASE_URL y SECRET_KEY
```

### 3. Inicializar base de datos

**SQLite (desarrollo rápido — sin configuración extra):**
```bash
# DATABASE_URL=sqlite+aiosqlite:///./pandaskaters.db  (ya viene por defecto)
python run.py
# La DB se crea automáticamente al iniciar
```

**PostgreSQL (producción):**
```bash
# Crear la base de datos
createdb pandaskaters
psql pandaskaters < ../database/init.sql
psql pandaskaters < ../database/seed.sql  # datos de prueba

# En .env:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pandaskaters
```

### 4. Ejecutar la app

```bash
cd backend
python run.py
```

La aplicación estará disponible en: **http://localhost:8000**

---

## 🔑 Credenciales de Prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| 👤 Pasajero | passenger@demo.com | demo123 |
| 🚗 Conductor | driver@demo.com | demo123 |
| 🛡️ Admin | admin@pandaskaters.com | admin123 |

> Los botones "Demo" en la pantalla de login cargan estas credenciales automáticamente.

---

## 📡 API REST

Documentación interactiva disponible en:
- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

### Endpoints principales

```
POST   /api/auth/login                  Login
POST   /api/auth/register/passenger     Registro pasajero
POST   /api/auth/register/driver        Registro conductor
GET    /api/auth/me                     Usuario actual

GET    /api/rides/estimate              Estimar tarifas
POST   /api/rides/request               Solicitar viaje
GET    /api/rides/active                Viaje activo
PATCH  /api/rides/{id}/status           Actualizar estado
POST   /api/rides/driver/accept/{id}    Conductor acepta viaje

GET    /api/drivers/nearby              Conductores cercanos
PATCH  /api/drivers/me/location         Actualizar ubicación
PATCH  /api/drivers/me/status           Online/Offline

GET    /api/admin/stats                 Estadísticas
GET    /api/admin/drivers               Listar conductores
PATCH  /api/admin/drivers/{id}/approve  Aprobar conductor
GET    /api/admin/users                 Listar usuarios

WS     /ws/{user_id}                    WebSocket tiempo real
```

---

## 💰 Cálculo de Tarifas

| Servicio | Tarifa Base | Por km |
|----------|-------------|--------|
| 🚗 Económico | $3.00 | $0.80/km |
| 🚙 Premium | $5.00 | $1.50/km |
| 🏍️ MotoTaxi | $2.00 | $0.50/km |

*Configurable en `.env` o desde el panel admin.*

---

## 🗺️ Mapas

Usa **Leaflet.js + OpenStreetMap** con tiles oscuros de CartoCDN.

Para usar **Google Maps** en su lugar:
1. Obtén un API key en Google Cloud Console
2. Reemplaza la inicialización en `map.js`
3. Agrega `MAPS_API_KEY=<tu-key>` en `.env`

---

## 📱 Instalación como PWA

En Chrome/Safari móvil:
1. Abre la app en el navegador
2. Menú → "Agregar a pantalla de inicio"
3. ¡Listo! Funciona como app nativa

---

## 🔒 Seguridad

- Contraseñas encriptadas con **bcrypt**
- Autenticación con **JWT** (Bearer tokens)
- CORS configurado por entorno
- Validación de inputs con **Pydantic**
- Separación de roles: passenger / driver / admin

---

## 🧪 Tech Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 + FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | python-jose + passlib/bcrypt |
| WebSockets | FastAPI WebSocket nativo |
| Base de datos | SQLite (dev) / PostgreSQL (prod) |
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Mapas | Leaflet.js + OpenStreetMap |
| Iconos | Font Awesome 6 |
| Fuente | Google Fonts – Poppins |
| PWA | Web App Manifest |

---

*PandaSkaters © 2026 – Plataforma de Transporte Inteligente*
