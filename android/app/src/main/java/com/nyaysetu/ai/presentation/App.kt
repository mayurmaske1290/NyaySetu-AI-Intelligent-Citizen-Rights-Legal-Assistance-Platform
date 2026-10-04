package com.nyaysetu.ai.presentation

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.pdf.PdfDocument
import android.net.Uri
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.android.gms.location.LocationServices
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.nyaysetu.ai.BuildConfig
import com.nyaysetu.ai.core.FileHasher
import com.nyaysetu.ai.core.IncidentIds
import com.nyaysetu.ai.data.*
import com.nyaysetu.ai.domain.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.io.File
import java.io.FileOutputStream
import java.util.Locale

private val Navy = Color(0xFF071A2B)
private val Teal = Color(0xFF0E7490)
private val Background = Color(0xFFF5F8FB)
private val TextDark = Color(0xFF102033)
private val TextMuted = Color(0xFF65758B)
private val Danger = Color(0xFFDC2626)


data class UiState(
    val screen: String = "home",
    val input: String = "",
    val loading: Boolean = false,
    val analysis: Analysis? = null,
    val incidentId: String? = null,
    val error: String? = null,
    val gaps: GapResult? = null,
    val timeline: List<TimelineEvent> = emptyList(),
    val claims: List<ClaimLink> = emptyList(),
    val safety: ActionSafety? = null,
    val complaint: ComplaintDraft? = null,
    val authorities: List<AuthorityItem> = emptyList(),
    val locationText: String = "",
    val locationLat: Double? = null,
    val locationLng: Double? = null,
    val backendUrl: String = BuildConfig.API_BASE_URL
)

class NyayViewModel(private val context: Context) : ViewModel() {
    private val db = AppDatabase.create(context)
    private val prefs = context.getSharedPreferences("nyaysetu_settings", Context.MODE_PRIVATE)
    private val backend = BackendClient(
        prefs.getString("backend_url", BuildConfig.API_BASE_URL) ?: BuildConfig.API_BASE_URL
    )

    private val _state = MutableStateFlow(UiState(backendUrl = backend.getBaseUrl()))
    val state = _state.asStateFlow()

    val incidents = db.incidents().observeAll().stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        emptyList()
    )

    val evidence = db.evidence().observeAll().stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        emptyList()
    )

    fun setScreen(screen: String) = _state.update { it.copy(screen = screen, error = null) }

    fun setInput(value: String) = _state.update { it.copy(input = value) }

    fun setBackendUrl(url: String) {
        val normalized = url.trim().let { if (it.endsWith('/')) it else "$it/" }
        prefs.edit().putString("backend_url", normalized).apply()
        backend.setBaseUrl(normalized)
        _state.update { it.copy(backendUrl = normalized, error = null) }
    }

    private fun ensureIncident(): String {
        state.value.incidentId?.let { return it }
        val id = IncidentIds.create()
        db.incidents().insert(
            IncidentEntity(
                id = id,
                title = "NyaySetu incident",
                category = "OTHER",
                severity = "LOW",
                summary = state.value.input.take(400)
            )
        )
        _state.update { it.copy(incidentId = id) }
        return id
    }

    fun analyze(categoryHint: String? = null) {
        val text = state.value.input.trim()
        if (text.isBlank()) {
            _state.update { it.copy(error = "Describe what happened first.") }
            return
        }

        val incidentId = ensureIncident()
        _state.update { it.copy(loading = true, error = null) }

        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                backend.analyze(text, "en", categoryHint)
                    ?: error("Backend analysis failed. Check the backend URL and server logs.")
            }.onSuccess { result ->
                db.incidents().insert(
                    IncidentEntity(
                        id = incidentId,
                        title = result.summary.take(72).ifBlank { "NyaySetu analysis" },
                        category = result.primaryCategory,
                        severity = result.severity,
                        summary = result.summary
                    )
                )
                _state.update {
                    it.copy(
                        loading = false,
                        analysis = result,
                        incidentId = incidentId,
                        screen = "result",
                        error = null
                    )
                }
            }.onFailure { error ->
                _state.update {
                    it.copy(
                        loading = false,
                        error = error.message ?: "Backend analysis failed."
                    )
                }
            }
        }
    }

    fun saveEvidence(name: String, type: String, bytes: ByteArray, note: String = "") {
        val incidentId = ensureIncident()
        viewModelScope.launch(Dispatchers.IO) {
            runCatching {
                val hash = FileHasher.sha256(bytes)
                val dir = File(context.filesDir, "evidence/$incidentId").apply { mkdirs() }
                val safeName = name.replace(Regex("[^A-Za-z0-9._-]"), "_").ifBlank { "evidence.bin" }
                val file = File(dir, "${hash.take(12)}_$safeName")
                file.writeBytes(bytes)
                db.evidence().insert(
                    EvidenceEntity(
                        id = IncidentIds.create(),
                        incidentId = incidentId,
                        name = safeName,
                        type = type,
                        hash = hash,
                        localPath = file.absolutePath,
                        createdAt = System.currentTimeMillis(),
                        note = note
                    )
                )
            }
        }
    }

    fun deleteEvidence(item: EvidenceEntity) {
        viewModelScope.launch(Dispatchers.IO) {
            runCatching { if (item.localPath.isNotBlank()) File(item.localPath).delete() }
            db.evidence().delete(item)
        }
    }

    fun clearData() {
        viewModelScope.launch(Dispatchers.IO) {
            db.incidents().deleteAll()
            db.evidence().deleteAll()
            prefs.edit()
                .remove("trusted_name")
                .remove("trusted_phone")
                .remove("trusted_enabled")
                .apply()
        }
    }

    fun updateStatus(id: String, status: String) = viewModelScope.launch(Dispatchers.IO) {
        db.incidents().updateStatus(id, status)
    }

    fun loadGaps() {
        val current = state.value
        val analysis = current.analysis ?: return
        viewModelScope.launch(Dispatchers.IO) {
            val result = backend.evidenceGaps(current.input, analysis.primaryCategory, evidence.value)
            _state.update {
                it.copy(
                    gaps = result ?: GapResult(
                        evidence.value.map { item -> item.name },
                        analysis.evidenceGaps.map { gap -> gap.item },
                        listOf("Keep original files and timestamps unchanged.")
                    ),
                    screen = "gaps"
                )
            }
        }
    }

    fun loadTimeline() {
        val current = state.value
        viewModelScope.launch(Dispatchers.IO) {
            val result = backend.timeline(current.input, evidence.value)
            _state.update {
                it.copy(
                    timeline = result ?: listOf(
                        TimelineEvent(null, current.input.take(180), true)
                    ),
                    screen = "timeline"
                )
            }
        }
    }

    fun loadClaims() {
        val current = state.value
        viewModelScope.launch(Dispatchers.IO) {
            val result = backend.claims(current.input, evidence.value)
            _state.update {
                it.copy(
                    claims = result ?: emptyList(),
                    screen = "claims"
                )
            }
        }
    }

    fun checkSafety(planned: String) {
        if (planned.isBlank()) return
        val current = state.value
        viewModelScope.launch(Dispatchers.IO) {
            val result = backend.actionSafety(
                planned,
                current.input,
                current.analysis?.primaryCategory
            )
            _state.update {
                it.copy(
                    safety = result ?: ActionSafety(
                        planned,
                        "Pause before an irreversible, risky, or urgent action.",
                        "Verify through an official channel first."
                    ),
                    screen = "safety"
                )
            }
        }
    }

    fun generateComplaint() {
        val current = state.value
        viewModelScope.launch(Dispatchers.IO) {
            val result = backend.complaint(
                statement = current.input,
                category = current.analysis?.primaryCategory,
                evidenceNames = evidence.value.map { it.name },
                incidentId = current.incidentId,
                locationText = current.locationText
            )
            _state.update {
                it.copy(
                    complaint = result ?: ComplaintDraft(
                        "Incident report",
                        current.input.take(400),
                        "DRAFT FOR REVIEW\n\n${current.input}",
                        "Authority to be verified"
                    ),
                    screen = "complaint"
                )
            }
        }
    }

    fun loadAuthorities(lat: Double?, lng: Double?) {
        val category = state.value.analysis?.primaryCategory
        viewModelScope.launch(Dispatchers.IO) {
            val result = backend.authorities(lat, lng, category)
            _state.update {
                it.copy(
                    authorities = result ?: emptyList(),
                    locationLat = lat,
                    locationLng = lng,
                    locationText = if (lat != null && lng != null) {
                        "%.5f, %.5f".format(Locale.US, lat, lng)
                    } else {
                        "Location unavailable"
                    },
                    screen = "help"
                )
            }
        }
    }

    fun setLocation(lat: Double, lng: Double) {
        _state.update {
            it.copy(
                locationLat = lat,
                locationLng = lng,
                locationText = "%.5f, %.5f".format(Locale.US, lat, lng)
            )
        }
    }

    fun trustedName(): String = prefs.getString("trusted_name", "") ?: ""
    fun trustedPhone(): String = prefs.getString("trusted_phone", "") ?: ""
    fun trustedEnabled(): Boolean = prefs.getBoolean("trusted_enabled", false)

    fun saveTrusted(name: String, phone: String, enabled: Boolean) {
        prefs.edit()
            .putString("trusted_name", name.trim())
            .putString("trusted_phone", phone.trim())
            .putBoolean("trusted_enabled", enabled)
            .apply()
    }
}

