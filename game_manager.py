from datetime import datetime, timezone
from terminaltables import AsciiTable
from terminaltables import SingleTable 

from material_manager import MaterialManager
from mission_manager import MissionManager 
from mission_manager import Mission

class GameManager:
    IGNORED_EVENTS = [
        "ReceiveText", "UnderAttack", "ShipTargeted", "ReservoirReplenished", "Docked", "Undocked", "ApproachSettlement", "StartJump", "SupercruiseEntry",
        "NpcCrewPaidWage", "BuyAmmo", "RestockVehicle", "RefuelAll", "SupercruiseExit", "DockingRequested", "DockingGranted", "FSSSignalDiscovered",
        "FSDTarget", "NavRoute", "Interdicted", "MaterialDiscovered", "Promotion",
        "SellDrones", "ModuleInfo", "Friends", "Fileheader", "ModuleSell",
        "EscapeInterdiction",
        "RepairAll",
        "USSDrop",
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
        "CrewHire",
        "SelfDestruct",
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
        "Missions",
        "MissionAccepted",
        "MissionRedirected",
        "MissionCompleted",
        "MissionAbandoned",
        "MissionFailed",
        "FSDJump",
        "Shutdown",
        "Materials", # Useful info to display
        "SupercruiseExit",

        "DockFighter",
        "LaunchFighter",
        "FighterRebuilt",
        "FighterDestroyed",
        "Died",
        "HullDamage",
        "Resurrect",
        "LoadGame",
    ]

    def __init__(self):
        self.mission_manager = MissionManager()
        self.material_manager = MaterialManager()

        self.session_pirate_count = 0
        self.system_pirate_count = 0
        self.last_kill_value = 0
        self.last_pirate_killed_at = None

        self.first_pirate_killed_at = None
        self.most_recent_update_at = None

        self.in_combat = False
        self.total_missions = 0
        self.bounties = {}
        self.session_bounties = [] 
        self.material_table_data = {}

        self.hull_status = None
        self.slf_status = None

    def minutes_ago(self, time):
        new_time = time.replace(tzinfo=timezone.utc).astimezone(tz=None)
        return f'{round((datetime.now(timezone.utc) - new_time).total_seconds() / 60, 2)} min ago'

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
            self.last_pirate_killed_at = datetime.strptime(event["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
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
        
        elif event_type == "Missions":
            active_ids = [e["MissionID"] for e in event["Active"]]
            self.total_missions = len(active_ids)
            self.mission_manager.filter_by_active_ids(active_ids)

        elif event_type == "MissionAccepted":
            self.total_missions += 1
            if event["Name"] in ["Mission_Massacre", "Mission_MassacreWing"]: 
                self.mission_manager.add_massacre_mission(Mission(event))
            # elif event["Name"] in ["Mission_Assassinate_name"]:
            #    self.mission_manager.add_assassinate_mission(Mission(event))

        elif event_type == "MissionRedirected":
            if event["Name"] in ["Mission_Massacre", "Mission_MassacreWing"]: 
                self.mission_manager.handle_massacre_mission_redirect(event["MissionID"])
            # elif event["Name"] in ["Mission_Assassinate_name"]:
            #    self.mission_manager.handle_assassinate_mission_redirect(Mission(event))

        elif event_type in ["MissionCompleted", "MissionAbandoned", "MissionFailed"]:
            self.total_missions -= 1
            if event["Name"] in ["Mission_Massacre", "Mission_MassacreWing"]: 
                self.mission_manager.remove_massacre_mission(event["MissionID"])
            # elif event["Name"] in ["Mission_Assassinate_name"]:
            #    self.mission_manager.remove_assassinate_mission(Mission(event))

        elif event_type == "Materials":
            self.material_manager.handle_materials_event(event)

        elif event_type in ("DockFighter", "LaunchFighter", "FighterRebuilt", "FighterDestroyed"):
            self.slf_status = event_type
            if event_type == "FighterDestroyed":
                self.slf_hull_status = 0.0
            elif event_type == "LaunchFighter":
                self.slf_hull_status = 1.0

        elif event_type == "HullDamage":
            if event["PlayerPilot"]:
                self.hull_status = event["Health"]
            elif event["Fighter"]:
                self.slf_hull_status = event["Health"]
        
        elif event_type == "Died":
            self.hull_status = 0.0

        elif event_type == "Resurrect":
            self.hull_status = 1.0

        elif event_type == "FSDJump":
            self.start_new_session()

        # Change to end_session at some point and 
        elif event_type == "Shutdown":
            self.start_new_session()

        elif event_type == "LoadGame":
            self.start_new_session()

        else:
            print("You forgot to add this event to the HANDLED_EVENTS list:")
            print(event)
    
    def start_new_session(self):
        self.first_pirate_killed_at = self.most_recent_update_at
        self.session_pirate_count = 0
        self.system_pirate_count = 0
        self.last_kill_value = 0
        self.session_bounties = []

    def current_session_summary(self):
        mission_values = sum([b["MissionValue"] for b in self.session_bounties])
        reward_values = sum([sum(r["Reward"] for r in b["Rewards"]) for b in self.session_bounties])
        cr_earned = mission_values + reward_values
        time_in_session = ((self.most_recent_update_at - self.first_pirate_killed_at).total_seconds() / 3600.0)
        hrs = round(time_in_session, 2)
        num_pirates_killed = len(self.session_bounties)
        kills_per_hour = 0.0
        if self.first_pirate_killed_at != None and time_in_session != 0:
            kills_per_hour = round(num_pirates_killed / time_in_session, 1)

        cr_per_hour = 0.0
        if self.first_pirate_killed_at != None and time_in_session != 0:
            cr_per_hour = cr_earned / time_in_session
        
        table_data = [
            ["Kills", f'{num_pirates_killed}'],
            ["Kills/hr", f'{kills_per_hour}'],
            ["CR earned", '${:,}'.format(int(cr_earned))],
            ["CR/hr", '${:,}'.format(int(cr_per_hour))],
        ]
        table = AsciiTable(table_data, f" Session stats ({hrs} hrs)")
        table.inner_heading_row_border = False
        return table.table


    
    def can_handle_event(self, event_type):
        return event_type in self.HANDLED_EVENTS

    def can_ignore_event(self, event_type):
        return event_type in self.IGNORED_EVENTS
        
    def text_summary(self):
        reward_total = sum([m.reward for m in self.mission_manager.missions_by_id.values()])
        summary = [
            f"Event times - Last event: {self.minutes_ago(self.most_recent_update_at)}, Last pirate killed at: {self.minutes_ago(self.last_pirate_killed_at)}",
            f"Health info - Last SLF event: {self.slf_status}, SLF Hull: {self.slf_hull_status}, Player Hull: {self.hull_status}",
            f"Mission totals ({self.total_missions}) - Max Reward: {'${:,}'.format(reward_total)}",

        ]

        mmt = self.mission_manager.current_massacre_missions_table()
        if mmt != None: summary.append(mmt)

        summary.append(self.current_session_summary())

        # mat_table = self.material_manager.current_materials_table()
        # if mat_table != None: summary += mat_table

        return '\n'.join(summary)