# USO

## Requisitos

- Python 3.8+
- `uvicorn`
- `docker` y `docker-compose` (si se utiliza Docker)
- Las dependencias listadas en `requirements.txt`

## Instalación

Para configurar el entorno virtual y las dependencias necesarias:

```bash
make install
```

Esto crea un entorno virtual, lo activa e instala los paquetes definidos en `requirements.txt`.

<br>

## Comandos disponibles

<br>

### Ejecutar la aplicación

Para iniciar el servidor FastAPI localmente, ejecuta el siguiente comando:

```bash
make run
```

Esto inicia `uvicorn` en el host `0.0.0.0` y el puerto `8000` con el recargado automático activado.

<br>

### Ejecutar las pruebas

Puedes correr todas las pruebas definidas utilizando pytest con el siguiente comando:

```bash
make test
```

<br>

### Docker

Para levantar la aplicación dentro de un contenedor Docker, usa:

```bash
make docker-up
```

Esto construirá la imagen de Docker y lanzará los servicios definidos en el archivo `docker-compose.yml`.

Para detener y eliminar los contenedores, usa:

```bash
make docker-down
```

<br>

### Limpiar archivos temporales

Puedes eliminar los archivos compilados de Python y las carpetas `__pycache__` con el siguiente comando:

```bash
make clean
```

### Abrir documentacion Swagger

Para abrir automáticamente la documentación de Swagger generada por FastAPI en localhost:8000/docs.

```bash
make open-docs
```