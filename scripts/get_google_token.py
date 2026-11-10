"""Helper script to obtain and save Google Health API OAuth tokens into .env."""

import argparse
import http.server
import json
import socketserver
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
HEALTH_SCOPES = [
    "https://www.googleapis.com/auth/googlehealth.nutrition.writeonly",
    "https://www.googleapis.com/auth/googlehealth.sleep.readonly",
    "https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.readonly",
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
]
HEALTH_SCOPE_STR = " ".join(HEALTH_SCOPES)



def save_token_to_env(access_token: str, refresh_token: str = None) -> None:
    """Save or update tokens in the root .env file."""
    lines = []
    if ENV_PATH.exists():
        lines = [l for l in ENV_PATH.read_text(encoding="utf-8").splitlines() if not l.startswith("GOOGLE_HEALTH_")]

    lines.append(f"GOOGLE_HEALTH_ACCESS_TOKEN={access_token}")
    if refresh_token:
        lines.append(f"GOOGLE_HEALTH_REFRESH_TOKEN={refresh_token}")

    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n✅ Token guardado con éxito en: {ENV_PATH}")


def manual_paste_mode():
    print("\n" + "=" * 60)
    print("MÉTODO RÁPIDO: Google OAuth 2.0 Playground (1 minuto)")
    print("=" * 60)
    print("1. Abre en tu navegador:")
    print("   👉 https://developers.google.com/oauthplayground")
    print("\n2. En el panel izquierdo ('Step 1 Select & authorize APIs'):")
    print("   - Baja hasta la casilla 'Input your own scopes'")
    print("   - Pega estos scopes (separados por espacio):")
    print(f"     {HEALTH_SCOPE_STR}")
    print("   - Haz clic en el botón azul 'Authorize APIs'")
    print("   - Inicia sesión con tu cuenta de Google y concede los permisos")
    print("\n3. En 'Step 2 Exchange authorization code for tokens':")
    print("   - Haz clic en el botón azul 'Exchange authorization code for tokens'")
    print("   - Copia el valor del campo 'Access token' (empieza por 'ya29...')")
    print("=" * 60)

    token = input("\nPega aquí tu Access Token: ").strip()
    if not token:
        print("❌ Token vacío. Operación cancelada.")
        return

    save_token_to_env(token)


def oauth_browser_flow(client_id: str, client_secret: str, port: int = 8080):
    redirect_uri = f"http://localhost:{port}/callback"
    auth_code = None

    class OAuthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<h1>Autenticacion completada con exito</h1><p>Puedes cerrar esta pestana y volver a la terminal.</p>")
            else:
                self.send_response(400)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": HEALTH_SCOPE_STR,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    print(f"\nAbriendo navegador para autorización...\nURL: {url}")
    webbrowser.open(url)

    with socketserver.TCPServer(("localhost", port), OAuthHandler) as httpd:
        print(f"Esperando respuesta de Google en {redirect_uri}...")
        httpd.handle_request()

    if not auth_code:
        print("❌ No se recibió el código de autorización.")
        return

    print("Intercambiando código por tokens...")
    token_payload = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode("utf-8")

    req = urllib.request.Request(GOOGLE_TOKEN_URL, data=token_payload, method="POST")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    if access_token:
        save_token_to_env(access_token, refresh_token)
    else:
        print("❌ Error al obtener access token:", data)


def main():
    import os
    from src.config import settings

    parser = argparse.ArgumentParser(description="Obtain Google Health API OAuth access token")
    parser.add_argument("--client-id", help="Google Cloud OAuth Client ID")
    parser.add_argument("--client-secret", help="Google Cloud OAuth Client Secret")
    parser.add_argument("--manual", action="store_true", help="Force manual token paste mode")
    args = parser.parse_args()

    client_id = args.client_id or settings.google_client_id or os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = args.client_secret or settings.google_client_secret or os.environ.get("GOOGLE_CLIENT_SECRET")

    if not args.manual and client_id and client_secret:
        oauth_browser_flow(client_id, client_secret)
    else:
        manual_paste_mode()


if __name__ == "__main__":
    main()

