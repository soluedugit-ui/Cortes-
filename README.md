# Optimizador de cortes

Web para planear cortes de material y reducir el desperdicio en la fábrica.

**Estado actual (MVP):** corte lineal 1D (tubos, perfiles, barras, listones) con sierra.

- **Backend:** FastAPI + optimizador en Python con ancho de sierra: modo rápido (heurística Best Fit Decreasing) y modo exacto (OR-Tools).
- **Frontend:** React + Vite. Formulario de piezas y barras, resumen de desperdicio y diagrama del plan de cortes (imprimible).

## Cómo arrancar

Backend (terminal 1):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173. La documentación automática de la API está en http://localhost:8000/docs.

Pruebas del optimizador:

```bash
cd backend
pytest
```

## Publicarlo en internet (gratis, en Render)

La app se publica como **un solo servicio**: FastAPI sirve también el frontend ya compilado (el `Dockerfile` hace todo).

1. **Cuentas de la empresa.** Crea el repositorio en GitHub y la cuenta de Render con un correo de la empresa (no personal), para que nunca dependa de una sola persona.
2. **Sube el proyecto a GitHub** (la carpeta `optimizador-cortes` completa, con `Dockerfile` y `render.yaml` en la raíz).
3. En [render.com](https://render.com): **New → Blueprint**, elige el repositorio y confirma. Render lee `render.yaml`, construye el contenedor con el plan gratuito y te da una dirección pública tipo `https://optimizador-cortes.onrender.com`.
4. A partir de ahí, cada cambio que subas a GitHub se publica solo.

Cosas que debes saber del plan gratuito (verifica las condiciones actuales en Render antes de publicar, cambian con el tiempo):

- El servicio **se duerme tras un rato sin visitas**. La primera visita después tarda hasta aproximadamente un minuto. La web muestra un aviso mientras espera.
- Hay límites de horas/recursos. Para uso ligero (unas 500 piezas al día) alcanza de sobra.
- Si algún día la herramienta pasa a ser crítica, el plan de pago básico elimina la espera.

Cualquier otro hosting que ejecute contenedores Docker (Railway, Fly.io, etc.) funciona con el mismo `Dockerfile`.

### Protecciones incluidas

- Máximo **1000 piezas**, 30 tipos de pieza y 10 tipos de barra por cálculo.
- El modo exacto tiene un máximo de **20 s** y solo corre **un cálculo exacto a la vez** (el resto recibe "servidor ocupado").
- Tope de **30 peticiones por minuto por visitante** (configurable con la variable `RATE_LIMIT_PER_MIN`).
- Los límites de tamaño están al inicio de `backend/app/schemas.py`.

### Variables de entorno (opcionales)

| Variable | Para qué sirve | Por defecto |
|---|---|---|
| `RATE_LIMIT_PER_MIN` | Peticiones por minuto por visitante | 30 |
| `CORS_ORIGINS` | Dominios permitidos si el frontend se sirve aparte | localhost:5173 |
| `STATIC_DIR` | Carpeta del frontend compilado | `backend/static` |

### Mantenimiento

- Las versiones de las librerías están fijadas en `backend/requirements.txt` para que una actualización externa no rompa la página sin aviso.
- Si el dominio es propio, activa la renovación automática.
- Para ver si la app está viva: `https://TU-DIRECCIÓN/api/health` debe responder `{"status":"ok"}`.
- Si se cae, en el panel de Render se ven los registros (*Logs*) y el botón *Manual Deploy → Deploy latest commit* la vuelve a levantar.

## Cómo se calcula el ancho de corte

Una barra con `n` piezas necesita `n - 1` cortes entre piezas:

```
requerido = suma(piezas) + ancho_sierra * (n - 1)
sobrante  = largo_barra - requerido
```

El resultado separa el desperdicio en **pérdida por sierra** y **sobrantes**. Usa la misma unidad en todo (por ejemplo mm).

## Modos de cálculo

- **Rápido:** heurística Best Fit Decreasing. Responde al instante.
- **Exacto (OR-Tools):** modelo CP-SAT que minimiza el largo total de barras. Dice si el resultado es óptimo demostrado y nunca devuelve algo peor que el modo rápido. Tiene un tiempo máximo (10 s por defecto).

Para comparar ambos modos con varios casos de prueba:

```bash
cd backend
python compare.py
```

## Limitaciones conocidas

- El modo rápido, al abrir una barra nueva, usa la más corta donde quepa la pieza; con stock limitado puede quedar lejos del óptimo (el modo exacto lo corrige).
- En pedidos muy grandes el modo exacto puede agotar el tiempo y devolver "mejor encontrado" en vez de óptimo demostrado.
- No hay inventario de sobrantes reutilizables ni guardado de trabajos (no hay base de datos todavía).
- La web es pública y sin inicio de sesión: sirve para calcular, pero si se agrega inventario o historial habrá que añadir usuarios.
- El `Dockerfile` no pudo probarse construyendo la imagen en el entorno donde se desarrolló; sí se probó el mismo empaquetado a mano (frontend compilado servido por FastAPI).
- Solo 1D. Las láminas de metal (2D) quedan para la siguiente etapa.

## Próximos pasos sugeridos

1. **Probar con una orden real** de la fábrica y comparar contra cómo se corta hoy (medir el desperdicio actual para demostrar el ahorro).
2. **Inventario de retales**: reutilizar sobrantes guardados antes de abrir barras nuevas.
3. **Cargar piezas desde Excel/CSV** y exportar el plan a PDF.
4. **Láminas (2D):** `rectpack` o un enfoque guillotina; considerar cizalla/plasma según cómo se corte.
5. **Base de datos** (PostgreSQL) para historial, usuarios y reportes.
