package com.nyaysetu.ai

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import dagger.hilt.android.AndroidEntryPoint
import com.nyaysetu.ai.presentation.NyayApp
import com.nyaysetu.ai.presentation.ShareBus

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)

        enableEdgeToEdge()

        handleShare(intent)

        setContent {
            NyayApp()
        }
    }

    override fun onNewIntent(
        intent: Intent
    ) {
        super.onNewIntent(intent)

        setIntent(intent)

        handleShare(intent)
    }

    private fun handleShare(
        intent: Intent?
    ) {

        if (intent == null) {
            return
        }

        when (intent.action) {

            Intent.ACTION_SEND -> {

                val text =
                    intent.getStringExtra(
                        Intent.EXTRA_TEXT
                    )

                val uri =
                    intent.getParcelableExtra<Uri>(
                        Intent.EXTRA_STREAM
                    )

                ShareBus.publish(
                    text,
                    listOfNotNull(uri)
                )
            }

            Intent.ACTION_SEND_MULTIPLE -> {

                val uris =
                    intent.getParcelableArrayListExtra<Uri>(
                        Intent.EXTRA_STREAM
                    ).orEmpty()

                ShareBus.publish(
                    null,
                    uris
                )
            }
        }
    }
}