@Composable
fun NyayApp() {
    val context = LocalContext.current
    val vm = remember { NyayViewModel(context) }
    val state by vm.state.collectAsState()
    val incidents by vm.incidents.collectAsState()
    val evidence by vm.evidence.collectAsState()
    val shared by ShareBus.events.collectAsState()

    LaunchedEffect(shared) {
        shared?.let { event ->
            event.first?.takeIf { it.isNotBlank() }?.let(vm::setInput)
            event.second.firstOrNull()?.let { uri ->
                processUri(context, uri, vm) {}
            }
            if (event.first?.isNotBlank() == true || event.second.isNotEmpty()) {
                vm.setScreen("input")
            }
            ShareBus.clear()
        }
    }

    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Teal,
            secondary = Color(0xFF0F766E),
            background = Background,
            surface = Color.White,
            onBackground = TextDark,
            onSurface = TextDark,
            error = Danger
        )
    ) {
        Surface(Modifier.fillMaxSize()) {
            when (state.screen) {
                "home" -> Home(vm)
                "input" -> InputScreen(vm, state)
                "result" -> ResultScreen(vm, state)
                "vault" -> Vault(vm, evidence)
                "history" -> History(vm, incidents)
                "live" -> LiveScreen(vm, state)
                "help" -> HelpScreen(vm, state)
                "settings" -> SettingsScreen(vm, state)
                "complaint" -> ComplaintScreen(vm, state)
                "offline" -> OfflineScreen(vm)
                "timeline" -> TimelineScreen(vm, state)
                "claims" -> ClaimsScreen(vm, state)
                "safety" -> SafetyScreen(vm, state)
                "gaps" -> GapsScreen(vm, state)
                else -> Home(vm)
            }
        }
    }
}

@Composable
private fun Shell(title: String, onBack: () -> Unit, content: @Composable ColumnScope.() -> Unit) {
    Column(
        Modifier
            .fillMaxSize()
            .background(Background)
            .padding(18.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) {
                Icon(Icons.Default.ArrowBack, "Back")
            }
            Text(title, fontSize = 24.sp, fontWeight = FontWeight.Bold)
        }
        Spacer(Modifier.height(10.dp))
        Column(
            Modifier
                .weight(1f)
                .verticalScroll(rememberScrollState()),
            content = content
        )
    }
}

