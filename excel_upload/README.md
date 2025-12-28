# 🏥 API de Gestión de Medicamentos – Farmacia

API REST sencilla desarrollada en **Python** usando `http.server`, conectada a **MySQL**, que permite:

- 📥 Carga masiva de medicamentos desde Excel
- 📋 Listado de medicamentos
- 🔄 Actualización automática si el código ya existe (upsert)
- 🗑️ Eliminación de medicamentos
- 📄 Descarga de formato Excel
- 🌐 Consumo desde frontend con Bootstrap

---

## 🧱 Arquitectura del proyecto

```
EXCEL_UPLOAD/
│
├── api/                 # Backend (Python)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
│
├── mysql/               # Base de datos
│   └── init.sql
│
├── web/                 # Frontend (HTML + Nginx)
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
│
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## 🚀 Tecnologías usadas

* **Backend:** Python 3.11 (`http.server`)
* **Base de datos:** MySQL
* **Frontend:** HTML + JavaScript + Nginx
* **Contenedores:** Docker + Docker Compose
* **Automatización:** Makefile

---

## ▶️ Levantar el proyecto (Makefile)

Este proyecto está preparado para que **solo necesites clonar el repositorio y ejecutar un comando**.

### 🔹 Requisitos

* Docker
* Docker Compose
* Make

---

### 🔹 Comandos disponibles

```bash
make help
```

```text
Comandos disponibles:
  make up      - Levanta el proyecto
  make down    - Detiene los contenedores
  make build   - Reconstruye las imágenes
  make logs    - Ver logs
```

---

### 🚀 Levantar todo el proyecto

```bash
make up
```

Este comando:

* Construye las imágenes Docker
* Levanta la API en Python
* Levanta el frontend con Nginx
* Inicializa MySQL usando `init.sql`

👉 **No se requiere configuración adicional.**

---

### 🛑 Detener los contenedores

```bash
make down
```

---

### 🔨 Reconstruir imágenes

```bash
make build
```

---

### 📜 Ver logs en tiempo real

```bash
make logs
```

---

## 🌐 Accesos

| Servicio | URL                                            |
| -------- | ---------------------------------------------- |
| Frontend | [http://localhost:8080](http://localhost:8080) |
| API      | [http://localhost:8000](http://localhost:8000) |

---

## 🔌 Endpoints de la API

### 📄 Listar medicamentos

```http
GET /api/medicamentos
```

Respuesta:

```json
[
  {
    "codigo": "54",
    "nombre": "Paracetamol",
    "cantidad": 100,
    "precio": 2500
  }
]
```

---

### ➕ Subir archivo Excel

```http
POST /api/upload
```

**Form‑Data:**

* `file`: archivo `.xlsx`

📌 Si el código del medicamento **ya existe**, se **actualiza**.

---

### ❌ Eliminar medicamento

```http
DELETE /api/medicamentos?codigo=MED001
```

Respuesta:

```json
{ "message": "Medicamento eliminado correctamente" }
```

---

## 🧪 Probar la API con Postman

| Acción            | Método | URL               | Params           |
| ------------------| ------ | ----------------- | ---------------- |
| Descragar formato | GET    | /api/format       | —                |
| Listar            | GET    | /api/medicamentos | —                |
| Subir Excel       | POST   | /api/upload       | form‑data `file` |
| Eliminar          | DELETE | /api/medicamentos | `codigo`         |

---

🚀 *Clona, ejecuta `make up` y empieza a trabajar.*
