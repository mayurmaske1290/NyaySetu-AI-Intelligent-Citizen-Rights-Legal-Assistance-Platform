NyaySetu AI — Final Batch

Previously reported source errors fixed:
- Gradle build.gradle.kts API URL quoting
- BackendClient expression-body return
- BackendClient missing closing brace
- App.kt bitmapBytes helper
- App.kt FocusRequester imports/usage

Core batch fixes included:
- Type input focus/keyboard
- Camera permission and OCR
- File/share import and local evidence storage
- SHA-256 evidence hashing
- Evidence gap/timeline/claim/safety/complaint flows
- Complaint sharing/PDF export
- Trusted contact settings and SMS hand-off
- Location/authority lookup and Maps/web hand-off
- Configurable backend URL for physical devices
- Speech error recovery
- Offline guidance and demo fallback

Build on the user's Android Studio/SDK environment:
1. Open this folder: android/
2. Use Gradle JVM 21.
3. Let Gradle Sync finish.
4. Build > Assemble Project.
5. Only after BUILD SUCCESSFUL, install/run on the phone.

Note: this environment cannot run the Android Gradle build because it does not have the user's Android SDK/Gradle cache. Therefore the final device build must be verified in Android Studio.
