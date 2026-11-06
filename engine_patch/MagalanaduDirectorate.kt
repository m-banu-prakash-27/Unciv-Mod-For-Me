package com.unciv.ui.popups

import com.unciv.Constants
import com.unciv.GUI
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.city.City
import com.unciv.logic.civilization.diplomacy.DiplomaticModifiers
import com.unciv.logic.map.mapunit.MapUnit
import com.unciv.logic.trade.Trade
import com.unciv.logic.trade.TradeOffer
import com.unciv.logic.trade.TradeOfferType
import com.unciv.models.ruleset.tile.ResourceType
import kotlin.random.Random

/**
 * Magalanadu v4.0 Strategic Directorate: actual game-state operations.
 * This UI is only available to the human player controlling Magalanadu.
 * All persistent economic contracts use stock Unciv's serializable trade records.
 */
object MagalanaduDirectorate {
    private const val CONTRACT_TURNS = 20
    private const val RESOURCE_TURNS = 30
    private const val RESOURCE_LONG_TERM_TURNS = 9999

    fun open(selectedUnit: MapUnit) {
        val user = selectedUnit.civ
        if (user.civName != "Magalanadu" || !user.isCurrentPlayer()) return
        val popup = newPopup("MAGALANADU STRATEGIC DIRECTORATE")
        popup.addGoodSizedLabel("Select an operation. Orders change real diplomacy, resource supply, and treasuries.").row()
        popup.addButton("PROXY WAR: A declares war on B") {
            popup.close()
            selectCiv(user, "Choose ATTACKER civilization", { it.isMajorCiv }) { attacker ->
                selectCiv(user, "Choose TARGET of ${attacker.civName}", {
                    it != attacker && it.isMajorCiv && attacker.knows(it)
                }) { defender ->
                    proxyWar(user, attacker, defender)
                }
            }
        }.row()
        popup.addButton("FOREIGN RESOURCE RIGHTS: lease or 9,999 turns") {
            popup.close()
            selectCiv(user, "Choose resource supplier", { it.isMajorCiv || it.isCityState }) { supplier ->
                selectResource(user, supplier)
            }
        }.row()
        popup.addButton("SABOTAGE: delay a foreign city's current project") {
            popup.close()
            selectCiv(user, "Choose a foreign civilization", { it.isMajorCiv }) { victim ->
                selectCity(user, victim)
            }
        }.row()
        popup.addButton("DISINFORMATION: damage A-B relations") {
            popup.close()
            selectCiv(user, "Choose first rival", { it.isMajorCiv }) { first ->
                selectCiv(user, "Choose rival of ${first.civName}", {
                    it != first && it.isMajorCiv && first.knows(it)
                }) { second ->
                    val one = first.getDiplomacyManager(second)
                    val two = second.getDiplomacyManager(first)
                    if (one == null || two == null) message("Civilizations must know each other.")
                    else {
                        one.addModifier(DiplomaticModifiers.Denunciation, -40f, -100f)
                        two.addModifier(DiplomaticModifiers.Denunciation, -40f, -100f)
                        message("Disinformation succeeded: ${first.civName} and ${second.civName} now hold stronger negative diplomatic opinions of each other. This does not directly declare war.")
                    }
                }
            }
        }.row()
        popup.addButton("COVERT TREASURY: extract actual Gold") {
            popup.close()
            selectCiv(user, "Choose treasury target", { it.isMajorCiv }) { victim ->
                treasuryOperation(user, victim)
            }
        }.row()
        popup.addButton("ARMS CONTRACTS: donate a military unit") {
            popup.close()
            message("Move a Magalanadu military unit into or next to a friendly major civilization. Select the unit and choose 'Arms contract to [Civilization]'. The recipient will pay 20 turns of Gold-per-turn after receiving the unit.")
        }.row()
        popup.addCloseButton().row()
        popup.open()
    }

    private fun newPopup(title: String): Popup {
        val popup = Popup(GUI.getWorldScreen(), Popup.Scrollability.All)
        popup.addGoodSizedLabel(title).row()
        return popup
    }

    private fun message(text: String) {
        val popup = newPopup("STRATEGIC DIRECTORATE")
        popup.addGoodSizedLabel(text).row()
        popup.addCloseButton().row()
        popup.open()
    }