@Composable
private fun Home(vm: NyayViewModel) {
    Column(
        Modifier
            .fillMaxSize()
            .background(Background)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 24.dp)
    ) {
        Box(
            Modifier
                .fillMaxWidth()
                .height(285.dp)
                .clip(RoundedCornerShape(bottomStart = 34.dp, bottomEnd = 34.dp))
                .background(
                    androidx.compose.ui.graphics.Brush.linearGradient(
                        listOf(Navy, Color(0xFF123B5D), Teal)
                    )
                )
        ) {
            Column(
                Modifier.fillMaxSize().padding(24.dp),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        shape = RoundedCornerShape(16.dp),
                        color = Color.White.copy(alpha = .14f)
                    ) {
                        Icon(Icons.Default.Shield, null, tint = Color.White, modifier = Modifier.padding(11.dp).size(27.dp))
                    }
                    Spacer(Modifier.width(12.dp))
                    Column {
                        Text("NyaySetu AI", color = Color.White, fontSize = 25.sp, fontWeight = FontWeight.ExtraBold)
                        Text("Your intelligent rights companion", color = Color.White.copy(alpha = .72f), fontSize = 12.sp)
                    }
                }
                Column {
                    Text("Understand.", color = Color.White, fontSize = 30.sp, fontWeight = FontWeight.ExtraBold)
                    Text("Protect. Act safely.", color = Color.White, fontSize = 30.sp, fontWeight = FontWeight.ExtraBold)
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "Describe what happened and get structured, safety-first guidance from your connected AI backend.",
                        color = Color.White.copy(alpha = .78f), fontSize = 13.sp
                    )
                }
            }
        }

        Column(Modifier.padding(horizontal = 20.dp)) {
            Spacer(Modifier.height(22.dp))
            Text("How can we help?", fontSize = 22.sp, fontWeight = FontWeight.Bold, color = TextDark)
            Text("Start with a description or choose a common situation", color = TextMuted, fontSize = 13.sp)
            Spacer(Modifier.height(16.dp))

            Card(
                onClick = { vm.setScreen("input") },
                shape = RoundedCornerShape(22.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(defaultElevation = 3.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(Modifier.padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
                    Surface(shape = RoundedCornerShape(15.dp), color = Color(0xFFE7F7F8)) {
                        Icon(Icons.Default.Edit, null, tint = Teal, modifier = Modifier.padding(12.dp).size(25.dp))
                    }
                    Spacer(Modifier.width(14.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Describe an incident", fontWeight = FontWeight.Bold, fontSize = 17.sp, color = TextDark)
                        Text("Explain the situation in your own words and analyze it with AI.", color = TextMuted, fontSize = 12.sp)
                    }
                    Icon(Icons.Default.ChevronRight, null, tint = TextMuted)
                }
            }

            Spacer(Modifier.height(12.dp))
            Card(
                onClick = { vm.setScreen("live") },
                shape = RoundedCornerShape(22.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFFFF5F5)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(Modifier.padding(18.dp), verticalAlignment = Alignment.CenterVertically) {
                    Surface(shape = RoundedCornerShape(15.dp), color = Color(0xFFFFE3E3)) {
                        Icon(Icons.Default.Warning, null, tint = Danger, modifier = Modifier.padding(12.dp).size(25.dp))
                    }
                    Spacer(Modifier.width(14.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Live situation mode", fontWeight = FontWeight.Bold, fontSize = 17.sp, color = TextDark)
                        Text("Quick safety guidance, emergency calling, location and trusted-contact tools.", color = TextMuted, fontSize = 12.sp)
                    }
                    Icon(Icons.Default.ChevronRight, null, tint = Danger)
                }
            }

            Spacer(Modifier.height(22.dp))
            Text("Popular situations", fontSize = 17.sp, fontWeight = FontWeight.Bold, color = TextDark)
            Spacer(Modifier.height(10.dp))
            val categories = listOf(
                "Traffic Stop" to "TRAFFIC_STOP",
                "Bribe Demand" to "BRIBE_DEMAND",
                "Scam / Fraud" to "SCAM",
                "Threat / Harassment" to "THREAT_HARASSMENT",
                "Legal Notice" to "LEGAL_NOTICE",
                "Other" to "OTHER"
            )
            categories.chunked(2).forEach { row ->
                Row(Modifier.fillMaxWidth()) {
                    row.forEach { (label, category) ->
                        Card(
                            onClick = { vm.setInput("I need help regarding a $label situation."); vm.setScreen("input") },
                            shape = RoundedCornerShape(18.dp),
                            modifier = Modifier.weight(1f).padding(4.dp),
                            colors = CardDefaults.cardColors(containerColor = Color.White)
                        ) {
                            Column(Modifier.padding(14.dp)) {
                                Text(label, fontWeight = FontWeight.SemiBold, color = TextDark)
                                Text(category.replace('_', ' '), color = TextMuted, fontSize = 10.sp)
                            }
                        }
                    }
                }
            }

            Spacer(Modifier.height(18.dp))
            Row(Modifier.fillMaxWidth()) {
                OutlinedButton({ vm.setScreen("vault") }, Modifier.weight(1f)) { Text("Evidence Vault") }
                Spacer(Modifier.width(8.dp))
                OutlinedButton({ vm.setScreen("help") }, Modifier.weight(1f)) { Text("Find Help") }
            }
            Row(Modifier.fillMaxWidth()) {
                TextButton({ vm.setScreen("history") }, Modifier.weight(1f)) { Text("History") }
                TextButton({ vm.setScreen("settings") }, Modifier.weight(1f)) { Text("Settings") }
            }
        }
    }
}

@Composable
private fun InputScreen(vm: NyayViewModel, state: UiState) {
    val context = LocalContext.current
    val keyboard = LocalSoftwareKeyboardController.current
    val focusRequester = remember { FocusRequester() }
    var text by remember { mutableStateOf(state.input) }

    LaunchedEffect(state.input) {
        if (state.input != text && text.isBlank()) text = state.input
    }
    var listening by remember { mutableStateOf(false) }
    var busy by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf<String?>(null) }

    fun updateText(value: String) {
        text = value
        vm.setInput(value)
    }

    val camera = rememberLauncherForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap: Bitmap? ->
        if (bitmap == null) {
            status = "No photo was captured."
            return@rememberLauncherForActivityResult
        }
        busy = true
        vm.saveEvidence(
            "camera_${System.currentTimeMillis()}.jpg",
            "image",
            bitmapBytes(bitmap),
            "Captured with NyaySetu camera"
        )
        TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
            .process(InputImage.fromBitmap(bitmap, 0))
            .addOnSuccessListener { result ->
                val extracted = result.text.trim()
                if (extracted.isNotBlank()) {
                    updateText(extracted)
                    status = "Text extracted from the image. Review it before analysis."
                } else {
                    status = "No readable text was found. You can still describe the incident manually."
                }
            }
            .addOnFailureListener { error ->
                status = "OCR failed: ${error.message ?: "unknown error"}."
            }
            .addOnCompleteListener { busy = false }
    }

    val micPermission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) {
            listening = true
            startSpeech(
                context,
                text,
                onText = {
                    updateText(it)
                    listening = false
                    status = "Speech captured. Review it before analysis."
                },
                onFinished = { listening = false }
            )
        } else {
            status = "Microphone permission was denied."
        }
    }

    val cameraPermission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) camera.launch(null) else status = "Camera permission was denied."
    }

    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        uri?.let { processUri(context, it, vm, onBusy = { busy = it }, onText = ::updateText) }
    }

    LaunchedEffect(Unit) {
        focusRequester.requestFocus()
        keyboard?.show()
    }

    Shell("Describe what happened", { keyboard?.hide(); vm.setScreen("home") }) {
        OutlinedTextField(
            value = text,
            onValueChange = ::updateText,
            modifier = Modifier.fillMaxWidth().height(190.dp).focusRequester(focusRequester),
            singleLine = false,
            placeholder = { Text("Describe what happened in your own words…") },
            trailingIcon = {
                if (text.isNotEmpty()) {
                    IconButton({ updateText("") }) { Icon(Icons.Default.Clear, "Clear") }
                }
            }
        )

        status?.let { Text(it, Modifier.padding(top = 8.dp), color = Teal) }
        state.error?.let { Text(it, Modifier.padding(top = 8.dp), color = MaterialTheme.colorScheme.error) }

        Spacer(Modifier.height(12.dp))
        Row(Modifier.fillMaxWidth()) {
            Button({ micPermission.launch(Manifest.permission.RECORD_AUDIO) }, Modifier.weight(1f), enabled = !busy) {
                Icon(Icons.Default.Mic, null)
                Text(if (listening) " Listening…" else " Speak")
            }
            Spacer(Modifier.width(6.dp))
            Button({ cameraPermission.launch(Manifest.permission.CAMERA) }, Modifier.weight(1f), enabled = !listening) {
                Icon(Icons.Default.CameraAlt, null)
                Text(" Camera")
            }
            Spacer(Modifier.width(6.dp))
            Button({ picker.launch("image/*") }, Modifier.weight(1f), enabled = !listening) {
                Icon(Icons.Default.AttachFile, null)
                Text(" Image")
            }
        }

        if (busy) LinearProgressIndicator(Modifier.fillMaxWidth().padding(top = 12.dp))

        Spacer(Modifier.height(16.dp))
        Button(
            onClick = { keyboard?.hide(); vm.setInput(text); vm.analyze() },
            modifier = Modifier.fillMaxWidth().height(54.dp),
            enabled = text.trim().isNotBlank() && !state.loading && !listening && !busy
        ) {
            if (state.loading) CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp)
            else Text("Analyze with AI")
        }

        Spacer(Modifier.height(12.dp))
        Text("Your evidence stays local unless you choose to send text to the configured backend.", color = TextMuted, fontSize = 12.sp)
    }
}

