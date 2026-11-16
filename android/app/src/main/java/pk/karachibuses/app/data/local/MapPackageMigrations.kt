package pk.karachibuses.app.data.local

import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

/** Adds the local catalogue used to track full-city and area map packages. */
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE IF NOT EXISTS map_packages (
                packageId TEXT NOT NULL PRIMARY KEY,
                displayName TEXT NOT NULL,
                kind TEXT NOT NULL,
                areaSlug TEXT,
                west REAL NOT NULL,
                south REAL NOT NULL,
                east REAL NOT NULL,
                north REAL NOT NULL,
                minZoom INTEGER NOT NULL,
                maxZoom INTEGER NOT NULL,
                packageVersion TEXT NOT NULL,
                format TEXT NOT NULL,
                sizeBytes INTEGER NOT NULL,
                checksumSha256 TEXT NOT NULL,
                attribution TEXT NOT NULL,
                sourceName TEXT NOT NULL,
                licenceName TEXT NOT NULL,
                licenceUrl TEXT,
                offlineDownloadAllowed INTEGER NOT NULL,
                downloadUri TEXT,
                state TEXT NOT NULL,
                installedPath TEXT,
                updatedAtEpochMs INTEGER NOT NULL
            )
        """.trimIndent())
        db.execSQL("CREATE INDEX IF NOT EXISTS index_map_packages_kind ON map_packages(kind)")
        db.execSQL("CREATE INDEX IF NOT EXISTS index_map_packages_state ON map_packages(state)")
    }
}
