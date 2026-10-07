# Trabajo en este repositorio

- Backend: `backend/src/orders_app/` contiene dominio, aplicación, SQLite y API.
  Frontend: `frontend/src/` contiene cliente HTTP, carga y componentes React.
- Inspecciona el código y sus tests antes de modificarlo; consulta `docs/architecture.md`.
- Mantén cambios pequeños y acotados. No cambies código no relacionado.
- Backend, desde `backend/`: `.venv/bin/python -m pytest`.
- Frontend, desde `frontend/`: `npm test`, `npm run typecheck` y `npm run build`.
- Ejecuta las pruebas relevantes; antes de cerrar, revisa `git diff` y `git status`.
  Si hay archivos nuevos sin seguimiento, revisa también su contenido.
- No añadas dependencias o abstracciones sin necesidad. No hagas commits salvo petición.
