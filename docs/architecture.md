# Arquitectura

## Alcance y dependencias

La aplicación consulta pedidos y los presenta en una sola pantalla.
Las responsabilidades están separadas con módulos pequeños y un único puerto.

```text
API → aplicación → dominio
infraestructura → dominio
main.py → API + infraestructura (composición)
UI React → hook de carga → cliente HTTP → API
```

La dirección de ejecución no obliga a importar la implementación: los casos
de uso llaman al contrato `OrderRepository`, definido en dominio, y la
composición les proporciona `SQLiteOrderRepository`. Dominio y aplicación
utilizan solo la biblioteca estándar de Python.

## Dominio

`domain/order.py` contiene `Order`, una dataclass inmutable con `id`,
`customer_name`, `total` como Decimal y `status` como OrderStatus.
El importe debe ser finito, no negativo y representable en céntimos.
El estado debe pertenecer al catálogo definido en ese módulo. No se impone
un patrón al identificador ni reglas adicionales al nombre.

`domain/order_repository.py` define un Protocol con dos consultas:
`list_orders()` devuelve pedidos ordenados por id o una lista vacía;
`get_order(id)` devuelve un pedido o None. El contrato no expone SQL o HTTP.

## Aplicación

`application/orders.py` contiene las funciones `list_orders(repository)` y
`get_order(repository, order_id)`. La segunda interpreta la ausencia mediante
`OrderNotFound`, que conserva el identificador solicitado. Los fallos técnicos
se propagan. Los casos de uso no conocen SQLite, FastAPI ni Pydantic.

## Infraestructura y persistencia

`infrastructure/sqlite_order_repository.py` implementa las dos consultas con
sqlite3. Cada operación abre una conexión de solo lectura y la cierra con
`contextlib.closing`, incluso si falla. No hay conexión global compartida.
El listado usa ORDER BY id; el detalle utiliza un parámetro SQL.
Una ruta inexistente falla sin crear una base vacía.

El adaptador transforma sqlite3.Row en Order. SQLite guarda `total_cents` como
entero; se convierte a Decimal y se divide entre 100 sin pasar por float.
El esquema restringe identidad, campos no nulos, importe y estados válidos.

`infrastructure/database.py` contiene esquema y datos iniciales. El reset
recrea la tabla e inserta los tres pedidos en una transacción explícita.
Se confirma al terminar, se revierte si falla y siempre se cierra la conexión.
No hay efectos sobre la base al importar módulos; solo la función de reset o
su comando crean directorios y datos. `make reset-db` invoca ese comando.

## API y composición

`main.py` expone `create_app(database_path)` y `app` para Uvicorn. Construye el
repositorio y lo pasa explícitamente a `api/orders.py`, cuyo router captura
la dependencia. Construir la aplicación no abre ni inicializa SQLite.

Las dos rutas GET invocan los casos de uso existentes. Pydantic vive únicamente
en el modelo de respuesta HTTP. La salida contiene id, customer_name, total
como cadena con dos decimales y status. El listado devuelve un array; el detalle
un objeto. El endpoint traduce OrderNotFound a HTTP 404. Los errores técnicos
no se ocultan como listas vacías o pedidos inexistentes.

## Frontend

- `api/orders.ts`: fetch a `/api/orders`, estado HTTP y validación del JSON.
  Rechaza respuestas inválidas y recibe un AbortSignal opcional.
- `orders/application/useOrders.ts`: coordina loading, success y error. La
  ausencia de datos es success con lista vacía. Reintentar inicia otra carga;
  la limpieza aborta la petición y evita aplicar respuestas obsoletas.
- `orders/ui/`: OrdersPage presenta estados, OrderList organiza el listado y
  OrderCard muestra cada pedido. Los componentes no acceden a HTTP.
- `orders/types.ts`: contrato de datos para lectura, sin reglas de negocio.

Los importes se presentan como cadenas para conservar los céntimos. Las
etiquetas de estado son textos de presentación. Se utiliza HTML semántico,
role=status para carga/vacío, role=alert para error y foco visible en el botón.
CSS organiza tarjetas que se adaptan al ancho. No hay router ni estado global.
Vite reenvía `/api` al backend únicamente durante desarrollo.

## Estrategia de pruebas

| Responsabilidad | Dependencias | Qué verifica |
| --- | --- | --- |
| Dominio | Objetos en memoria | Estados e importes válidos e inválidos |
| Aplicación | Fake solo en tests | Listado, vacío, detalle y ausencia |
| SQLite | Archivos temporales reales | Mapeo, precisión, orden, ausencia y reset |
| API | FastAPI y SQLite de prueba | HTTP, contrato JSON y recorrido completo |
| Cliente HTTP | fetch controlado | Respuestas, errores y formato JSON |
| Pantalla | DOM y fetch controlado | Pedidos, carga, vacío, error y reintento |

Los datos son deterministas. pytest guarda sus bases temporales dentro del
proyecto. Los tests frontend limpian DOM y mocks al terminar; consultan roles,
nombres y resultados visibles. No sustituyen el hook ni el cliente HTTP.
TypeScript estricto comprueba fuente, tests y configuración. El build ejecuta
también typecheck. Las pruebas no sustituyen la revisión visual de la pantalla.

Las dependencias backend comprobadas están fijadas en requirements-dev.lock;
las frontend en package-lock.json. Los comandos de preparación, reset,
arranque y verificación están en README.md. AGENTS.md resume cómo trabajar.
