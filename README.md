# NyaySetu AI

**Know Your Rights. Protect Your Evidence. Take the Right Next Step.**

NyaySetu AI is a phone-native AI rights and evidence protection assistant. It is informational assistance, not legal advice.

## Current implementation

### Android
- Jetpack Compose Material 3 UI
- Home with six situation categories
- Text analysis flow
- Voice input using Android SpeechRecognizer
- Camera capture + ML Kit OCR
- File/share import and local evidence capture
- Room database for incidents and evidence
- SHA-256 integrity hashes
- Incident history
- Evidence Vault
- Live Situation Mode
- Offline guidance
- Complaint draft/edit/share
- Legitimate-help demo directory
- Privacy/settings and local-data deletion
- Backend connection with safe demo fallback

### Backend
- FastAPI API surface
- Structured Pydantic AI response
- Configurable AI provider abstraction
- Demo AI provider
- Demo RAG knowledge base
- Evidence gap, timeline, claims, complaint and authority services
- Controlled errors and validation
- Test suite

## Run backend

```bash
cd backend
python -m venv .venv
# activate the environment
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Android

Open the `android/` folder in Android Studio with a recent Android Studio release and allow Gradle to sync. The app is configured for emulator backend access at `http://10.0.2.2:8000/`.

For a physical phone, set the `API_BASE_URL` build config to the computer's LAN address, for example `http://192.168.1.10:8000/`, and ensure the backend is reachable from the phone.

Google Maps is optional in the current demo build; authority entries are explicitly labelled demo data until verified.

## Demo flow

1. Open the app.
2. Choose **Scam**, **Traffic Stop**, **Bribe Demand**, **Threat / Harassment**, **Legal Notice**, or **Other**.
3. Describe an incident or use Speak/Camera/Share.
4. Review OCR text if camera input is used.
5. Tap **Analyze safely**.
6. Review rights, warnings, next steps, evidence hints and gaps.
7. Save/view evidence in Evidence Vault.
8. Open Live Situation Mode.
9. Generate and edit a complaint draft.
10. Review legitimate-help demo entries.

## Important safety boundary

Demo legal knowledge and authority entries are clearly marked. The app must not fabricate laws, legal sections, penalties, government contacts or complaint URLs. Never auto-submit a complaint, secretly record, secretly track or secretly share.

## Physical Android Phone — Backend Connection

If NyaySetu AI is installed on a real Android phone and the FastAPI backend runs on your computer, do not use `10.0.2.2`. In the app open **Settings → Backend connection** and enter the computer's LAN IP, for example `http://192.168.1.5:8000/`. Run the backend on `0.0.0.0:8000` and allow port 8000 through the computer firewall. If the backend is unreachable, the app safely falls back to clearly labeled demo guidance.
