import os
import subprocess
import time
import requests

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTPUT_DIR = os.path.abspath("capturas")
BASE_URL = "http://localhost:5000"


def esperar_servidor():
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=1)
            if r.status_code == 200:
                print("Servidor Flask en línea y respondiendo.")
                return True
        except Exception:
            time.sleep(0.5)
    return False


def tomar_captura_edge(url, filename, window_size="1280,900", delay=1.0):
    time.sleep(delay)
    out_path = os.path.join(OUTPUT_DIR, filename)
    cmd = [
        EDGE_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={window_size}",
        f"--screenshot={out_path}",
        url,
    ]
    subprocess.run(cmd, check=True)
    print(f"Captura guardada: {filename}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Captura de terminal CI/CD (Pytest + Ruff)
    report_file = os.path.abspath("capturas/reporte_tests_ci.html")
    tomar_captura_edge(f"file:///{report_file}", "captura_01_ci_cd_tests_ruff.png", window_size="1050,750", delay=0.5)

    if not esperar_servidor():
        print("Error: El servidor no respondió a tiempo.")
        return

    # 2. Captura del Health Check de Render
    tomar_captura_edge(f"{BASE_URL}/health", "captura_02_health_check_render.png", window_size="1000,600", delay=0.5)

    # 3. Captura del Sprint Review Adaptado (Tab 1)
    tomar_captura_edge(f"{BASE_URL}/sprint-review?tab=tab-review", "captura_03_sprint_review_demos.png", window_size="1280,950", delay=1.2)

    # 4. Preparar estado Canary (20%) y simular transacción
    requests.post(f"{BASE_URL}/api/pagos-express/toggle", json={"rollout_pct": 20, "circuit_breaker": False})
    requests.post(
        f"{BASE_URL}/api/pagos-express?simulate_flags=canary",
        json={"user_id": "cliente_canary_01", "monto": 49.99, "item_id": "plan_pro_tbd"},
    )
    # Tomar captura de Liberación Segura Canary (Tab 2)
    tomar_captura_edge(f"{BASE_URL}/sprint-review?tab=tab-liberacion", "captura_04_pagos_express_canary_20.png", window_size="1280,1100", delay=1.2)

    # 5. Activar Kill Switch y capturar
    requests.post(f"{BASE_URL}/api/pagos-express/toggle", json={"circuit_breaker": True})
    tomar_captura_edge(f"{BASE_URL}/sprint-review?tab=tab-liberacion", "captura_05_kill_switch_emergencia.png", window_size="1280,1100", delay=1.2)

    # Restaurar estado saludable
    requests.post(f"{BASE_URL}/api/pagos-express/toggle", json={"rollout_pct": 20, "circuit_breaker": False})

    # 6. Captura de Retrospectiva Tablero Miro (Tab 3)
    tomar_captura_edge(f"{BASE_URL}/sprint-review?tab=tab-retro", "captura_06_sprint_retro_tablero.png", window_size="1280,1150", delay=1.2)

    # 7. Captura de Playbook v3.0 & Checklist Fase 1 (Tab 4)
    tomar_captura_edge(f"{BASE_URL}/sprint-review?tab=tab-playbook", "captura_07_checklist_fase1_playbook.png", window_size="1280,950", delay=1.2)

    print("Todas las capturas se generaron exitosamente.")


if __name__ == "__main__":
    main()
