package com.unciv.logic.civilization

import com.unciv.Constants
import com.unciv.logic.city.City
import com.unciv.logic.civilization.diplomacy.DiplomaticModifiers
import com.unciv.logic.trade.TradeLogic
import com.unciv.logic.trade.TradeOffer
import com.unciv.logic.trade.TradeOfferType
import com.unciv.models.SpyAction
import com.unciv.models.ruleset.tile.ResourceType
import com.unciv.models.ruleset.unique.UniqueType
import kotlin.random.Random

object MagalanaduAgency {
    const val Slots = 3
    const val CarefulCost = 25
    private const val ReportLimit = 24

    fun isAvailable(player: Civilization) =
        player.civName == "Magalanadu" && player.isHuman() && !player.isDefeated()
            && !player.gameInfo.gameParameters.isOnlineMultiplayer

    fun targets(player: Civilization) = player.getKnownCivs()
        .filter { it != player && !it.isDefeated() && (it.isMajorCiv || it.isCityState) }
        .sortedBy { it.civName }.toList()

    fun partners(player: Civilization, target: Civilization) = targets(player)
        .filter { it != target && it.isMajorCiv && target.isMajorCiv && target.knows(it) }

    fun network(player: Civilization, target: Civilization) =
        player.magalanaduAgency?.networks?.get(target.civID) ?: AgencyNetwork()

    fun chance(mission: AgencyMission, network: AgencyNetwork, careful: Boolean): Int =
        (mission.chance + network.access * 3 + stationBonus(network) - network.heat / 5 +
            (if (careful) 15 else 0)).coerceIn(15, 97)

    private fun stationBonus(network: AgencyNetwork) = if (network.station) 7 else 0

    fun exposure(mission: AgencyMission, network: AgencyNetwork, careful: Boolean): Int {
        val base = when (mission.group) {
            AgencyGroup.Intel, AgencyGroup.Network -> 12
            AgencyGroup.Influence -> 20
            AgencyGroup.Action, AgencyGroup.Conflict -> 30
        }
        return (base + network.heat / 3 - network.cover * 4 -
            (if (network.route) 10 else 0) - (if (careful) 15 else 0)).coerceIn(3, 75)
    }

    fun cost(mission: AgencyMission, careful: Boolean) = mission.cost + if (careful) CarefulCost else 0

    fun duration(mission: AgencyMission, careful: Boolean) = mission.turns + if (careful) 1 else 0

    fun queue(
        player: Civilization, mission: AgencyMission, target: Civilization, city: City?,
        secondary: String, careful: Boolean
    ): String? {
        if (!isAvailable(player) || !player.isCurrentPlayer() || target !in targets(player))
            return "The target is unavailable."
        val data = player.magalanaduAgency ?: MagalanaduAgencyData().also { player.magalanaduAgency = it }
        if (data.operations.size >= Slots) return "All three operation slots are occupied."
        if (data.operations.any { it.civId == target.civID }) return "An operation is already active in this civilization."
        val net = network(player, target)
        if (net.access < mission.access || net.leverage < mission.leverage)
            return "Requires ${mission.access} access and ${mission.leverage} leverage."
        if (mission.target in listOf(AgencyTarget.City, AgencyTarget.Secession) && city !in target.cities)
            return "The city is unavailable."
        if (mission.target == AgencyTarget.Pair && partners(player, target).none { it.civID == secondary })
            return "The two foreign nations must know each other."
        if (mission.target == AgencyTarget.Secession &&
            (city == null || !MagalanaduSecession.canTarget(player, target) ||
                !MagalanaduSecession.canSecede(target, city) ||
                eligibleNations(player).none { it.name == secondary }))
            return "The city or breakaway identity is unavailable."
        if (mission in listOf(AgencyMission.Interrogate, AgencyMission.TurnAgent) && !net.captive)
            return "This mission requires a captive from a successful counterintelligence sweep."
        if (mission == AgencyMission.Counterintel && net.captive)
            return "Your network already holds a captive from this civilization."
        if (mission in listOf(AgencyMission.Counterintel, AgencyMission.Expel) && !player.gameInfo.isEspionageEnabled())
            return "Native spies are disabled in this game."
        if ((mission == AgencyMission.Station && net.station) || (mission == AgencyMission.Smuggling && net.route))
            return "This network already has that facility."
        if (player.gold < cost(mission, careful)) return "Insufficient Gold."
        player.addGold(-cost(mission, careful))
        data.serial++
        data.operations.add(AgencyOperation(
            data.serial, mission.name, target.civID, city?.id.orEmpty(), secondary, careful,
            player.gameInfo.turns + duration(mission, careful)
        ))
        return null
    }

