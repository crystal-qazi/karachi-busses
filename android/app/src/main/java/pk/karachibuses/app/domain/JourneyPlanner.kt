package pk.karachibuses.app.domain

import pk.karachibuses.app.data.local.*
import kotlin.math.*

data class JourneyOption(
    val routeCodes: List<String>,
    val directionNames: List<String>,
    val boardingStop: String,
    val transferStop: String?,
    val destinationStop: String
) {
    val isDirect: Boolean get() = transferStop == null
}

object JourneyPlanner {
    fun plan(
        originLat: Double,
        originLng: Double,
        destinationQuery: String,
        radiusMetres: Double,
        routes: List<RouteEntity>,
        directions: List<DirectionEntity>,
        stops: List<StopEntity>,
        links: List<DirectionStopEntity>,
        maxResults: Int = 20
    ): List<JourneyOption> {
        require(originLat in -90.0..90.0 && originLng in -180.0..180.0)
        require(radiusMetres in 100.0..10000.0)
        val destinationIds = stops.filter { it.stopName.contains(destinationQuery, ignoreCase = true) }.map { it.id }.toSet()
        if (destinationIds.isEmpty()) return emptyList()
        val stopById = stops.associateBy { it.id }
        val routeById = routes.associateBy { it.id }
        val directionById = directions.associateBy { it.id }
        val byDirection = links.groupBy { it.directionId }.mapValues { (_, rows) -> rows.sortedBy { it.sequence } }
        val origin = stops.map { it to distance(originLat, originLng, it.latitude, it.longitude) }
            .filter { it.second <= radiusMetres }.minByOrNull { it.second }?.first ?: return emptyList()
        val results = mutableListOf<JourneyOption>()

        for ((directionId, rows) in byDirection) {
            val boardIndex = rows.indexOfFirst { it.stopId == origin.id }
            if (boardIndex < 0) continue
            val direction = directionById[directionId] ?: continue
            val route = routeById[direction.routeId] ?: continue
            val destinationLink = rows.drop(boardIndex + 1).firstOrNull { it.stopId in destinationIds }
            if (destinationLink != null) {
                val destination = stopById[destinationLink.stopId]
                if (destination != null) results += JourneyOption(listOf(route.routeCode), listOf(direction.directionName), origin.stopName, null, destination.stopName)
            }
        }

        if (results.isEmpty()) {
            for ((firstDirectionId, firstRows) in byDirection) {
                val boardIndex = firstRows.indexOfFirst { it.stopId == origin.id }
                if (boardIndex < 0) continue
                val firstDirection = directionById[firstDirectionId] ?: continue
                val firstRoute = routeById[firstDirection.routeId] ?: continue
                for (transferLink in firstRows.drop(boardIndex + 1)) {
                    val transfer = stopById[transferLink.stopId] ?: continue
                    for ((secondDirectionId, secondRows) in byDirection) {
                        if (secondDirectionId == firstDirectionId) continue
                        val transferIndex = secondRows.indexOfFirst { it.stopId == transferLink.stopId }
                        if (transferIndex < 0) continue
                        val secondDirection = directionById[secondDirectionId] ?: continue
                        val secondRoute = routeById[secondDirection.routeId] ?: continue
                        val destinationLink = secondRows.drop(transferIndex + 1).firstOrNull { it.stopId in destinationIds } ?: continue
                        val destination = stopById[destinationLink.stopId] ?: continue
                        results += JourneyOption(
                            listOf(firstRoute.routeCode, secondRoute.routeCode),
                            listOf(firstDirection.directionName, secondDirection.directionName),
                            origin.stopName, transfer.stopName, destination.stopName
                        )
                        if (results.size >= maxResults) return results
                    }
                }
            }
        }
        return results.distinctBy { listOf(it.routeCodes, it.boardingStop, it.transferStop, it.destinationStop) }.take(maxResults)
    }

    private fun distance(lat1: Double, lng1: Double, lat2: Double, lng2: Double): Double {
        val earth = 6371000.0
        val dLat = Math.toRadians(lat2 - lat1)
        val dLng = Math.toRadians(lng2 - lng1)
        val a = sin(dLat / 2).pow(2) + cos(Math.toRadians(lat1)) * cos(Math.toRadians(lat2)) * sin(dLng / 2).pow(2)
        return 2 * earth * asin(sqrt(a.coerceIn(0.0, 1.0)))
    }
}