import os
import subprocess
import sys
import time

server = subprocess.Popen([sys.executable, "src/app.py"], env=dict(os.environ, PORT="5000"))
try:
    time.sleep(2)
    subprocess.run([sys.executable, "capturas/tomar_capturas.py"], check=True)
finally:
    server.terminate()
    try:
        server.wait(timeout=3)
    except Exception:
        server.kill()
print("Proceso de generacion de capturas finalizado.")