@Composable
private fun ResultScreen(vm: NyayViewModel, state: UiState) {
    val analysis = state.analysis ?: return

    Shell("AI Assessment", { vm.setScreen("home") }) {
        AssistChip(
            onClick = {},
            label = { Text("BACKEND AI RESULT") },
            leadingIcon = { Icon(Icons.Default.CheckCircle, null) }
        )

        Spacer(Modifier.height(12.dp))
        Card(
            colors = CardDefaults.cardColors(containerColor = Navy),
            shape = RoundedCornerShape(26.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(Modifier.padding(22.dp)) {
                Text("Situation summary", color = Color.White.copy(alpha = .7f))
                Spacer(Modifier.height(8.dp))
                Text(analysis.summary.ifBlank { "The backend classified the situation but returned no summary." }, color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(12.dp))
                Text(
                    "${analysis.primaryCategory} • ${analysis.secondaryCategories.joinToString().ifBlank { "single classification" }} • ${analysis.severity} • ${(analysis.confidence * 100).toInt()}%",
                    color = Color.White.copy(alpha = .75f),
                    fontSize = 12.sp
                )
            }
        }

        if (analysis.rights.isNotEmpty()) {
            Section("Your rights") { analysis.rights.forEach { Item(it.title, it.explanation) } }
        } else {
            Section("Your rights") { Text("The backend did not return rights for this case. Check the source guidance or try the analysis again.") }
        }

        Section("Next safe steps") {
            if (analysis.actionSteps.isEmpty()) Text("No action steps were returned. Prioritize immediate safety and verify important claims through official channels.")
            analysis.actionSteps.forEach { Text("${it.order}. ${it.text}", Modifier.padding(vertical = 5.dp)) }
        }

        Section("What not to do") {
            if (analysis.whatNotToDo.isEmpty()) Text("Avoid irreversible actions until the situation is verified.")
            analysis.whatNotToDo.forEach { Item(it.warning, it.reason) }
        }

        Section("Evidence to preserve") {
            if (analysis.evidenceToPreserve.isEmpty()) Text("Keep original messages, documents, screenshots, receipts and timestamps when safe.")
            analysis.evidenceToPreserve.forEach { Item(it.item, it.reason) }
        }

        if (analysis.evidenceGaps.isNotEmpty()) {
            Section("Potential evidence gaps") { analysis.evidenceGaps.forEach { Item(it.item, it.whyUseful) } }
        }

        if (analysis.safetyNotes.isNotBlank()) {
            Section("Safety note") { Text(analysis.safetyNotes) }
        }

        if (analysis.sources.isNotEmpty()) {
            Section("Sources returned by backend") {
                analysis.sources.forEach {
                    Text(it.title, fontWeight = FontWeight.SemiBold)
                    it.url?.let { url -> Text(url, color = Teal, fontSize = 12.sp) }
                    Spacer(Modifier.height(5.dp))
                }
            }
        }

        Text(analysis.disclaimer, Modifier.padding(vertical = 10.dp), color = TextMuted, fontSize = 12.sp)

        Row(Modifier.fillMaxWidth()) {
            Button({ vm.loadGaps() }, Modifier.weight(1f)) { Text("Evidence Gaps") }
            Spacer(Modifier.width(6.dp))
            Button({ vm.generateComplaint() }, Modifier.weight(1f)) { Text("Complaint Draft") }
        }
        Row(Modifier.fillMaxWidth().padding(top = 6.dp)) {
            Button({ vm.loadTimeline() }, Modifier.weight(1f)) { Text("Timeline") }
            Spacer(Modifier.width(6.dp))
            Button({ vm.loadClaims() }, Modifier.weight(1f)) { Text("Claim Map") }
        }
        Row(Modifier.fillMaxWidth().padding(top = 6.dp)) {
            OutlinedButton({ vm.setScreen("vault") }, Modifier.weight(1f)) { Text("Evidence Vault") }
            Spacer(Modifier.width(6.dp))
            OutlinedButton({ vm.setScreen("live") }, Modifier.weight(1f)) { Text("Live Mode") }
        }
        Button({ vm.setScreen("help") }, Modifier.fillMaxWidth().padding(top = 6.dp)) { Text("Find Legitimate Help") }
    }
}

@Composable
private fun LiveScreen(vm: NyayViewModel, state: UiState) {
    val context = LocalContext.current
    val locationPermission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) fetchLocation(context, vm) else Toast.makeText(context, "Location permission denied. Live mode still works without location.", Toast.LENGTH_LONG).show()
    }

    Shell("LIVE SITUATION", { vm.setScreen("home") }) {
        Text("Use this mode when something is happening now. Keep the screen simple and prioritize your safety.", color = TextMuted)
        Spacer(Modifier.height(14.dp))

        Text("CURRENT SITUATION", fontWeight = FontWeight.Bold, color = TextDark)
        Spacer(Modifier.height(8.dp))

        val options = listOf(
            "Traffic Stop" to "TRAFFIC_STOP",
            "Bribe Demand" to "BRIBE_DEMAND",
            "Threat / Harassment" to "THREAT_HARASSMENT",
            "Other Emergency" to "OTHER"
        )
        options.forEach { (label, category) ->
            Button(
                onClick = {
                    vm.setInput("I am currently dealing with a $label situation. I need immediate safety guidance.")
                    vm.analyze(category)
                },
                modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp),
                enabled = !state.loading
            ) { Text(label) }
        }

        Spacer(Modifier.height(10.dp))
        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(16.dp)) {
                Text("Current situation", fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(5.dp))
                Text(state.analysis?.summary ?: state.input.ifBlank { "Choose a situation above or describe what is happening." })
            }
        }

        Spacer(Modifier.height(10.dp))
        Button(
            onClick = { dialEmergency(context) },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = Danger)
        ) {
            Icon(Icons.Default.Phone, null)
            Spacer(Modifier.width(8.dp))
            Text("CALL EMERGENCY SERVICES — 112")
        }

        Button({ vm.setScreen("vault") }, Modifier.fillMaxWidth().padding(top = 8.dp)) { Text("Preserve Evidence") }
        Button({ locationPermission.launch(Manifest.permission.ACCESS_FINE_LOCATION) }, Modifier.fillMaxWidth().padding(top = 8.dp)) { Text("Get Current Location") }

        if (state.locationText.isNotBlank()) {
            Text("Location: ${state.locationText}", Modifier.padding(top = 8.dp), color = Teal)
            if (state.locationLat != null && state.locationLng != null) {
                OutlinedButton(
                    onClick = { openMap(context, state.locationLat, state.locationLng) },
                    modifier = Modifier.fillMaxWidth().padding(top = 5.dp)
                ) { Text("Open Location in Maps") }
            }
        }

        Button({ vm.setScreen("safety") }, Modifier.fillMaxWidth().padding(top = 8.dp)) { Text("Pause & Verify an Action") }
        Button({ shareTrusted(context, vm, state) }, Modifier.fillMaxWidth().padding(top = 8.dp)) { Text("Share with Trusted Contact") }
        Button({ vm.setScreen("help") }, Modifier.fillMaxWidth().padding(top = 8.dp)) { Text("Find Legitimate Help") }
    }
}