    private fun selectCiv(
        player: Civilization,
        title: String,
        eligible: (Civilization) -> Boolean,
        onChosen: (Civilization) -> Unit
    ) {
        val popup = newPopup(title)
        val possible = player.getKnownCivs()
            .filter { it != player && !it.isDefeated() && eligible(it) }
            .sortedBy { it.civName }
            .toList()
        if (possible.isEmpty()) popup.addGoodSizedLabel("No eligible civilization discovered.").row()
        for (c in possible) {
            popup.addButton(c.civName) {
                popup.close()
                onChosen(c)
            }.row()
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun proxyWar(player: Civilization, attacker: Civilization, defender: Civilization) {
        val declaration = attacker.getDiplomacyManager(defender)
        val popup = newPopup("PROXY WAR: ${attacker.civName} vs ${defender.civName}")
        if (declaration?.canDeclareWar() != true) {
            popup.addGoodSizedLabel("War cannot be declared now. They may already be fighting, or a peace treaty may still be active.").row()
        } else {
            popup.addGoodSizedLabel("This directly orders ${attacker.civName} to declare war on ${defender.civName}. Magalanadu does not automatically join. Existing pacts can still affect who joins.").row()
            popup.addButton("FORCE WAR NOW") {
                popup.close()
                if (declaration.canDeclareWar()) {
                    declaration.declareWar()
                    val fee = minOf(250, attacker.gold.coerceAtLeast(0))
                    if (fee > 0) {
                        attacker.addGold(-fee)
                        player.addGold(fee)
                    }
                    message("War declared: ${attacker.civName} vs ${defender.civName}. Magalanadu received $fee Gold in consulting fees from the attacker.")
                } else message("War is no longer available. No change made.")
            }.row()
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun selectResource(player: Civilization, supplier: Civilization) {
        if (supplier.isAtWarWith(player)) {
            message("Resource agreements are unavailable while at war with the supplier.")
            return
        }
        val available = supplier.getCivResourceSupply()
            .filter { it.amount > 0 && !it.resource.isStockpiled &&
                it.resource.resourceType in setOf(ResourceType.Strategic, ResourceType.Luxury) }
            .groupBy { it.resource.name }
            .mapValues { (_, supplies) -> supplies.sumOf { it.amount } }
            .filter { it.value > 0 }
        val popup = newPopup("RESOURCE RIGHTS: ${supplier.civName}")
        popup.addGoodSizedLabel("Force a 30-turn lease or 9,999-turn long-term concession. Supply is deducted from the supplier and added to Magalanadu. Contracts can terminate if the supplier runs out.").row()
        if (available.isEmpty()) popup.addGoodSizedLabel("No available strategic or luxury resource stock.").row()
        for ((resource, count) in available.toSortedMap()) {
            popup.addButton("$resource: $count available") {
                popup.close()
                selectQuantity(player, supplier, resource)
            }.row()
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun selectQuantity(player: Civilization, supplier: Civilization, resourceName: String) {
        val popup = newPopup("$resourceName concessions")
        val current = supplier.getCivResourceSupply().sumBy(resourceName).coerceAtLeast(0)
        popup.addGoodSizedLabel("Available: $current. Select quantity and duration.").row()
        for (quantity in listOf(1, 5, 10, 25).filter { it <= current }) {
            for (duration in listOf(RESOURCE_TURNS, RESOURCE_LONG_TERM_TURNS)) {
                val term = if (duration == RESOURCE_TURNS) "30-turn lease" else "9,999-turn control"
                popup.addButton("$quantity $resourceName: $term") {
                    popup.close()
                    val ok = acquireResources(player, supplier, resourceName, quantity, duration)
                    message(if (ok) "Contract active: +$quantity $resourceName to Magalanadu for $duration turns, deducted from ${supplier.civName}." else "Transfer failed: supply or diplomatic conditions changed.")
                }.row()
            }
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun acquireResources(player: Civilization, supplier: Civilization, name: String, amount: Int, duration: Int): Boolean {
        if (player == supplier || amount <= 0 || supplier.isDefeated() || supplier.isAtWarWith(player)) return false
        val resource = player.gameInfo.ruleset.tileResources[name] ?: return false
        if (resource.isStockpiled || resource.resourceType == ResourceType.Bonus) return false
        if (supplier.getCivResourceSupply().sumBy(name) < amount) return false
        val type = if (resource.resourceType == ResourceType.Luxury) TradeOfferType.Luxury_Resource
                   else TradeOfferType.Strategic_Resource
        val transfer = Trade()
        transfer.theirOffers.add(TradeOffer(name, type, amount, duration))
        player.getDiplomacyManager(supplier)?.trades?.add(transfer) ?: return false
        supplier.getDiplomacyManager(player)?.trades?.add(transfer.reverse()) ?: return false
        supplier.cache.updateCivResources()
        player.cache.updateCivResources()
        return true
    }

    private fun selectCity(player: Civilization, victim: Civilization) {
        val popup = newPopup("SABOTAGE: ${victim.civName}")
        popup.addGoodSizedLabel("Select a city to sabotage. This removes half of its stored construction progress when successful.").row()
        for (city in victim.cities.sortedBy { it.name }) {
            popup.addButton(city.name) {
                popup.close()
                sabotageCity(player, city)
            }.row()
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun sabotageCity(player: Civilization, city: City) {
        val popup = newPopup("SABOTAGE: ${city.name}")
        popup.addGoodSizedLabel("STEALTH: costs 100 Gold, 75% success. SUPREME: guaranteed and free. Any accumulated production on the city's current project is reduced by half; it does not destroy buildings.").row()
        popup.addButton("STEALTH SABOTAGE (100 Gold)") {
            popup.close()
            if (player.gold < 100 || city.civ.isDefeated()) message("Operation blocked: insufficient funds or city no longer active.")
            else {
                player.addGold(-100)
                if (Random.nextInt(100) < 75) applySabotage(city)
                else message("Sabotage failed: 100 Gold spent, construction progress unchanged.")
            }
        }.row()
        popup.addButton("SUPREME SABOTAGE (GUARANTEED)") {
            popup.close()
            if (city.civ.isDefeated()) message("Target no longer active.")
            else applySabotage(city)
        }.row()
        popup.addCloseButton().row()
        popup.open()
    }

    private fun applySabotage(city: City) {
        val current = city.cityConstructions.currentConstructionName()
        val existing = city.cityConstructions.getWorkDone(current)
        val removed = existing / 2
        if (current.isEmpty() || removed <= 0) {
            message("${city.name} has no accumulated production to sabotage on its current project.")
            return
        }
        city.cityConstructions.inProgressConstructions[current] = existing - removed
        message("Sabotage completed: ${city.name} lost $removed Production of stored progress on $current.")
    }

    private fun treasuryOperation(player: Civilization, victim: Civilization) {
        val popup = newPopup("COVERT TREASURY: ${victim.civName}")
        popup.addGoodSizedLabel("STEALTH: 75% chance to seize up to 300 Gold; costs 50 Gold, even on failure. SUPREME: guaranteed seizure of up to 1,000 Gold and no operating cost. Both transfer real Gold from the target.").row()
        popup.addButton("STEALTH OPERATION (50 Gold)") {
            popup.close()
            if (player.gold < 50 || victim.isDefeated()) {
                message("Cannot operate: Magalanadu needs 50 Gold and the target must be active.")
            } else {
                player.addGold(-50)
                if (Random.nextInt(100) < 75) {
                    val seized = minOf(300, victim.gold.coerceAtLeast(0))
                    victim.addGold(-seized)
                    player.addGold(seized)
                    message("Operation succeeded: recovered $seized Gold from ${victim.civName}; 50 Gold spent.")
                } else message("Operation failed. 50 Gold spent; no money transferred.")
            }
        }.row()
        popup.addButton("SUPREME SEIZURE (GUARANTEED)") {
            popup.close()
            if (victim.isDefeated()) message("Target is defeated. No operation performed.")
            else {
                val seized = minOf(1000, victim.gold.coerceAtLeast(0))
                victim.addGold(-seized)
                player.addGold(seized)
                message("Supreme seizure completed: $seized Gold transferred from ${victim.civName} to Magalanadu.")
            }
        }.row()
        popup.addCloseButton().row()
        popup.open()
    }

    /** Uses standard bilateral Trade records so the recipient really pays per turn. */
    fun registerArmsContract(seller: Civilization, buyer: Civilization, productionCost: Int): Int {
        if (seller == buyer || buyer.isDefeated() || buyer.isAtWarWith(seller)) return 0
        val goldPerTurn = (productionCost / 20).coerceIn(5, 250)
        val trade = Trade()
        trade.theirOffers.add(TradeOffer(Constants.goldPerTurn, TradeOfferType.Gold_Per_Turn, goldPerTurn, CONTRACT_TURNS))
        seller.getDiplomacyManager(buyer)?.trades?.add(trade) ?: return 0
        buyer.getDiplomacyManager(seller)?.trades?.add(trade.reverse()) ?: return 0
        seller.updateStatsForNextTurn()
        buyer.updateStatsForNextTurn()
        return goldPerTurn
    }
}
