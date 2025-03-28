# Lab01-Inkafarma-Software

## Descripción

Este proyecto es una aplicación web desarrollada con FastAPI que integra un sistema de mensajería asíncrona mediante RabbitMQ. La aplicación ofrece endpoints para autenticación, gestión de productos, manejo de stock, procesamiento de órdenes, pagos y fidelidad de clientes.

Este documento explica cómo levantar el servicio de RabbitMQ utilizando Docker y, a continuación, ejecutar la aplicación FastAPI con Uvicorn.

## Requisitos

- [Docker](https://www.docker.com/) instalado.
- Python 3.8 o superior.
- (Opcional) Git para clonar el repositorio.

## Instalación y Configuración

### 1. Clonar el Repositorio

Si aún no tienes el proyecto en tu máquina, clónalo desde GitHub:

```bash
git clone https://github.com/tu_usuario/Lab01-Inkafarma-Software.git
cd Lab01-Inkafarma-Software


### 2. Configurar el Entorno Virtual

Es recomendable usar un entorno virtual para gestionar las dependencias del proyecto.

1. Crear el entorno virtual:
   ```bash
   python -m venv venv
   ```
2. Activar el entorno virtual:
   - En Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - En macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
3. Actualizar `pip` e instalar las dependencias:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

> **Nota:** Asegúrate de que el archivo `requirements.txt` incluya las dependencias necesarias, como `fastapi`, `uvicorn`, `pika` y `redis` (si se utiliza).

## Levantar RabbitMQ con Docker

Para activar RabbitMQ, utiliza el siguiente comando en la terminal:

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

- **Descripción:**
  - `-d`: Ejecuta el contenedor en segundo plano.
  - `--name rabbitmq`: Asigna el nombre "rabbitmq" al contenedor.
  - `-p 5672:5672`: Mapea el puerto 5672 para conexiones AMQP.
  - `-p 15672:15672`: Mapea el puerto 15672 para la interfaz de administración.
  - `rabbitmq:3-management`: Utiliza la imagen con la interfaz de administración habilitada.

Una vez iniciado, podrás acceder a la interfaz de administración en [http://localhost:15672](http://localhost:15672) usando:
- Usuario: `guest`
- Contraseña: `guest`

## Ejecutar la Aplicación FastAPI

Con RabbitMQ corriendo, puedes iniciar la aplicación FastAPI:

1. Asegúrate de que tu archivo principal (por ejemplo, `main.py`) contiene la instancia de FastAPI nombrada como `app`.

2. Ejecuta Uvicorn con el siguiente comando:
   ```bash
   uvicorn main:app --reload
   ```
   - La opción `--reload` permite que la aplicación se recargue automáticamente al detectar cambios en el código (ideal para desarrollo).

La aplicación estará disponible en [http://localhost:8000](http://localhost:8000) y podrás consultar la documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs).

## Uso y Mantenimiento

- **Detener RabbitMQ:**  
  Para detener el contenedor RabbitMQ, utiliza:
  ```bash
  docker stop rabbitmq
  ```
  Y, si deseas eliminarlo:
  ```bash
  docker rm rabbitmq
  ```

- **Actualización de la Aplicación:**  
  Cada vez que realices cambios en el código, guarda los cambios, realiza commit y, si es necesario, reinicia Uvicorn (con `--reload` en desarrollo se actualiza automáticamente).

## Contribuciones



```