@Composable
private fun HelpScreen(vm: NyayViewModel, state: UiState) {
    val context = LocalContext.current
    val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) fetchLocation(context, vm) else vm.loadAuthorities(null, null)
    }

    LaunchedEffect(Unit) {
        if (state.authorities.isEmpty()) vm.loadAuthorities(null, null)
    }

    Shell("Legitimate Help", { vm.setScreen("home") }) {
        Text("Use official channels and verify contact details before relying on them.", color = TextMuted)
        Text("Location: ${state.locationText.ifBlank { "not provided" }}", Modifier.padding(top = 6.dp), color = TextMuted)

        Button({ permission.launch(Manifest.permission.ACCESS_FINE_LOCATION) }, Modifier.fillMaxWidth().padding(top = 10.dp)) {
            Text("Use Current Location")
        }

        if (state.locationLat != null && state.locationLng != null) {
            OutlinedButton(
                onClick = { openNearbySearch(context, state.locationLat, state.locationLng) },
                modifier = Modifier.fillMaxWidth().padding(top = 6.dp)
            ) {
                Text("Find Nearby Police / Help in Maps")
            }
        }

        if (state.authorities.isEmpty()) {
            Text("No verified local authority directory is configured. The app will not invent local contacts; use Maps or the official national channels below.", Modifier.padding(top = 14.dp))
        }

        state.authorities.forEach { authority ->
            Card(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
                Column(Modifier.padding(15.dp)) {
                    Text(authority.name, fontWeight = FontWeight.Bold)
                    Text(authority.type, color = Teal)
                    Text(authority.city)
                    authority.distanceKm?.let { Text("Distance: %.1f km".format(Locale.US, it)) }
                    authority.website?.let { website ->
                        TextButton({ openWeb(context, website) }) { Text("Open official website") }
                    }
                    TextButton({ openMap(context, authority.lat, authority.lng) }) { Text("Open in Maps") }
                }
            }
        }

        Section("Official national channels") {
            Text("Emergency police / emergency services: 112")
            Text("Cyber financial fraud: 1930")
            Text("National Consumer Helpline: 1915")
            Spacer(Modifier.height(8.dp))
            TextButton({ openWeb(context, "https://www.cybercrime.gov.in/") }) { Text("Cyber Crime Reporting Portal") }
            TextButton({ openWeb(context, "https://consumerhelpline.gov.in/") }) { Text("National Consumer Helpline") }
        }
    }
}

