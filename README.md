# El Switcher

Proyecto de ingenieria de Software 1 2024 - FAMAF UNC

## Estructura del proyecto

Esta detallada en [ARCHITECTURE.md](src/ARCHITECTURE.md)

## Comenzando 🚀

### Requisitos 📋

Para poder correr el proyecto necesitas tener instalado:
- [Docker](https://www.docker.com/)

Opcionalmente, si no queres usar Docker, necesitas tener instalado:
- [Python](https://www.python.org/downloads/)

### Instalación

#### Linux

1. Clonar el repositorio
```bash
git clone git@github.com:NoSeRecursaMas/switcher-backend.git
```

2. Ingresar al repositorio
```bash
cd switcher-backend
```

3. Ejecutar el script de instalación
```bash
make build-docker
```

4. Iniciar el contenedor
```bash
make run-docker
```

5. Acceder a la documentación de la aplicación en [localhost:8000/docs](http://localhost:8000/docs)

#### Windows

1. Clonar el repositorio
```bash
git clone git@github.com:NoSeRecursaMas/switcher-backend.git
```

2. Ingresar al repositorio
```bash
cd switcher-backend
```

3. Ejecutar el script de instalación
```bash
docker build -t backend .
```

4. Iniciar el contenedor
```bash
docker run -p 8000:80 -v .:/app backend
```

5. Acceder a la documentación de la aplicación en [localhost:8000/docs](http://localhost:8000/docs)

#### Sin Docker

1. Clonar el repositorio
```bash
git clone git@github.com:NoSeRecursaMas/switcher-backend.git
```

2. Ingresar al repositorio
```bash
cd switcher-backend
```

3. Instalar el entorno virtual y las dependencias
```bash
make install
```

4. Iniciar el servidor
```bash
make run
```

5. Acceder a la documentación de la aplicación en [localhost:8000/docs](http://localhost:8000/docs)

## Otras tareas

### Ejecutar las pruebas

Puedes correr todas las pruebas definidas utilizando pytest con el siguiente comando:

```bash
make test
```


### Limpiar archivos temporales

Puedes eliminar los archivos compilados de Python y las carpetas `__pycache__` con el siguiente comando:

```bash
make clean
```


### Abrir documentación Swagger

Para abrir automáticamente la documentación de Swagger generada por FastAPI en localhost:8000/docs.

```bash
make open-docs
```