    fun eligibleNations(player: Civilization) =
        MagalanaduSecession.availableNations(player, false) + MagalanaduSecession.availableNations(player, true)

    fun abort(player: Civilization, serial: Int) {
        if (!isAvailable(player) || !player.isCurrentPlayer()) return
        val data = player.magalanaduAgency ?: return
        val op = data.operations.firstOrNull { it.serial == serial } ?: return
        data.operations.remove(op)
        report(player, data, "${op.mission()?.title ?: "Operation"} aborted. Funding was spent.")
    }

    fun layLow(player: Civilization, serial: Int) {
        if (!isAvailable(player) || !player.isCurrentPlayer()) return
        val data = player.magalanaduAgency ?: return
        val index = data.operations.indexOfFirst { it.serial == serial && !it.postponed }
        if (index < 0) return
        val op = data.operations[index]
        val net = data.networks.getOrPut(op.civId) { AgencyNetwork() }
        net.heat = (net.heat - 15).coerceAtLeast(0)
        data.operations[index] = op.copy(readyTurn = op.readyTurn + 2, postponed = true)
    }

    fun processTurn(player: Civilization) {
        val data = player.magalanaduAgency ?: return
        if (!isAvailable(player)) return
        for (net in data.networks.values) net.heat = (net.heat - 4).coerceAtLeast(0)
        val due = data.operations.filter { it.readyTurn <= player.gameInfo.turns }
        for (op in due) {
            data.operations.remove(op)
            val mission = op.mission() ?: continue
            val target = player.gameInfo.getCivilizationOrNull(op.civId)
            val label = "${mission.title} in ${target?.civName ?: op.civId}"
            val city = target?.cities?.firstOrNull { it.id == op.cityId }
            val needsCity = mission.target == AgencyTarget.City || mission.target == AgencyTarget.Secession
            if (target == null || target.isDefeated() || (needsCity && city == null)) {
                report(player, data, "$label aborted. Target changed before execution.")
                continue
            }
            val net = data.networks.getOrPut(target.civID) { AgencyNetwork() }
            if (net.access < mission.access || net.leverage < mission.leverage) {
                report(player, data, "$label aborted. Required network access or leverage was lost.")
                continue
            }
            val random = Random(player.gameInfo.gameId.hashCode() xor op.serial xor player.civID.hashCode())
            val succeeded = random.nextInt(100) < chance(mission, net, op.careful)
            val exposed = random.nextInt(100) < exposure(mission, net, op.careful)
            val result = if (succeeded) execute(player, target, city, op, mission, net)
                else "Failed before reaching the objective."
            net.heat = (net.heat + if (exposed) 28 else 8).coerceAtMost(100)
            if (exposed) {
                net.access = (net.access - 1).coerceAtLeast(0)
                target.getDiplomacyManager(player)?.addModifier(DiplomaticModifiers.SpiedOnUs, -15f, -60f)
                target.addNotification("A Magalanadu operation was exposed in our territory.", NotificationCategory.Espionage)
            }
            report(player, data, "$label. $result" + if (exposed) " Exposed. Network access lost." else "")
        }
    }

    private fun report(player: Civilization, data: MagalanaduAgencyData, message: String) {
        data.reports.add(0, "Turn ${player.gameInfo.turns}. $message")
        while (data.reports.size > ReportLimit) data.reports.removeAt(data.reports.lastIndex)
        player.addNotification(message, NotificationCategory.Espionage)
    }