@Composable
private fun ComplaintScreen(vm: NyayViewModel, state: UiState) {
    val context = LocalContext.current
    val draft = state.complaint ?: return
    var text by remember(draft.body) { mutableStateOf(draft.body) }

    Shell("Complaint Draft", { vm.setScreen("result") }) {
        Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE6F0F5))) {
            Column(Modifier.padding(16.dp)) {
                Text("Draft only", fontWeight = FontWeight.Bold)
                Text("Review every fact before sharing. NyaySetu never submits a complaint automatically.", color = TextMuted)
            }
        }
        Spacer(Modifier.height(12.dp))
        Text(draft.subject, fontSize = 20.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(8.dp))
        OutlinedTextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.fillMaxWidth().height(380.dp)
        )
        Row(Modifier.fillMaxWidth().padding(top = 8.dp)) {
            OutlinedButton({ copyText(context, text) }, Modifier.weight(1f)) { Text("Copy") }
            Spacer(Modifier.width(6.dp))
            Button({ shareText(context, text) }, Modifier.weight(1f)) { Text("Share") }
        }
        Row(Modifier.fillMaxWidth().padding(top = 6.dp)) {
            OutlinedButton({ exportPdf(context, "NyaySetu Complaint", text) }, Modifier.weight(1f)) { Text("Export PDF") }
        }
        Section("Suggested recipient") { Text(draft.recipient) }
    }
}

@Composable
private fun Vault(vm: NyayViewModel, items: List<EvidenceEntity>) {
    Shell("Evidence Vault", { vm.setScreen("home") }) {
        Text("Evidence is stored locally on this device by default.", color = TextMuted)
        if (items.isEmpty()) Text("No evidence saved yet.", Modifier.padding(top = 20.dp))
        items.forEach { item ->
            Card(Modifier.fillMaxWidth().padding(vertical = 5.dp)) {
                Column(Modifier.padding(14.dp)) {
                    Text(item.name, fontWeight = FontWeight.Bold)
                    Text("${item.type} • ${item.hash.take(20)}…")
                    Text("SHA-256", fontWeight = FontWeight.SemiBold)
                    Text(item.hash, fontSize = 10.sp)
                    Text("Stored locally", color = Teal)
                    Text("A hash helps detect later file changes; it does not itself establish legal admissibility.", color = TextMuted, fontSize = 11.sp)
                    TextButton({ vm.deleteEvidence(item) }) { Text("Delete") }
                }
            }
        }
    }
}

@Composable
private fun History(vm: NyayViewModel, items: List<IncidentEntity>) {
    Shell("Incident History", { vm.setScreen("home") }) {
        if (items.isEmpty()) Text("No incidents yet.")
        items.forEach { item ->
            Card(Modifier.fillMaxWidth().padding(vertical = 5.dp)) {
                Column(Modifier.padding(14.dp)) {
                    Text(item.title, fontWeight = FontWeight.Bold)
                    Text("${item.category} • ${item.severity} • ${item.status}")
                    Text(item.summary, color = TextMuted)
                    Row {
                        TextButton({ vm.updateStatus(item.id, "ACTIVE") }) { Text("Active") }
                        TextButton({ vm.updateStatus(item.id, "RESOLVED") }) { Text("Resolved") }
                        TextButton({ vm.setInput(item.summary); vm.setScreen("input") }) { Text("Continue") }
                    }
                }
            }
        }
    }
}

@Composable
private fun TimelineScreen(vm: NyayViewModel, state: UiState) {
    Shell("Incident Timeline", { vm.setScreen("result") }) {
        Text("Only supplied times are treated as actual times. Inferred events are marked.", color = TextMuted)
        state.timeline.forEach { event ->
            Card(Modifier.fillMaxWidth().padding(vertical = 5.dp)) {
                Column(Modifier.padding(14.dp)) {
                    Text(event.time ?: "Time not provided", fontWeight = FontWeight.Bold)
                    Text(event.label)
                    if (event.inferred) Text("INFERRED", color = Color(0xFFB45309), fontSize = 11.sp)
                }
            }
        }
    }
}

@Composable
private fun ClaimsScreen(vm: NyayViewModel, state: UiState) {
    Shell("Evidence-to-Claim Mapping", { vm.setScreen("result") }) {
        Text("This maps evidence to described events; it does not prove a legal conclusion.", color = TextMuted)
        state.claims.forEach { claim ->
            Section(claim.status) {
                Text(claim.claim, fontWeight = FontWeight.SemiBold)
                Text(if (claim.evidence.isEmpty()) "No supporting evidence found." else claim.evidence.joinToString())
            }
        }
    }
}

