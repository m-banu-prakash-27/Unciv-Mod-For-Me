package com.unciv.logic.civilization

import com.unciv.logic.IsPartOfGameInfoSerialization
import com.unciv.logic.city.City
import com.unciv.logic.civilization.Notification.NotificationCategory

/** Stored on the player civilization. A new objective replaces the previous result. */
data class MagalanaduDefenseObjective(
    val defenderId: String = "",
    val defenderName: String = "",
    val rivalId: String = "",
    val rivalName: String = "",
    val cityId: String = "",
    val cityName: String = "",
    val deadline: Int = 0,
    val status: Status = Status.Active
) : IsPartOfGameInfoSerialization {
    enum class Status { Active, Succeeded, CityLost, NeutralityBroken, Cancelled }

    companion object {
        const val Duration = 20
        const val Reward = 500

        fun canStart(player: Civilization, defender: Civilization, rival: Civilization): Boolean =
            player.civName == "Magalanadu" && player.isHuman() && player.isCurrentPlayer()
                && !player.gameInfo.gameParameters.isOnlineMultiplayer && !player.isDefeated()
                && player.magalanaduDefenseObjective?.status != Status.Active
                && defender != player && rival != player && defender != rival
                && defender.isMajorCiv && rival.isMajorCiv && !defender.isDefeated() && !rival.isDefeated()
                && player.knows(defender) && player.knows(rival)
                && defender.isAtWarWith(rival) && !player.isAtWarWith(defender) && !player.isAtWarWith(rival)

        fun start(player: Civilization, defender: Civilization, rival: Civilization, city: City): Boolean {
            if (!canStart(player, defender, rival) || city !in defender.cities) return false
            player.magalanaduDefenseObjective = MagalanaduDefenseObjective(
                defender.civID, defender.civName, rival.civID, rival.civName, city.id, city.name,
                player.gameInfo.turns + Duration
            )
            return true
        }

        fun cancel(player: Civilization) {
            val objective = player.magalanaduDefenseObjective ?: return
            if (objective.status == Status.Active)
                player.magalanaduDefenseObjective = objective.copy(status = Status.Cancelled)
        }

        /** Called after the next human turn has started, after intervening AI turns. */
        fun checkTurn(player: Civilization) {
            val objective = player.magalanaduDefenseObjective ?: return
            if (objective.status != Status.Active) return
            val defender = player.gameInfo.getCivilizationOrNull(objective.defenderId)
            val rival = player.gameInfo.getCivilizationOrNull(objective.rivalId)
            when {
                defender == null || defender.cities.none { it.id == objective.cityId } ->
                    finish(player, Status.CityLost)
                player.isAtWarWith(defender) || (rival != null && player.isAtWarWith(rival)) ->
                    finish(player, Status.NeutralityBroken)
                player.gameInfo.turns >= objective.deadline ->
                    finish(player, Status.Succeeded)
            }
        }

        /** Catches joining either side, even if peace is signed in the same turn. */
        fun onWarDeclared(player: Civilization, other: Civilization) {
            val objective = player.magalanaduDefenseObjective ?: return
            if (other.civID == objective.defenderId || other.civID == objective.rivalId)
                finish(player, Status.NeutralityBroken)
        }

        /** Catches loss even if the city is immediately retaken. */
        fun onCityLost(owner: Civilization, city: City) {
            for (player in owner.gameInfo.civilizations) {
                val objective = player.magalanaduDefenseObjective ?: continue
                if (objective.defenderId == owner.civID && objective.cityId == city.id)
                    finish(player, Status.CityLost)
            }
        }

        private fun finish(player: Civilization, status: Status) {
            val objective = player.magalanaduDefenseObjective ?: return
            if (objective.status != Status.Active) return
            player.magalanaduDefenseObjective = objective.copy(status = status)
            val result = when (status) {
                Status.Succeeded -> {
                    player.addGold(Reward)
                    "Objective complete. ${objective.defenderName} held ${objective.cityName}. You earned $Reward Gold."
                }
                Status.CityLost -> "Objective failed. ${objective.defenderName} lost ${objective.cityName}."
                Status.NeutralityBroken -> "Objective failed. Magalanadu entered the war against one of the participants."
                else -> return
            }
            player.addNotification(result, NotificationCategory.Diplomacy)
        }
    }
}