    private fun execute(
        player: Civilization, target: Civilization, city: City?, op: AgencyOperation,
        mission: AgencyMission, net: AgencyNetwork
    ): String {
        val second = if (mission.target == AgencyTarget.Pair)
            player.gameInfo.getCivilizationOrNull(op.secondaryId)?.takeIf { it in partners(player, target) }
        else null
        if (mission.target == AgencyTarget.Pair && second == null) return "The second nation is unavailable."
        return when (mission) {
            AgencyMission.Surveillance -> {
                city!!.getCenterTile().getTilesInDistance(2).forEach { it.setExplored(player, true) }
                "Revealed terrain within two tiles of ${city.name}."
            }
            AgencyMission.Intercepts -> {
                val wars = target.getCivsAtWarWith().map { it.civName }.sorted()
                val tradePartners = target.getKnownCivs().filter {
                    target.getDiplomacyManager(it)?.trades?.isNotEmpty() == true
                }.map { it.civName }.sorted().toList()
                val resources = target.getCivResourceSupply().filter {
                    it.amount > 0 && it.resource.resourceType == ResourceType.Strategic
                }.map { "${it.resource.name} ${it.amount}" }.sorted()
                "Wars: ${brief(wars)}. Active trade: ${brief(tradePartners)}. Strategic supply: ${brief(resources)}."
            }
            AgencyMission.Recon -> {
                val army = target.units.getCivUnits().filter { it.isMilitary() }.toList()
                val groups = army.groupingBy { it.name }.eachCount().entries.sortedByDescending { it.value }
                    .map { "${it.value} ${it.key}" }
                val strongest = army.maxByOrNull { it.baseUnit.cost }
                val position = strongest?.getTile()?.position
                "Military units: ${army.size}. ${brief(groups)}. Highest-cost unit: ${strongest?.name ?: "none"}" +
                    (if (position != null) " near $position." else ".")
            }
            AgencyMission.Scientific -> scientific(player, target)
            AgencyMission.BreakIn -> {
                net.leverage = (net.leverage + 2).coerceAtMost(6)
                "Archived documents recovered. Leverage is now ${net.leverage}."
            }
            AgencyMission.Interrogate -> {
                net.captive = false
                net.leverage = (net.leverage + 2).coerceAtMost(6)
                "Captive debriefed. Leverage is now ${net.leverage}. ${scientific(player, target)}"
            }
            AgencyMission.Recruit -> {
                net.access = (net.access + 1).coerceAtMost(6)
                "Source recruited. Access is now ${net.access}."
            }
            AgencyMission.Mole -> {
                net.access = (net.access + 2).coerceAtMost(6)
                net.leverage = (net.leverage + 1).coerceAtMost(6)
                "Mole installed. Access ${net.access}, leverage ${net.leverage}."
            }
            AgencyMission.Station -> {
                net.station = true
                "Station operational. Future operations receive +7 success points."
            }
            AgencyMission.Smuggling -> {
                net.route = true
                "Route established. Future operations receive -10 exposure points."
            }
            AgencyMission.Safehouse -> {
                net.cover = (net.cover + 2).coerceAtMost(6)
                net.heat = (net.heat - 20).coerceAtLeast(0)
                "Safehouse ready. Cover is now ${net.cover}."
            }
            AgencyMission.Exfiltrate -> {
                net.access = (net.access - 1).coerceAtLeast(0)
                net.heat = (net.heat - 45).coerceAtLeast(0)
                "Compromised assets recalled. Network heat lowered."
            }
            AgencyMission.TurnAgent -> {
                net.captive = false
                net.access = (net.access + 2).coerceAtMost(6)
                net.cover = (net.cover + 1).coerceAtMost(6)
                "Agent turned. Access ${net.access}, cover ${net.cover}."
            }
            AgencyMission.Counterintel, AgencyMission.Expel -> sweep(player, target, net, mission)
            AgencyMission.Propaganda -> {
                val relation = target.getDiplomacyManager(player) ?: return "Diplomatic contact lost."
                if (target.isCityState) {
                    if (target.isAtWarWith(player)) return "City-State influence is unavailable during war."
                    relation.addInfluence(25f)
                    "Gained 25 City-State influence."
                } else {
                    relation.addModifier(DiplomaticModifiers.GaveUsGifts, 20f, 60f)
                    "Improved the target's opinion of Magalanadu."
                }
            }
            AgencyMission.Leak -> {
                val witnesses = target.getKnownCivs().filter { it.isMajorCiv && !it.isDefeated() && it != player }.toList()
                if (witnesses.isEmpty()) return "No foreign audience had contact with the target."
                net.leverage--
                for (witness in witnesses)
                    witness.getDiplomacyManager(target)?.addModifier(DiplomaticModifiers.WarMongerer, -15f, -60f)
                "Scandal reached ${witnesses.size} civilizations."
            }
            AgencyMission.Blackmail -> {
                if (target.gold <= 0) return "No funds were available to extort."
                net.leverage--
                transferGold(player, target, 400)
            }
            AgencyMission.Disinfo -> {
                target.getDiplomacyManager(second!!)?.addModifier(DiplomaticModifiers.Denunciation, -30f, -90f)
                second.getDiplomacyManager(target)?.addModifier(DiplomaticModifiers.Denunciation, -30f, -90f)
                "Damaged relations between both civilizations."
            }
            AgencyMission.FalseFlag -> {
                val capital = target.getCapital() ?: return "The target no longer has a capital."
                val damage = sabotageProduction(capital)
                if (damage == 0) return "The capital had no stored production to sabotage."
                target.getDiplomacyManager(second!!)?.addModifier(DiplomaticModifiers.SpiedOnUs, -35f, -90f)
                "Removed $damage Production in ${capital.name}. ${second.civName} was blamed."
            }
            AgencyMission.Bribe -> {
                val relation = target.getDiplomacyManager(player) ?: return "Diplomatic contact lost."
                target.addGold(100)
                if (target.isCityState) relation.addInfluence(15f)
                else relation.addModifier(DiplomaticModifiers.GaveUsGifts, 12f, 60f)
                "Delivered 100 Gold and increased goodwill."
            }
            AgencyMission.Mediate -> {
                if (!target.isAtWarWith(second!!)) return "The two civilizations are already at peace."
                if (lockedDiplomacy(player)) return "The active ruleset locks diplomatic relations."
                val trade = TradeLogic(target, second)
                trade.currentTrade.ourOffers.add(TradeOffer(Constants.peaceTreaty, TradeOfferType.Treaty, speed = player.gameInfo.speed))
                trade.currentTrade.theirOffers.add(TradeOffer(Constants.peaceTreaty, TradeOfferType.Treaty, speed = player.gameInfo.speed))
                trade.acceptTrade(false)
                "Both parties signed a peace treaty."
            }
            AgencyMission.Embargo -> disruptTrade(target, second!!)
            AgencyMission.StealTech -> {
                val tech = player.espionageManager.getTechsToSteal(target).sorted().firstOrNull()
                    ?: return "No stealable technology met Magalanadu's prerequisites."
                player.tech.addTechnology(tech, false)
                "Acquired $tech."
            }
            AgencyMission.Factory -> "Removed ${sabotageProduction(city!!)} stored Production in ${city.name}."
            AgencyMission.Infrastructure -> {
                val tile = city!!.getTiles().firstOrNull { !it.isCityCenter() && it.getOwner() == target && it.canPillageTile() }
                    ?: return "No eligible improvement or road in the city territory."
                val name = tile.getImprovementToPillageName() ?: "infrastructure"
                tile.setPillaged()
                city.cityStats.update()
                "Sabotaged $name near ${city.name}."
            }
            AgencyMission.ResearchSabotage -> {
                val tech = target.tech.currentTechnologyName() ?: return "The target had no active research."
                val before = target.tech.techsInProgress[tech] ?: 0
                val loss = before / 2
                if (loss > 0) target.tech.techsInProgress[tech] = before - loss
                "Removed $loss Science stored toward $tech."
            }
            AgencyMission.Treasury -> transferGold(player, target, 300)
            AgencyMission.Assassinate -> {
                val victim = city!!.getTiles().flatMap { it.getUnits() }.firstOrNull { it.civ == target && it.isGreatPerson() }
                    ?: return "No Great Person remained in the target city's territory."
                val name = victim.name
                victim.destroy()
                "$name eliminated."
            }
            AgencyMission.Unrest -> {
                if (MagalanaduSecession.foment(player, target, listOf(city!!)) == 0)
                    return "This target is ineligible for unrest."
                "Resistance started in ${city.name}."
            }
            AgencyMission.Coup -> {
                val capital = target.getCapital() ?: return "The target no longer has a capital."
                if (!target.isMajorCiv || city == capital || city?.isInResistance() != true)
                    return "A coup requires a major civilization and a resisting city other than its current capital."
                net.leverage--
                target.moveCapitalTo(city, capital)
                MagalanaduSecession.foment(player, target, listOf(capital))
                target.cache.updateCitiesConnectedToCapital()
                "The seat of government moved from ${capital.name} to ${city.name}."
            }
            AgencyMission.Secession -> {
                val nation = player.gameInfo.ruleset.nations[op.secondaryId]
                    ?: return "The selected nation is unavailable."
                if (!MagalanaduSecession.secede(player, target, city!!, nation, nation.isCityState))
                    return "Secession was blocked. Resistance, city eligibility or the unused identity changed."
                "${city.name} became independent as ${nation.name}."
            }
            AgencyMission.ArmsSupport -> {
                if (target.isAtWarWith(player)) return "Magalanadu is at war with the recipient."
                val site = city!!
                val unit = site.cityConstructions.getConstructableUnits()
                    .filter { it.isMilitary && it.isLandUnit }
                    .maxByOrNull { it.cost } ?: return "No buildable land unit was available."
                if (target.units.placeUnitNearTile(site.location, unit) == null)
                    return "The recipient had no legal deployment tile."
                "${target.civName} received a ${unit.name} near ${site.name}."
            }
            AgencyMission.ProxyWar -> {
                if (lockedDiplomacy(player)) return "The active ruleset locks diplomatic relations."
                val relation = target.getDiplomacyManager(second!!) ?: return "Diplomatic contact was lost."
                if (!relation.canDeclareWar()) return "War is blocked by an active treaty or existing conflict."
                net.leverage--
                relation.declareWar()
                "${target.civName} declared war on ${second.civName}."
            }
        }
    }

