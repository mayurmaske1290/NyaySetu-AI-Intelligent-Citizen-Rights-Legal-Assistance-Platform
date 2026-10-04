# NyaySetu AI — Implementation Status

## Current build target
- Android: Kotlin + Jetpack Compose + Room + ML Kit + Fused Location Provider
- Backend: FastAPI + demo AI/RAG/authority providers
- Gradle: 8.9
- Gradle JVM: use JDK 21

## Implemented in this pass
- Text input with automatic focus/keyboard
- Voice input with microphone permission and error recovery
- Camera capture with camera permission and OCR
- File/share import for images and text; imported evidence is copied to the local evidence vault
- SHA-256 hashing with persistent local file path
- Evidence delete action
- Evidence gap detector endpoint integration with local evidence context
- Incident timeline endpoint integration
- Evidence-to-claim mapping endpoint integration
- Action Safety / Pause & Verify endpoint integration
- Complaint generation endpoint integration
- Complaint editing, copy, share, and PDF export
- Trusted contact save/edit/enable and explicit SMS hand-off
- Location permission and nearby-authority lookup
- Official-site and map hand-off for authority entries
- Configurable backend URL for physical-device testing
- Local incident status controls
- Offline rights screen
- Demo fallback remains available when backend is unavailable

## Backend verification
`pytest -q` → 18 passed.

## Physical-device backend configuration
The emulator can use `http://10.0.2.2:8000/` to reach a backend running on the host computer.
For a physical phone, open **Settings → Backend connection** inside NyaySetu AI and enter the computer's LAN address, for example:

`http://192.168.1.5:8000/`

The computer firewall must allow inbound TCP traffic to port 8000 and the backend should listen on `0.0.0.0` for LAN access.

## Important demo-data boundary
The bundled legal knowledge and authority entries are demo data. They must be replaced or verified against official sources before production/legal reliance.
