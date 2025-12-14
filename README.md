# DinoJumper

Juego estilo Chrome Dino controlado con la cámara usando MediaPipe Pose. Salta o agáchate moviendo la cabeza; reinicia levantando la mano cuando pierdes..

## Requisitos

- Python 3.13
- Pygame, OpenCV, MediaPipe (instalar con `pip install -r requirements.txt`)
- Cámara web activa

## Instalación rápida

```pwsh
cd "directorio"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecución

```pwsh
python .\main.py
```

## Controles (seguimiento corporal)

- Cabeza por encima de la línea verde: salto.
- Cabeza por debajo de la línea roja: agachado.
- Mano por encima de la línea morada (solo en game over): reinicio.

## Notas

- Mantén buena iluminación para que MediaPipe detecte el cuerpo con precisión.
- El juego alterna entre día y noche automáticamente según tu puntuación.
