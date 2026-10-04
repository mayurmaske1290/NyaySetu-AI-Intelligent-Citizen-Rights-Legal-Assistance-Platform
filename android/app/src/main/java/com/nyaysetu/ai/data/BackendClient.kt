package com.nyaysetu.ai.data

import com.nyaysetu.ai.domain.model.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

class BackendClient(initialBaseUrl: String) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(90, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private var baseUrl = normalize(initialBaseUrl)
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    @Synchronized
    fun setBaseUrl(url: String) { baseUrl = normalize(url) }

    @Synchronized
    fun getBaseUrl(): String = baseUrl

    fun analyze(text: String, language: String = "en", categoryHint: String? = null): Analysis? {
        val body = JSONObject().apply {
            put("text", text)
            put("language", language)
            categoryHint?.let { put("category_hint", it) }
        }
        return post("/api/analyze/text", body)?.let(::parseAnalysis)
    }

    fun evidenceGaps(description: String, category: String, evidence: List<EvidenceEntity>): GapResult? {
        val body = JSONObject().apply {
            put("description", description)
            put("category", category)
            put("evidence", JSONArray().apply { evidence.forEach { put(evidenceJson(it)) } })
        }
        return post("/api/evidence/gaps", body)?.let { o ->
            GapResult(
                strings(o.optJSONArray("available")),
                strings(o.optJSONArray("potentially_useful")),
                strings(o.optJSONArray("recommended_preservation"))
            )
        }
    }

    fun timeline(description: String, evidence: List<EvidenceEntity>): List<TimelineEvent>? {
        val body = JSONObject().apply {
            put("description", description)
            put("evidence", JSONArray().apply { evidence.forEach { put(evidenceJson(it)) } })
        }
        return post("/api/timeline/generate", body)?.let { o ->
            val array = o.optJSONArray("events") ?: JSONArray()
            buildList { for (i in 0 until array.length()) {
                val e = array.optJSONObject(i) ?: continue
                add(TimelineEvent(e.optStringOrNull("event_time"), e.optString("label"), e.optBoolean("inferred", false)))
            }}
        }
    }

    fun claims(description: String, evidence: List<EvidenceEntity>): List<ClaimLink>? {
        val body = JSONObject().apply {
            put("description", description)
            put("evidence", JSONArray().apply { evidence.forEach { put(evidenceJson(it)) } })
        }
        return post("/api/claims/map", body)?.let { o ->
            val array = o.optJSONArray("mappings") ?: JSONArray()
            buildList { for (i in 0 until array.length()) {
                val e = array.optJSONObject(i) ?: continue
                add(ClaimLink(e.optString("claim"), strings(e.optJSONArray("evidence_names")), e.optString("status")))
            }}
        }
    }

    fun actionSafety(planned: String, situation: String, category: String?): ActionSafety? {
        val body = JSONObject().apply {
            put("planned_action", planned)
            put("situation", situation)
            category?.let { put("category", it) }
        }
        return post("/api/action-safety/check", body)?.let { o ->
            ActionSafety(o.optString("appears_to_plan"), o.optString("risk_why"), o.optString("safer_step"))
        }
    }

    fun complaint(
        statement: String,
        category: String?,
        evidenceNames: List<String>,
        incidentId: String?,
        locationText: String?
    ): ComplaintDraft? {
        val body = JSONObject().apply {
            incidentId?.let { put("incident_id", it) }
            put("user_statement", statement)
            category?.let { put("category", it) }
            locationText?.takeIf { it.isNotBlank() }?.let { put("location_text", it) }
            put("evidence_names", JSONArray(evidenceNames))
        }
        return post("/api/complaints/generate", body)?.let { o ->
            ComplaintDraft(
                subject = o.optString("subject"),
                summary = o.optString("incident_summary"),
                body = o.optString("body"),
                recipient = o.optString("recipient_category")
            )
        }
    }

    fun authorities(lat: Double?, lng: Double?, category: String?): List<AuthorityItem>? {
        val query = buildString {
            lat?.let { append("lat=$it&") }
            lng?.let { append("lng=$it&") }
            category?.let { append("category=").append(java.net.URLEncoder.encode(it, "UTF-8")).append('&') }
        }.trimEnd('&')
        return get("/api/authorities/nearby${if (query.isNotBlank()) "?$query" else ""}")?.let { o ->
            val array = o.optJSONArray("most_appropriate") ?: o.optJSONArray("nearest") ?: JSONArray()
            buildList { for (i in 0 until array.length()) {
                val a = array.optJSONObject(i) ?: continue
                add(AuthorityItem(
                    id = a.optString("authority_id"),
                    name = a.optString("name"),
                    type = a.optString("type"),
                    city = a.optString("city"),
                    lat = a.optDouble("latitude"),
                    lng = a.optDouble("longitude"),
                    website = a.optStringOrNull("website"),
                    isDemo = a.optBoolean("is_demo", true),
                    distanceKm = if (a.has("distance_km") && !a.isNull("distance_km")) a.optDouble("distance_km") else null
                ))
            }}
        }
    }

    private fun post(path: String, json: JSONObject): JSONObject? = request("POST", path, json)

    private fun get(path: String): JSONObject? = request("GET", path, null)

    private fun request(method: String, path: String, json: JSONObject?): JSONObject? {
        val url = synchronized(this) { baseUrl.trimEnd('/') + "/" + path.trimStart('/') }
        val builder = Request.Builder().url(url).header("Accept", "application/json")
        if (method == "POST") {
            builder.post((json?.toString() ?: "{}").toRequestBody(jsonMediaType))
        } else builder.get()

        try {
            client.newCall(builder.build()).execute().use { response ->
                val raw = response.body?.string().orEmpty()
                if (!response.isSuccessful) {
                    val message = runCatching { JSONObject(raw).optString("detail") }.getOrNull().orEmpty()
                    throw BackendException(message.ifBlank { "Backend returned HTTP ${response.code}." })
                }
                if (raw.isBlank()) throw BackendException("Backend returned an empty response.")
                return JSONObject(raw)
            }
        } catch (e: BackendException) { throw e }
        catch (e: IOException) { throw BackendException("Cannot reach backend at $url. Start the backend and verify the app URL.", e) }
        catch (e: Exception) { throw BackendException(e.message ?: "Backend request failed.", e) }
    }

    private fun parseAnalysis(o: JSONObject): Analysis = Analysis(
        primaryCategory = o.optString("primary_category", "OTHER"),
        secondaryCategories = strings(o.optJSONArray("secondary_categories")),
        severity = o.optString("severity", "LOW"),
        confidence = o.optDouble("confidence", 0.0).coerceIn(0.0, 1.0),
        confidenceLabel = o.optString("confidence_label", "UNCERTAIN"),
        summary = o.optString("summary"),
        rights = objects(o.optJSONArray("rights")) { RightItem(it.optString("title"), it.optString("explanation"), it.optString("why"), it.optStringOrNull("source_title")) },
        whatNotToDo = objects(o.optJSONArray("what_not_to_do")) { WarningItem(it.optString("warning"), it.optString("reason")) },
        actionSteps = objects(o.optJSONArray("action_steps")) { ActionStep(it.optInt("order", 0), it.optString("text"), it.optString("kind", "immediate")) },
        evidenceToPreserve = objects(o.optJSONArray("evidence_to_preserve")) { EvidenceHint(it.optString("item"), it.optString("reason")) },
        evidenceGaps = objects(o.optJSONArray("evidence_gaps")) { EvidenceGap(it.optString("item"), it.optString("why_useful")) },
        sources = objects(o.optJSONArray("sources")) { SourceRef(it.optString("title"), it.optStringOrNull("url"), it.optBoolean("demo", false)) },
        requiresHumanHelp = o.optBoolean("requires_human_help", false),
        safetyNotes = o.optString("safety_notes"),
        disclaimer = o.optString("disclaimer", "Informational assistance only. Not legal advice."),
        demoMode = o.optBoolean("demo_mode", false)
    )

    private fun evidenceJson(e: EvidenceEntity) = JSONObject().apply {
        put("id", e.id); put("file_name", e.name); put("file_type", e.type); put("description", e.note)
        put("source_type", e.type); put("sha256_hash", e.hash); put("has_location", false); put("has_timestamp", true)
    }

    private fun strings(a: JSONArray?): List<String> = if (a == null) emptyList() else buildList { for (i in 0 until a.length()) add(a.optString(i)) }

    private fun <T> objects(a: JSONArray?, map: (JSONObject) -> T): List<T> = if (a == null) emptyList() else buildList { for (i in 0 until a.length()) a.optJSONObject(i)?.let { add(map(it)) } }

    private fun normalize(url: String): String = url.trim().ifBlank { "http://10.0.2.2:8000" }.trimEnd('/')

    private fun JSONObject.optStringOrNull(key: String): String? = if (has(key) && !isNull(key)) optString(key).takeIf { it.isNotBlank() } else null
}

class BackendException(message: String, cause: Throwable? = null) : RuntimeException(message, cause)
