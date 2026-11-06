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
import com.unciv.models.ruleset.unique.UniqueType
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
        popup.addButton("FOREIGN RESOURCE RIGHTS: choose supplier or bulk acquisition") {
            popup.close()
            selectCiv(user, "Choose resource supplier", { it.isMajorCiv || it.isCityState }) { supplier ->
                selectResource(user, supplier)
            }
        }.row()
        // MAGALANADU_V4_5_GLOBAL_RESOURCES: optional bulk transfer from known suppliers.
        popup.addButton("ACQUIRE ALL RESOURCES: every known civilization / City-State") {
            popup.close()
            selectGlobalResourceDuration(user)
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

    /** Returns available, non-stockpiled, game-tradable quantities, net of existing trade
     *  commitments. A resource already acquired therefore cannot be acquired twice.
     *  Standard Unciv trade records do not support Bonus or stockpiled resources.
     */
    private fun availableResourceBundle(supplier: Civilization): Map<String, Int> =
        supplier.getCivResourceSupply()
            .asSequence()
            .filter { !it.resource.isStockpiled &&
                !it.resource.hasUnique(UniqueType.CannotBeTraded, supplier.state) &&
                (it.resource.resourceType == ResourceType.Strategic ||
                 it.resource.resourceType == ResourceType.Luxury) }
            .groupBy { it.resource.name }
            .mapValues { entry -> entry.value.sumOf { it.amount } }
            .filterValues { it > 0 }
            .toSortedMap()

    private fun selectResource(player: Civilization, supplier: Civilization) {
        if (supplier.isAtWarWith(player)) {
            message("Resource agreements are unavailable while at war with the supplier.")
            return
        }
        val available = availableResourceBundle(supplier)
        val popup = newPopup("RESOURCE RIGHTS: ${supplier.civName}")
        popup.addGoodSizedLabel("Acquire one resource or ALL available resources at once. Transfers are real bilateral trade contracts. Only non-stockpiled strategic and luxury resources can be traded.").row()
        if (available.isEmpty()) popup.addGoodSizedLabel("No available tradable resources. Existing concessions may already use the supply.").row()
        else {
            popup.addButton("ACQUIRE ALL ${available.size} RESOURCE TYPES (30 turns)") {
                popup.close()
                confirmResourceBundle(player, supplier, RESOURCE_TURNS)
            }.row()
            popup.addButton("ACQUIRE ALL ${available.size} RESOURCE TYPES (9,999 turns)") {
                popup.close()
                confirmResourceBundle(player, supplier, RESOURCE_LONG_TERM_TURNS)
            }.row()
        }
        for ((resource, count) in available) {
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
        val current = availableResourceBundle(supplier)[resourceName] ?: 0
        popup.addGoodSizedLabel("Available: $current. Choose quantity and duration.").row()
        if (current > 0) {
            for (duration in listOf(RESOURCE_TURNS, RESOURCE_LONG_TERM_TURNS)) {
                popup.addButton("ACQUIRE ALL $current $resourceName ($duration turns)") {
                    popup.close()
                    val transferred = acquireResourceBundle(player, supplier, mapOf(resourceName to current), duration)
                    message(if (transferred > 0)
                        "Transferred all $transferred $resourceName from ${supplier.civName} to Magalanadu for $duration turns."
                    else "Transfer failed: available supply or diplomatic conditions changed.")
                }.row()
            }
        }
        for (quantity in listOf(1, 5, 10, 25).filter { it <= current }) {
            for (duration in listOf(RESOURCE_TURNS, RESOURCE_LONG_TERM_TURNS)) {
                popup.addButton("$quantity $resourceName ($duration turns)") {
                    popup.close()
                    val transferred = acquireResourceBundle(player, supplier, mapOf(resourceName to quantity), duration)
                    message(if (transferred == quantity)
                        "Contract active: $quantity $resourceName for $duration turns from ${supplier.civName}."
                    else "Transfer failed: supply or diplomatic conditions changed.")
                }.row()
            }
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun confirmResourceBundle(player: Civilization, supplier: Civilization, duration: Int) {
        val available = availableResourceBundle(supplier)
        val popup = newPopup("ACQUIRE ALL: ${supplier.civName}")
        popup.addGoodSizedLabel("Transfer all ${available.size} available resource types (${available.values.sum()} total units) for $duration turns. This deducts resources from ${supplier.civName}, creates ONE persistent trade contract, and cannot be undone by this menu.").row()
        for ((name, amount) in available) popup.addGoodSizedLabel("$name: $amount").row()
        if (available.isNotEmpty()) popup.addButton("CONFIRM: ACQUIRE EVERYTHING") {
            popup.close()
            // Re-read at confirmation time so stale menu quantities cannot overdraw.
            val actual = availableResourceBundle(supplier)
            val transferred = acquireResourceBundle(player, supplier, actual, duration)
            message(if (transferred > 0)
                "Acquired $transferred resource units from ${supplier.civName} in one contract for $duration turns."
            else "No resources transferred. Check war status, availability and existing contracts.")
        }.row()
        popup.addCloseButton().row()
        popup.open()
    }

    /** Optional GLOBAL action; only nations discovered by Magalanadu can be targeted.
     *  One bilateral contract per supplier, not one contract per resource.
     */
    private fun selectGlobalResourceDuration(player: Civilization) {
        val popup = newPopup("GLOBAL RESOURCE ACQUISITION")
        val suppliers = eligibleBulkSuppliers(player)
        val totalTypes = suppliers.sumOf { availableResourceBundle(it).size }
        popup.addGoodSizedLabel("Eligible suppliers: ${suppliers.size}; resource positions: $totalTypes. Acquires all CURRENT net tradable strategic and luxury resources from every known non-hostile civilization and City-State. Existing contracts are respected.").row()
        if (totalTypes > 0) {
            popup.addButton("ACQUIRE ALL: 30-turn contracts") {
                popup.close()
                confirmGlobalResourceBundle(player, RESOURCE_TURNS)
            }.row()
            popup.addButton("ACQUIRE ALL: 9,999-turn contracts") {
                popup.close()
                confirmGlobalResourceBundle(player, RESOURCE_LONG_TERM_TURNS)
            }.row()
        } else popup.addGoodSizedLabel("No currently available resource supplies from eligible nations.").row()
        popup.addCloseButton().row()
        popup.open()
    }

    private fun eligibleBulkSuppliers(player: Civilization): List<Civilization> =
        player.getKnownCivs()
            .filter { it != player && !it.isDefeated() && !it.isAtWarWith(player) &&
                (it.isMajorCiv || it.isCityState) }
            .sortedBy { it.civName }.toList()

    private fun confirmGlobalResourceBundle(player: Civilization, duration: Int) {
        val eligible = eligibleBulkSuppliers(player)
        val total = eligible.sumOf { availableResourceBundle(it).values.sum() }
        val popup = newPopup("CONFIRM GLOBAL RESOURCE RIGHTS")
        popup.addGoodSizedLabel("This will acquire up to $total resource units from ${eligible.size} discovered eligible nations for $duration turns. All valid transfers are real trade agreements; the action will NOT annex cities or alter map tiles.").row()
        popup.addButton("CONFIRM: ACQUIRE FROM ALL") {
            popup.close()
            var totalReceived = 0
            var supplierCount = 0
            for (supplier in eligibleBulkSuppliers(player)) {
                val bundle = availableResourceBundle(supplier)
                if (bundle.isEmpty()) continue
                val received = acquireResourceBundle(player, supplier, bundle, duration)
                if (received > 0) {
                    supplierCount++
                    totalReceived += received
                }
            }
            message("Global acquisition complete: $totalReceived total resource units acquired from $supplierCount civilizations / City-States for $duration turns. Unavailable or hostile suppliers were skipped.")
        }.row()
        popup.addCloseButton().row()
        popup.open()
    }

    /** Atomic bilateral record per supplier with many resource offers. No net overdrawing,
     *  no duplicated concessions for already-exported resources, and no bonus-resource tricks.
     *  Return the total number of actual resource units committed.
     */
    private fun acquireResourceBundle(
        player: Civilization,
        supplier: Civilization,
        requested: Map<String, Int>,
        duration: Int
    ): Int {
        if (player == supplier || supplier.isDefeated() || supplier.isAtWarWith(player) ||
            duration !in listOf(RESOURCE_TURNS, RESOURCE_LONG_TERM_TURNS)) return 0
        val playerDiplo = player.getDiplomacyManager(supplier) ?: return 0
        val supplierDiplo = supplier.getDiplomacyManager(player) ?: return 0
        val stillAvailable = availableResourceBundle(supplier)
        val trade = Trade()
        var total = 0
        for ((name, quantity) in requested) {
            if (quantity <= 0) continue
            val resource = player.gameInfo.ruleset.tileResources[name] ?: continue
            if (resource.isStockpiled) continue
            val available = stillAvailable[name] ?: 0
            // If the menu's requested quantity went stale, do not silently
            // transfer a partial quantity and report it as a failure.
            if (available < quantity) return 0
            val amount = quantity
            val offerType = when (resource.resourceType) {
                ResourceType.Luxury -> TradeOfferType.Luxury_Resource
                ResourceType.Strategic -> TradeOfferType.Strategic_Resource
                else -> continue
            }
            trade.theirOffers.add(TradeOffer(name, offerType, amount, duration))
            total += amount
        }
        if (total == 0) return 0
        // The mirror record is created before either side is mutated.
        val mirror = trade.reverse()
        playerDiplo.trades.add(trade)
        supplierDiplo.trades.add(mirror)
        supplier.cache.updateCivResources()
        player.cache.updateCivResources()
        return total
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
