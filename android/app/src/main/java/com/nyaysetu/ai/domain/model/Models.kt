package com.nyaysetu.ai.domain.model

data class RightItem(val title: String, val explanation: String, val why: String, val sourceTitle: String? = null)
data class WarningItem(val warning: String, val reason: String)
data class ActionStep(val order: Int, val text: String, val kind: String)
data class EvidenceHint(val item: String, val reason: String)
data class EvidenceGap(val item: String, val whyUseful: String)
data class SourceRef(val title: String, val url: String? = null, val demo: Boolean = true)

data class Analysis(
    val primaryCategory: String,
    val secondaryCategories: List<String>,
    val severity: String,
    val confidence: Double,
    val confidenceLabel: String,
    val summary: String,
    val rights: List<RightItem>,
    val whatNotToDo: List<WarningItem>,
    val actionSteps: List<ActionStep>,
    val evidenceToPreserve: List<EvidenceHint>,
    val evidenceGaps: List<EvidenceGap>,
    val sources: List<SourceRef>,
    val requiresHumanHelp: Boolean,
    val safetyNotes: String,
    val disclaimer: String,
    val demoMode: Boolean,
)

data class GapResult(
    val available: List<String>,
    val potentiallyUseful: List<String>,
    val recommended: List<String>,
)

data class TimelineEvent(val time: String?, val label: String, val inferred: Boolean)
data class ClaimLink(val claim: String, val evidence: List<String>, val status: String)
data class ActionSafety(val appears: String, val risk: String, val safer: String)
data class ComplaintDraft(
    val subject: String,
    val summary: String,
    val body: String,
    val recipient: String,
)
data class AuthorityItem(
    val id: String,
    val name: String,
    val type: String,
    val city: String,
    val lat: Double,
    val lng: Double,
    val website: String?,
    val isDemo: Boolean,
    val distanceKm: Double?,
)
