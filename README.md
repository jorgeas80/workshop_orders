# Workshop Orders

Mini-aplicación para consultar pedidos: FastAPI, SQLite y React con TypeScript.
Un único listado muestra identificador, cliente, importe y estado.

## Requisitos

- Python 3.11 o posterior; entorno comprobado con Python 3.14.6.
- Node.js 22.12 o posterior; entorno comprobado con Node.js 25.9.0.
- npm y make. Hay un comando Python equivalente para resetear sin make.

Tras clonar el repositorio, abre una terminal en su raíz. Todos los comandos
siguientes indican desde qué directorio ejecutarlos.

## Preparación

Backend, desde la raíz:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-dev.lock -e './backend[test]'
```

`requirements-dev.lock` fija las dependencias de ejecución y pruebas del
entorno comprobado; no contiene rutas locales ni el paquete editable.

Frontend, desde la raíz:

```bash
cd frontend
npm ci
```

`package-lock.json` fija las versiones frontend. No uses `npm install` para
actualizarlas durante la preparación del taller.

## Restaurar SQLite

Desde la raíz:

```bash
make reset-db
```

Recrea la tabla de pedidos y carga exactamente:

| ID | Cliente | Total | Estado |
| --- | --- | --- | --- |
| ORD-1001 | Alice | 84.50 € | pending |
| ORD-1002 | Bob | 120.00 € | processing |
| ORD-1003 | Carol | 39.90 € | shipped |

La base se genera en `backend/data/orders.sqlite3` y se ignora en Git.
El reset descarta cambios en los pedidos; ejecútalo con el backend detenido.
Dos ejecuciones consecutivas producen el mismo estado.

Ruta alternativa, desde la raíz:

```bash
make reset-db DB_PATH=backend/data/ensayo.sqlite3
```

Sin make, desde `backend/`:

```bash
PYTHONPATH=src .venv/bin/python -B -m orders_app.infrastructure.database
```

## Arranque

Terminal 1, desde la raíz, después del reset:

```bash
cd backend
.venv/bin/python -B -m uvicorn orders_app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2, desde la raíz:

```bash
cd frontend
npm run dev
```

Abre [la pantalla de pedidos](http://127.0.0.1:5173).
Vite reenvía `/api` a FastAPI en `127.0.0.1:8000`; no hace falta configurar CORS.
Si el puerto 5173 está ocupado, Vite falla sin cambiarlo silenciosamente.
Detén cada proceso con Ctrl+C. Arrancar el backend no inicializa SQLite.

La pantalla muestra carga, lista vacía y error; «Reintentar» repite una carga
fallida. El build genera archivos estáticos; el proxy descrito es de desarrollo.

## API

- `GET /api/orders`: array JSON, HTTP 200, también cuando está vacío.
- `GET /api/orders/{order_id}`: objeto JSON con HTTP 200, o HTTP 404 con
  `{"detail": "Order not found"}`.
- [Documentación interactiva](http://127.0.0.1:8000/docs).

Cada objeto contiene `id`, `customer_name`, `total` y `status`.
El importe es una cadena decimal con dos posiciones, por ejemplo `"84.50"`.

## Verificación

Backend, desde `backend/`:

```bash
.venv/bin/python -m pytest
```

Frontend, desde `frontend/`:

```bash
npm test
npm run typecheck
npm run build
```

Los tests SQLite utilizan bases independientes en `backend/.pytest_tmp`; no
modifican la base de demo. `npm test` ejecuta la suite una vez y termina.
No se ha configurado lint; las comprobaciones disponibles son las anteriores.

Para ensayar desde un estado conocido: detén los servicios, ejecuta el reset,
arranca ambos y comprueba los tres pedidos en pantalla.

## Orientación

- `backend/src/orders_app/`: dominio, consultas, adaptador SQLite y API.
- `frontend/src/`: cliente HTTP, hook de carga y presentación.
- `backend/tests/` y `frontend/tests/`: pruebas por responsabilidad.
- [Arquitectura](docs/architecture.md): límites y dirección de dependencias.
- `AGENTS.md`: instrucciones operativas para trabajar sobre el código.
