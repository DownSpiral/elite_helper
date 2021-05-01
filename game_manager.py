from datetime import datetime
from terminaltables import AsciiTable
from terminaltables import SingleTable 

from material_manager import MaterialManager
from mission_manager import MissionManager 
from mission_manager import Mission

class GameManager:
    IGNORED_EVENTS = [
        "ReceiveText", "UnderAttack", "ShipTargeted", "ReservoirReplenished", "Docked", "Undocked", "ApproachSettlement", "StartJump", "SupercruiseEntry",
        "NpcCrewPaidWage", "BuyAmmo", "RestockVehicle", "RefuelAll", "SupercruiseExit", "DockingRequested", "DockingGranted", "FSSSignalDiscovered",
        "FSDTarget", "NavRoute", "Interdicted", "DockFighter", "LaunchFighter", "FighterRebuilt", "MaterialDiscovered", "Promotion",
        "SellDrones", "ModuleInfo", "Friends", "Fileheader", "LoadGame", "ModuleSell",
        "EscapeInterdiction",
        "RepairAll",
        "USSDrop",
        "Missions",
        "WingLeave",
        "WingJoin",
        "WingAdd",
        "WingInvite",
        "FSSDiscoveryScan",
        "FSSAllBodiesFound",
        "VehicleSwitch",
        "ShipyardTransfer",
        "ShipyardNew",
        "NpcCrewRank",
        "LaunchDrone",
        "FuelScoop",
        "ModuleBuy",
        "ModuleStore",
        "BuyDrones",
        "EngineerCraft",
        "NavBeaconScan",
        "ApproachBody",
        "CommitCrime",
        "CodexEntry",
        "SAASignalsFound",
        "SAAScanComplete",
        "LeaveBody",
        "LeaveBody",
        "DockingDenied",
        "DockingDenied",
        "CrewMemberRoleChange",
        "CrewMemberJoins",
        "CrewMemberQuits",
        "EndCrewSession",
        "SRVDestroyed",
        "Liftoff",
        "Touchdown",
        "Resurrect",
        "CrewHire",
        "SelfDestruct",
        "Died",
        "LaunchSRV",
        "DockSRV",
        "DatalinkScan",
        "Repair",
        "DataScanned",
        "EngineerContribution",
        "BuyExplorationData",
        "CollectCargo",
        "EjectCargo",
        "ModuleSellRemote",
        "BuyTradeData",
        "SendText",
        "ModuleSwap",
        "ModuleRetrieve",
        "ShipyardSell",
        "CockpitBreached",
        "Powerplay",
        "PowerplayJoin",
        "SquadronStartup",
        "SellExplorationData",
        "PowerplaySalary",
        "TechnologyBroker",
        "SquadronCreated",
        "Interdiction",

        "HeatWarning",
        "HeatDamage",

        # Events to handle
        "Scanned",

        # Handle money updates
        "MarketBuy",
        "MarketSell",

        # Handle exploration
        "Scan",
        "MultiSellExplorationData",

        "FighterDestroyed", # Should be alerted on
        "HullDamage", # Should be alerted on
        "ShieldState",

        "CrewAssign", # Should see this before heading out (or at least if we saw a crew unassign)
        "Loadout", # Useful info to display, happens on ship change

        "StoredShips", # Useful info to display
        "StoredModules", # Useful info to display
        "Outfitting", # Useful info to display

        "Shipyard", # Useful info to display
        "ShipyardBuy", # Useful info to display
        "ShipyardSwap", # Useful info to display
        "Cargo", # Happens on ship change?
        "Location", # Happens on ship change?

        "Market", # Useful info to display at station

        "Commander", # Useful info to display
        "EngineerProgress", # Useful info to display
        "Rank", # Useful info to display
        "Progress", # Useful info to display
        "Reputation", # Useful info to display
        "Statistics", # Useful info to display

        "MaterialCollected", # Use to update material info
        "MaterialTrade", # Use to update material info
        "Synthesis", # Use to update material info

        "RedeemVoucher", # Handle for bounties
        "PayFines", # Handle for bounties

    ]
    
    HANDLED_EVENTS = [
        "Music",
        "Bounty",
        "MissionAccepted",
        "MissionRedirected",
        "MissionCompleted",
        "MissionAbandoned",
        "MissionFailed",
        "FSDJump",
        "Shutdown",
        "Materials", # Useful info to display
        "SupercruiseExit",
    ]

    def __init__(self):
        self.mission_manager = MissionManager()
        self.material_manager = MaterialManager()

        self.session_pirate_count = 0
        self.system_pirate_count = 0
        self.last_kill_value = 0

        self.first_pirate_killed_at = None
        self.most_recent_update_at = None

        self.in_combat = False
        self.total_missions = 0
        self.bounties = {}
        self.session_bounties = [] 
        self.material_table_data = {}

    def handle_event(self, event):
        event_type = event["event"]
        self.most_recent_update_at = datetime.strptime(event["timestamp"], '%Y-%m-%dT%H:%M:%SZ')

        # Use music to determine combat state
        if event_type == "Music":
            track = event["MusicTrack"]
            if track == "Combat_Dogfight":
                self.in_combat = True
            elif track == "Exploration":
                self.in_combat = False
        
        elif event_type == "SupercruiseExit":
            self.first_pirate_killed_at = self.most_recent_update_at
        
        elif event_type == "Bounty":
            rewards = event.get("Rewards", None)
            if rewards:
                reward = rewards[0]
                # Update kill counts
                self.session_pirate_count += 1
                self.system_pirate_count += 1

                # Update bounty sums
                nkv = self.mission_manager.get_next_kill_value(event["VictimFaction"])
                if reward["Faction"] in self.bounties:
                    self.bounties[reward["Faction"]] += reward["Reward"]
                    if nkv != 0:
                        self.last_kill_value = nkv + reward["Reward"]
                else:
                    self.bounties[reward["Faction"]] = reward["Reward"]
                event["MissionValue"] = nkv

                self.session_bounties.append(event)
                # Update kill missions
                self.mission_manager.handle_bounty_update(event["VictimFaction"])

        elif event_type == "MissionAccepted":
            self.total_missions += 1
            if event["Name"] in ["Mission_Massacre", "Mission_MassacreWing"]: 
                self.mission_manager.add_mission(Mission(event))

        elif event_type == "MissionRedirected":
            self.mission_manager.handle_mission_redirect(event["MissionID"])

        elif event_type in ["MissionCompleted", "MissionAbandoned", "MissionFailed"]:
            self.total_missions -= 1
            self.mission_manager.remove_mission(event["MissionID"])

        elif event_type == "FSDJump":
            self.system_pirate_count = 0
            self.last_kill_value = 0

        elif event_type == "Shutdown":
            self.first_pirate_killed_at = self.most_recent_update_at
            self.session_pirate_count = 0
            self.system_pirate_count = 0
            self.last_kill_value = 0

        elif event_type == "Materials":
            self.material_manager.handle_materials_event(event)

        else:
            print("You forgot to add this event to the HANDLED_EVENTS list:")
            print(event)
    
    def can_handle_event(self, event_type):
        return event_type in self.HANDLED_EVENTS

    def can_ignore_event(self, event_type):
        return event_type in self.IGNORED_EVENTS
        
    def text_summary(self):
        reward_total = sum([m.reward for m in self.mission_manager.missions_by_id.values()])
        kills_per_hour = 0
        time_in_system = ((self.most_recent_update_at - self.first_pirate_killed_at).total_seconds() / 3600.0)
        if self.first_pirate_killed_at != None and time_in_system != 0:
            kills_per_hour = self.system_pirate_count / time_in_system
        kph = round(kills_per_hour, 1)
        hrs = round(time_in_system, 2)
        lkv = '${:,}'.format(int(self.last_kill_value))
        projected_cph = '${:,}'.format(int(kills_per_hour * self.last_kill_value))
        summary = [
            f"Mission totals ({self.total_missions}) - Max Reward: {'${:,}'.format(reward_total)}",
            f"Pirates stats - Session Kills: {self.session_pirate_count}, System Kills: {self.system_pirate_count}",
            f"                kills/hr: {kph} ({hrs} hrs), Last kill value: {lkv}, Projected CR/hr: {projected_cph}",
        ]

        mmt = self.mission_manager.current_massacre_missions_table()
        if mmt != None: summary.append(mmt)

        mat_table = self.material_manager.current_materials_table()
        if mat_table != None: summary += mat_table

        return '\n'.join(summary)