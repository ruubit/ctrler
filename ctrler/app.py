import secrets
from pathlib import Path

import qrcode
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ctrler.remote_controller import RemoteController


class RemoteControllerApp:
    """Remote controller app that handles the startup and API of the remote controller."""

    def __init__(self, local_ip: str, port: int = 8000) -> None:
        """Instantiates a `RemoteControllerApp`.

        Parameters
        ----------
        local_ip : str
            Local ip address to bind the service to.
        port : int, optional
            Port to listen to, by default 8000.
        """
        self.port = port
        self.local_ip = local_ip
        self.session_token = self._generate_session_token()
        self.service_url = self._generate_service_url()

    def run(self) -> None:
        """Run the app."""
        qr = self._create_qr_code()
        self._show_start_up_message(qr)
        app = self._create_app()
        uvicorn.run(app=app, host=self.local_ip, port=self.port)

    def _generate_session_token(self) -> str:
        """Generate a session token."""
        return secrets.token_urlsafe()

    def _generate_service_url(self) -> str:
        """Generate the URL to access the remote controller."""
        return f"http://{self.local_ip}:{self.port}#token={self.session_token}"

    def _create_qr_code(self) -> qrcode.QRCode:
        """Creates a QR code that embeds the service URL."""
        qr = qrcode.QRCode()
        qr.add_data(self.service_url)
        qr.make(fit=True)
        return qr

    def _show_start_up_message(self, qr_code: qrcode.QRCode) -> None:
        """Prints a start up message and the QR code."""
        banner = """

        ======================================
                        CTRLER
        ======================================

        Scan the QR code below with your 
        phone to access the remote 
        controller.

        ⚠️  WARNING: Do not share the token, the URL 
        or the QR code with anyone. Anyone with access 
        to your local network and the session token can 
        control video playback while the app is running. 
        """
        print(banner)
        qr_code.print_ascii()

    def _create_app(self) -> FastAPI:
        """Creates the FastAPI app."""

        frontend_path = Path(__file__).parent / "frontend"
        app = FastAPI()
        app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")
        remote_controller = RemoteController()

        class Action(BaseModel):
            action: str

        security = HTTPBearer()

        @app.get("/")
        def read_index():
            return FileResponse(frontend_path / "index.html")

        @app.post("/api/action")
        def action(
            action: Action,
            credentials: HTTPAuthorizationCredentials = Depends(security),
        ):
            if not secrets.compare_digest(credentials.credentials, self.session_token):
                raise HTTPException(
                    status_code=401, detail="Not authorized to control the remote."
                )
            action_name = action.action
            if action_name not in remote_controller.allowed_actions:
                raise HTTPException(
                    status_code=400, detail=f"{action_name} is not a valid action."
                )
            try:
                remote_controller.execute_action(action_name)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Executing action {action_name} failed."
                ) from e
            return {"status": "success", "action": action_name}

        return app
