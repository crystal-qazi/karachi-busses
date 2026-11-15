package pk.karachibuses.app.data.remote

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.google.gson.JsonElement
import com.google.gson.JsonObject
import java.nio.charset.StandardCharsets
import java.security.MessageDigest

object DatasetChecksum {
    private val gson: Gson = GsonBuilder().serializeNulls().disableHtmlEscaping().create()

    fun sha256(dataset: DatasetDto): String {
        val tree = gson.toJsonTree(dataset)
        val canonical = canonicalize(tree)
        val bytes = gson.toJson(canonical).toByteArray(StandardCharsets.UTF_8)
        return MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it.toInt() and 0xff) }
    }

    private fun canonicalize(value: JsonElement): JsonElement = when {
        value.isJsonObject -> {
            val sorted = JsonObject()
            value.asJsonObject.entrySet().sortedBy { it.key }.forEach {
                sorted.add(it.key, canonicalize(it.value))
            }
            sorted
        }
        value.isJsonArray -> {
            val array = com.google.gson.JsonArray()
            value.asJsonArray.forEach { array.add(canonicalize(it)) }
            array
        }
        else -> value
    }
}