@Composable
private fun SafetyScreen(vm: NyayViewModel, state: UiState) {
    var plan by remember { mutableStateOf("") }
    Shell("Pause & Verify", { vm.setScreen("result") }) {
        OutlinedTextField(
            value = plan,
            onValueChange = { plan = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("What are you planning to do?") }
        )
        Button({ vm.checkSafety(plan) }, Modifier.fillMaxWidth().padding(top = 10.dp), enabled = plan.isNotBlank()) { Text("Check safety") }
        state.safety?.let {
            Section("Why pause") {
                Text(it.appears)
                Text(it.risk, Modifier.padding(top = 4.dp))
                Text("Safer step: ${it.safer}", Modifier.padding(top = 6.dp), fontWeight = FontWeight.SemiBold)
            }
        }
    }
}

@Composable
private fun GapsScreen(vm: NyayViewModel, state: UiState) {
    LaunchedEffect(Unit) { if (state.gaps == null) vm.loadGaps() }
    Shell("Evidence Gaps", { vm.setScreen("result") }) {
        state.gaps?.let { gaps ->
            Section("Already available") {
                gaps.available.forEach { Text("✓ $it") }
            }
            Section("Potentially useful") {
                gaps.potentiallyUseful.forEach { Text("• $it") }
            }
            Section("Preservation steps") {
                gaps.recommended.forEach { Text("• $it") }
            }
        } ?: CircularProgressIndicator()
    }
}

@Composable
private fun OfflineScreen(vm: NyayViewModel) {
    Shell("Offline Rights", { vm.setScreen("home") }) {
        Section("Basic safety") {
            Text("Prioritize immediate safety. Do not escalate a dangerous confrontation. Preserve relevant records when safe. Verify important legal details when you regain connectivity.")
        }
        Section("Evidence basics") {
            Text("Keep original screenshots, messages, receipts, documents and timestamps. NyaySetu stores an integrity hash for saved files.")
        }
    }
}

@Composable
private fun SettingsScreen(vm: NyayViewModel, state: UiState) {
    val context = LocalContext.current
    var name by remember { mutableStateOf(vm.trustedName()) }
    var phone by remember { mutableStateOf(vm.trustedPhone()) }
    var enabled by remember { mutableStateOf(vm.trustedEnabled()) }
    var url by remember(state.backendUrl) { mutableStateOf(state.backendUrl) }

    Shell("Settings", { vm.setScreen("home") }) {
        Section("Trusted contact") {
            OutlinedTextField(name, { name = it }, Modifier.fillMaxWidth(), label = { Text("Name") })
            OutlinedTextField(phone, { phone = it }, Modifier.fillMaxWidth().padding(top = 6.dp), label = { Text("Phone number") })
            Row(verticalAlignment = Alignment.CenterVertically) {
                Switch(enabled, { enabled = it })
                Text("Enable trusted-contact sharing", Modifier.padding(start = 8.dp))
            }
            Button({
                vm.saveTrusted(name, phone, enabled)
                Toast.makeText(context, "Trusted contact saved", Toast.LENGTH_SHORT).show()
            }, Modifier.fillMaxWidth()) { Text("Save trusted contact") }
        }

        Section("Backend connection") {
            Text("On a physical phone, use the computer's LAN IP, for example http://192.168.1.5:8000/", color = TextMuted)
            OutlinedTextField(url, { url = it }, Modifier.fillMaxWidth(), label = { Text("Backend URL") })
            Button({
                vm.setBackendUrl(url)
                Toast.makeText(context, "Backend URL saved", Toast.LENGTH_SHORT).show()
            }, Modifier.fillMaxWidth()) { Text("Save backend URL") }
        }

        Section("Privacy") {
            Text("Evidence remains local by default. Text is sent to the configured backend only when you request analysis or another backend operation. Location and trusted-contact sharing require user action.")
        }

        Button({
            vm.clearData()
            Toast.makeText(context, "Local data deleted", Toast.LENGTH_SHORT).show()
        }, Modifier.fillMaxWidth()) { Text("Delete local data") }
    }
}

@Composable
private fun Section(title: String, content: @Composable ColumnScope.() -> Unit) {
    Spacer(Modifier.height(14.dp))
    Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold)
    Card(Modifier.fillMaxWidth().padding(top = 7.dp), shape = RoundedCornerShape(16.dp)) {
        Column(Modifier.padding(14.dp), content = content)
    }
}

@Composable
private fun Item(title: String, body: String) {
    Text(title, fontWeight = FontWeight.SemiBold)
    if (body.isNotBlank()) Text(body, Modifier.padding(top = 2.dp, bottom = 7.dp), color = TextMuted)
}

private fun bitmapBytes(bitmap: Bitmap): ByteArray {
    val output = java.io.ByteArrayOutputStream()
    bitmap.compress(Bitmap.CompressFormat.JPEG, 90, output)
    return output.toByteArray()
}

private fun processUri(
    context: Context,
    uri: Uri,
    vm: NyayViewModel,
    onBusy: (Boolean) -> Unit,
    onText: (String) -> Unit = {}
) {
    val resolver = context.contentResolver
    val mime = resolver.getType(uri).orEmpty()
    val name = resolver.query(uri, null, null, null, null)?.use { cursor ->
        val index = cursor.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
        if (cursor.moveToFirst() && index >= 0) cursor.getString(index) else null
    } ?: "shared_file"

    val bytes = runCatching {
        resolver.openInputStream(uri)?.use { it.readBytes() }
    }.getOrNull()

    if (bytes == null) {
        Toast.makeText(context, "Could not read the selected file.", Toast.LENGTH_LONG).show()
        return
    }

    vm.saveEvidence(name, mime.ifBlank { "file" }, bytes, "Imported from Android share/file picker")

    if (mime.startsWith("image/")) {
        onBusy(true)
        val image = runCatching { InputImage.fromFilePath(context, uri) }.getOrNull()
        if (image == null) {
            onBusy(false)
            Toast.makeText(context, "Image could not be opened.", Toast.LENGTH_LONG).show()
            return
        }
        TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
            .process(image)
            .addOnSuccessListener { result ->
                if (result.text.isNotBlank()) onText(result.text.trim())
            }
            .addOnFailureListener {
                Toast.makeText(context, "OCR failed. You can type the situation manually.", Toast.LENGTH_LONG).show()
            }
            .addOnCompleteListener { onBusy(false) }
    } else if (mime == "text/plain" || mime.startsWith("text/")) {
        vm.setInput(bytes.toString(Charsets.UTF_8))
    } else {
        vm.setInput(vm.state.value.input + "\nAttached file: $name. Please describe what happened after reviewing it.")
    }
}

