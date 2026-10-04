package com.nyaysetu.ai.core

import java.security.MessageDigest
import java.util.Calendar
import kotlin.random.Random

object FileHasher {
    fun sha256(bytes: ByteArray): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(bytes)
        return digest.joinToString("") { "%02x".format(it) }
    }
}

object IncidentIds {
    fun create(year: Int = Calendar.getInstance().get(Calendar.YEAR)): String {
        val chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        val suffix = (1..5).map { chars[Random.nextInt(chars.length)] }.joinToString("")
        return "NYA-$year-$suffix"
    }
}

sealed class Outcome<out T> {
    data class Ok<T>(val value: T) : Outcome<T>()
    data class Err(val message: String, val retryable: Boolean = true) : Outcome<Nothing>()
}
