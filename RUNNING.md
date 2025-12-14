# How to Run the Dual Chatbot System

You can run the system in two ways: **Locally** (for development) or using **Docker** (for containerized deployment).

## Option 1: Run Locally (Recommended for Dev)
We have provided a helper script to start both the FastAPI backend and Django frontend automatically.

1.  **Open the Project Folder** in File Explorer or VS Code.
2.  **Double-click** the `run_app.bat` file.
    *   *Alternatively, run `.\run_app.bat` in your terminal.*
3.  This will open:
    *   A window for **FastAPI** (Backend) at `http://127.0.0.1:8001`
    *   A window for **Django** (Frontend) at `http://127.0.0.1:8000`
4.  **Access the App**: Go to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Option 2: Run with Docker
If you prefer to run everything in containers (simulating production):

1.  **Build and Start**:
    ```bash
    docker-compose up --build
    ```
2.  **Access the App**:
    *   Frontend: [http://localhost:8000](http://localhost:8000)
    *   Backend: [http://localhost:8001](http://localhost:8001)

## Troubleshooting
- **"Chat service unavailable"**: behavior implies the Django app cannot talk to FastAPI.
    - Ensure the FastAPI window is open and says "Application startup complete".
    - If running via Docker, make sure `docker-compose` is running.