    private fun brief(items: List<String>): String =
        if (items.isEmpty()) "none" else items.take(8).joinToString() + if (items.size > 8) " and more" else ""

    private fun scientific(player: Civilization, target: Civilization): String =
        "Current research: ${target.tech.currentTechnologyName() ?: "none"}. " +
            "Stealable technologies: ${brief(player.espionageManager.getTechsToSteal(target).sorted())}."

    private fun lockedDiplomacy(player: Civilization) =
        player.gameInfo.ruleset.modOptions.hasUnique(UniqueType.DiplomaticRelationshipsCannotChange)

    private fun sweep(player: Civilization, target: Civilization, net: AgencyNetwork, mission: AgencyMission): String {
        val spy = target.espionageManager.spyList.firstOrNull { it.getCityOrNull()?.civ == player }
            ?: return "The sweep found no active spy in Magalanadu."
        val name = spy.name
        spy.addNotification("Our spy [$name] was intercepted in Magalanadu.")
        spy.moveTo(null)
        if (mission == AgencyMission.Expel) return "$name expelled to the rival's hideout."
        spy.setAction(SpyAction.Dead, 5) // Reuse the native temporary replacement countdown.
        net.captive = true
        return "$name captured. A captive is available for interrogation or recruitment."
    }

    private fun sabotageProduction(city: City): Int {
        val project = city.cityConstructions.currentConstructionName()
        if (project.isEmpty()) return 0
        val stored = city.cityConstructions.getWorkDone(project)
        val loss = stored / 2
        if (loss > 0) city.cityConstructions.inProgressConstructions[project] = stored - loss
        return loss
    }

