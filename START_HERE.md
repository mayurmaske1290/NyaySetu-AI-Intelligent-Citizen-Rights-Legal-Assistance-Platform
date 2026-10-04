# NyaySetu AI — fixed runnable build

## 1. Start the backend on Windows

Open PowerShell in this project folder and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\scripts\run_backend.ps1
```

The script creates a **Windows** backend virtual environment under `backend\.venv`, installs the requirements, and starts:

`http://127.0.0.1:8000`

Check it from a second PowerShell window:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/health" | ConvertTo-Json
```

## 2. Configure real AI

Create `backend\.env` from `backend\.env.example` and put your own OpenRouter key in `LLM_API_KEY`.

`DEMO_MODE=false` is the default. If the key is missing, the API returns a clear configuration error instead of silently pretending the result is real AI.

**Do not share your API key or commit `backend\.env`.**

## 3. Android connection

- Android Emulator: `http://10.0.2.2:8000`
- Physical phone: use the PC's LAN address, e.g. `http://192.168.1.5:8000`

The app has this under **Settings → Backend connection**.

For a physical phone, allow Python through Windows Firewall on private networks if Android cannot connect.

## 4. What was fixed

- Restored the missing `BackendClient.kt`.
- Removed the duplicate `ShareBus` declaration.
- Fixed the Compose `background` import/build errors.
- Fixed the Compose `Text` argument ordering error.
- Fixed the text-field state bug that caused the cursor to flicker/reset while typing.
- Camera/gallery OCR now updates the visible input field.
- Backend errors are surfaced to the app instead of showing an empty result.
- Complaint draft response fields are mapped correctly.
- Backend launcher uses the correct module: `app.main:app` from the `backend` directory.
- Backend no longer silently switches to demo AI when the API key is absent.
- OpenAI-compatible calls retry without `response_format` when a model rejects that option.
- Added a generic JSON error handler for unexpected backend failures.
- Removed duplicate Android permissions.
- Refreshed the home screen with a premium card/gradient layout.