private fun startSpeech(context: Context, currentText: String, onText: (String) -> Unit, onFinished: () -> Unit) {
    if (!SpeechRecognizer.isRecognitionAvailable(context)) {
        Toast.makeText(context, "Speech recognition is unavailable on this phone.", Toast.LENGTH_LONG).show()
        onFinished()
        return
    }

    val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
    var finished = false

    fun finish() {
        if (finished) return
        finished = true
        runCatching { recognizer.destroy() }
        onFinished()
    }

    recognizer.setRecognitionListener(object : RecognitionListener {
        override fun onResults(results: Bundle?) {
            val spoken = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()?.trim().orEmpty()
            if (spoken.isNotBlank()) {
                onText(if (currentText.isBlank()) spoken else "$currentText $spoken")
            } else {
                Toast.makeText(context, "No speech was recognized. Please try again.", Toast.LENGTH_LONG).show()
            }
            finish()
        }
        override fun onError(error: Int) {
            Toast.makeText(context, "Speech recognition failed. Please try again.", Toast.LENGTH_LONG).show()
            finish()
        }
        override fun onReadyForSpeech(params: Bundle?) = Unit
        override fun onBeginningOfSpeech() = Unit
        override fun onRmsChanged(rmsdB: Float) = Unit
        override fun onBufferReceived(buffer: ByteArray?) = Unit
        override fun onEndOfSpeech() = Unit
        override fun onPartialResults(partialResults: Bundle?) = Unit
        override fun onEvent(eventType: Int, params: Bundle?) = Unit
    })

    val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
        putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN")
        putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
        putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
    }

    runCatching { recognizer.startListening(intent) }.onFailure {
        Toast.makeText(context, "Could not start speech recognition.", Toast.LENGTH_LONG).show()
        finish()
    }
}

private fun fetchLocation(context: Context, vm: NyayViewModel) {
    if (ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) return
    LocationServices.getFusedLocationProviderClient(context).lastLocation
        .addOnSuccessListener { location ->
            if (location != null) {
                vm.setLocation(location.latitude, location.longitude)
                vm.loadAuthorities(location.latitude, location.longitude)
            } else {
                vm.loadAuthorities(null, null)
                Toast.makeText(context, "Current location is not available yet. Turn on location and try again.", Toast.LENGTH_LONG).show()
            }
        }
        .addOnFailureListener {
            vm.loadAuthorities(null, null)
            Toast.makeText(context, "Location could not be read.", Toast.LENGTH_LONG).show()
        }
}

private fun dialEmergency(context: Context) {
    runCatching {
        context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:112")))
    }.onFailure {
        Toast.makeText(context, "Could not open the phone dialer.", Toast.LENGTH_LONG).show()
    }
}

private fun shareTrusted(context: Context, vm: NyayViewModel, state: UiState) {
    val name = vm.trustedName()
    val phone = vm.trustedPhone()
    if (!vm.trustedEnabled() || name.isBlank() || phone.isBlank()) {
        Toast.makeText(context, "Add and enable a trusted contact in Settings first.", Toast.LENGTH_LONG).show()
        return
    }

    val location = state.locationText.ifBlank { "location not shared" }
    val message = "NyaySetu AI live situation update. Incident: ${state.incidentId ?: "not created"}. Severity: ${state.analysis?.severity ?: "UNKNOWN"}. Location: $location. Please contact me if needed."
    val intent = Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:${Uri.encode(phone)}")).apply {
        putExtra("sms_body", message)
    }
    runCatching { context.startActivity(intent) }.onFailure {
        Toast.makeText(context, "No messaging app is available.", Toast.LENGTH_SHORT).show()
    }
}

private fun copyText(context: Context, text: String) {
    val manager = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
    manager.setPrimaryClip(android.content.ClipData.newPlainText("NyaySetu", text))
    Toast.makeText(context, "Copied", Toast.LENGTH_SHORT).show()
}

private fun shareText(context: Context, text: String) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
    }
    context.startActivity(Intent.createChooser(intent, "Share"))
}

private fun exportPdf(context: Context, title: String, text: String) {
    runCatching {
        val document = PdfDocument()
        val page = document.startPage(PdfDocument.PageInfo.Builder(595, 842, 1).create())
        val canvas = page.canvas
        val titlePaint = android.graphics.Paint().apply { textSize = 18f; isFakeBoldText = true }
        val paint = android.graphics.Paint().apply { textSize = 11f }
        var y = 36f
        canvas.drawText(title, 30f, y, titlePaint)
        y += 28f
        text.replace("\r", "").split("\n").flatMap { line ->
            if (line.length <= 82) listOf(line) else line.chunked(82)
        }.take(43).forEach { line ->
            canvas.drawText(line, 30f, y, paint)
            y += 18f
        }
        document.finishPage(page)
        val file = File(context.cacheDir, "nyaysetu_complaint.pdf")
        FileOutputStream(file).use { document.writeTo(it) }
        document.close()
        val uri = FileProvider.getUriForFile(context, context.packageName + ".fileprovider", file)
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "application/pdf"
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(intent, "Export PDF"))
    }.onFailure {
        Toast.makeText(context, "PDF export failed: ${it.message}", Toast.LENGTH_LONG).show()
    }
}

private fun openWeb(context: Context, url: String) {
    runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
}

private fun openNearbySearch(context: Context, lat: Double, lng: Double) {
    runCatching {
        val uri = Uri.parse("geo:$lat,$lng?q=police+station+near+me")
        context.startActivity(Intent(Intent.ACTION_VIEW, uri))
    }.onFailure {
        Toast.makeText(context, "Could not open Maps.", Toast.LENGTH_LONG).show()
    }
}

private fun openMap(context: Context, lat: Double, lng: Double) {
    runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("geo:$lat,$lng?q=$lat,$lng"))) }
}