    private fun transferGold(player: Civilization, target: Civilization, limit: Int): String {
        val gold = minOf(limit, target.gold.coerceAtLeast(0))
        target.addGold(-gold)
        player.addGold(gold)
        return "Transferred $gold Gold from the target."
    }

    private fun disruptTrade(target: Civilization, other: Civilization): String {
        val relation = target.getDiplomacyManager(other) ?: return "Diplomatic contact was lost."
        val reverse = relation.otherCivDiplomacy()
        val commercial = setOf(TradeOfferType.Gold_Per_Turn, TradeOfferType.Strategic_Resource, TradeOfferType.Luxury_Resource)
        val trades = relation.trades.filter { trade ->
            val offers = trade.ourOffers + trade.theirOffers
            offers.any { it.duration > 0 && it.type in commercial } &&
                offers.none { it.type == TradeOfferType.Treaty || it.type == TradeOfferType.Agreement }
        }
        var cancelled = 0
        for (trade in trades) {
            val reversedTrade = trade.reverse()
            val matching = reverse.trades.firstOrNull { it.equalTrade(reversedTrade) } ?: continue
            reverse.trades.remove(matching)
            relation.trades.remove(trade)
            cancelled++
        }
        for (side in listOf(relation, reverse)) side.updateHasOpenBorders()
        for (civ in listOf(target, other)) {
            civ.cache.updateCivResources()
            civ.updateStatsForNextTurn()
        }
        return "Cancelled $cancelled commercial deals."
    }
}
