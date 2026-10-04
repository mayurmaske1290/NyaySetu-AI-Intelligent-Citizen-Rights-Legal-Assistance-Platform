package com.nyaysetu.ai.core.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import androidx.compose.material3.Typography

val TealDeep = Color(0xFF0F3D3E)
val TealMid = Color(0xFF1F6F70)
val Sand = Color(0xFFF4F0E8)
val Ink = Color(0xFF1A1A1A)
val Danger = Color(0xFF8B2E2E)
val Caution = Color(0xFF8A6A12)
val OkGreen = Color(0xFF1B5E3B)

private val Light = lightColorScheme(
    primary = TealDeep,
    onPrimary = Color.White,
    secondary = TealMid,
    background = Sand,
    surface = Color.White,
    onBackground = Ink,
    onSurface = Ink,
    error = Danger,
)

@Composable
fun NyayTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = Light,
        typography = Typography(
            headlineLarge = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 28.sp, color = TealDeep),
            titleLarge = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 20.sp),
            bodyLarge = TextStyle(fontSize = 16.sp, lineHeight = 24.sp),
        ),
        content = content,
    )
}
