package com.nyaysetu.ai.presentation

import android.net.Uri
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

object ShareBus {
    private val _events = MutableStateFlow<Pair<String?, List<Uri>>?>(null)
    val events = _events.asStateFlow()

    fun publish(text: String?, uris: List<Uri>) { _events.value = text to uris }
    fun clear() { _events.value = null }
}
