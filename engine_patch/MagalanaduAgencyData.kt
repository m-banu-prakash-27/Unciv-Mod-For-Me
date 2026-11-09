package com.unciv.logic.civilization

import com.unciv.logic.IsPartOfGameInfoSerialization

enum class AgencyGroup(val title: String) {
    Intel("Intelligence collection"), Network("Agents and networks"), Influence("Influence and diplomacy"),
    Action("Covert action"), Conflict("Insurgency and proxy conflict")
}

enum class AgencyTarget { Country, City, Pair, Secession }

enum class AgencyMission(
    val group: AgencyGroup, val title: String, val effect: String, val target: AgencyTarget,
    val cost: Int, val turns: Int, val chance: Int, val access: Int = 0, val leverage: Int = 0
) {
    Surveillance(AgencyGroup.Intel, "Field surveillance", "Explore the city and nearby tiles.", AgencyTarget.City, 40, 1, 90),
    Intercepts(AgencyGroup.Intel, "Signals interception", "Report wars, trade partners, and available strategic resources.", AgencyTarget.Country, 60, 2, 85),
    Recon(AgencyGroup.Intel, "Military reconnaissance", "Report the army's composition and the location of its strongest unit.", AgencyTarget.Country, 60, 2, 85),
    Scientific(AgencyGroup.Intel, "Scientific dossier", "Report current research and identify stealable technologies.", AgencyTarget.Country, 75, 2, 85),
    BreakIn(AgencyGroup.Intel, "Break into archives", "Obtain two pieces of leverage from the target.", AgencyTarget.City, 80, 2, 72, 1),
    Interrogate(AgencyGroup.Intel, "Interrogate captured agent", "Trade a captured agent for a research report and two pieces of leverage.", AgencyTarget.Country, 45, 1, 92),

    Recruit(AgencyGroup.Network, "Recruit a local source", "Increase network access by one.", AgencyTarget.Country, 55, 2, 86),
    Mole(AgencyGroup.Network, "Plant an agency mole", "Increase access by two and obtain one piece of leverage.", AgencyTarget.Country, 110, 3, 68, 1),
    Station(AgencyGroup.Network, "Open an intelligence station", "Establish a station that improves success odds on future missions.", AgencyTarget.City, 125, 3, 77, 1),
    Smuggling(AgencyGroup.Network, "Open a smuggling route", "Establish a route that lowers future exposure risk.", AgencyTarget.City, 105, 3, 72, 1),
    Safehouse(AgencyGroup.Network, "Prepare a safehouse", "Increase network cover and lower current heat.", AgencyTarget.City, 75, 2, 84, 1),
    Exfiltrate(AgencyGroup.Network, "Exfiltrate compromised assets", "Spend one access to remove up to 45 network heat before exposure is applied.", AgencyTarget.Country, 50, 1, 91, 1),
    TurnAgent(AgencyGroup.Network, "Turn a captured agent", "Trade a captured agent for two access and additional cover.", AgencyTarget.Country, 85, 2, 75, 1),
    Counterintel(AgencyGroup.Network, "Counterintelligence sweep", "Capture a native spy from this rival operating in a Magalanadu city.", AgencyTarget.Country, 90, 2, 78),

    Propaganda(AgencyGroup.Influence, "Broadcast propaganda", "Improve bilateral opinion or gain City-State influence.", AgencyTarget.Country, 100, 3, 75, 1),
    Leak(AgencyGroup.Influence, "Expose a scandal", "Spend leverage to damage the target's reputation with known third parties.", AgencyTarget.Country, 80, 2, 74, 1, 1),
    Blackmail(AgencyGroup.Influence, "Blackmail officials", "Spend leverage to extract up to 400 Gold.", AgencyTarget.Country, 65, 2, 79, 1, 1),
    Disinfo(AgencyGroup.Influence, "Plant disinformation", "Damage the two foreign nations' opinions of each other.", AgencyTarget.Pair, 90, 2, 78, 1),
    FalseFlag(AgencyGroup.Influence, "Stage a false flag", "Blame the second nation for lost production in the target's capital.", AgencyTarget.Pair, 170, 3, 60, 2),
    Bribe(AgencyGroup.Influence, "Bribe intermediaries", "Deliver 100 Gold and improve the recipient's opinion of Magalanadu.", AgencyTarget.Country, 135, 2, 90),
    Mediate(AgencyGroup.Influence, "Backchannel ceasefire", "End the war between the chosen civilizations using native diplomacy.", AgencyTarget.Pair, 155, 3, 69, 1),
    Embargo(AgencyGroup.Influence, "Disrupt a trade corridor", "Cancel active commercial trade between the chosen pair. Treaty deals stay in place.", AgencyTarget.Pair, 125, 3, 70, 2),

    StealTech(AgencyGroup.Action, "Steal technology", "Acquire a researched technology for which Magalanadu meets the prerequisites.", AgencyTarget.Country, 140, 3, 71, 2),
    Factory(AgencyGroup.Action, "Sabotage construction", "Remove half the stored Production on the city's active project.", AgencyTarget.City, 95, 2, 75, 1),
    Infrastructure(AgencyGroup.Action, "Sabotage infrastructure", "Pillage a worked-region improvement or road belonging to this city.", AgencyTarget.City, 105, 2, 72, 1),
    ResearchSabotage(AgencyGroup.Action, "Sabotage research", "Remove half the target's stored progress on its active technology.", AgencyTarget.Country, 115, 3, 70, 2),
    Treasury(AgencyGroup.Action, "Raid the treasury", "Transfer up to 300 Gold from the target treasury.", AgencyTarget.Country, 80, 2, 74, 1),
    Assassinate(AgencyGroup.Action, "Eliminate a Great Person", "Remove a foreign Great Person stationed in the chosen city's territory.", AgencyTarget.City, 185, 3, 61, 2),
    Expel(AgencyGroup.Action, "Expel a hostile spy", "Send a native spy from this rival home from a Magalanadu city.", AgencyTarget.Country, 65, 1, 86),

    Unrest(AgencyGroup.Conflict, "Organize resistance", "Put the selected foreign city into resistance.", AgencyTarget.City, 105, 2, 76, 1),
    Coup(AgencyGroup.Conflict, "Back a capital coup", "Move the seat of government to a resisting city and trigger resistance in the former capital.", AgencyTarget.City, 230, 4, 57, 3, 1),
    Secession(AgencyGroup.Conflict, "Sponsor independence", "Release an eligible resisting city as the chosen unused major nation or City-State.", AgencyTarget.Secession, 200, 4, 62, 2),
    ArmsSupport(AgencyGroup.Conflict, "Arm a proxy", "Provide a buildable land military unit at the recipient's city.", AgencyTarget.City, 145, 2, 86),
    ProxyWar(AgencyGroup.Conflict, "Instigate a proxy war", "Have the first nation declare war on the second, subject to treaty rules.", AgencyTarget.Pair, 220, 4, 61, 2, 1)
}

data class AgencyNetwork(
    var access: Int = 0, var cover: Int = 0, var leverage: Int = 0, var heat: Int = 0,
    var station: Boolean = false, var route: Boolean = false, var captive: Boolean = false
) : IsPartOfGameInfoSerialization

data class AgencyOperation(
    val serial: Int = 0, val missionId: String = "", val civId: String = "",
    val cityId: String = "", val secondaryId: String = "", val careful: Boolean = false,
    val readyTurn: Int = 0, val postponed: Boolean = false
) : IsPartOfGameInfoSerialization {
    fun mission() = AgencyMission.entries.firstOrNull { it.name == missionId }
}

class MagalanaduAgencyData : IsPartOfGameInfoSerialization {
    var serial = 0
    var networks = HashMap<String, AgencyNetwork>()
    var operations = ArrayList<AgencyOperation>()
    var reports = ArrayList<String>()

    fun copy(): MagalanaduAgencyData {
        val result = MagalanaduAgencyData()
        result.serial = serial
        for ((key, network) in networks) result.networks[key] = network.copy()
        result.operations.addAll(operations)
        result.reports.addAll(reports)
        return result
    }
}
