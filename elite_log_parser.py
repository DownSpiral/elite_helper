from datetime import datetime
import glob
import http.server
import json
import os
import socketserver
from terminaltables import AsciiTable
from terminaltables import SingleTable 
import threading
import time
import subprocess
from urllib.parse import urlparse
from urllib.parse import parse_qs

MATERIAL_CAT_CLASS_MATRICIES = {
    "Raw": [
        ["carbon", "vanadium", "niobium", "yttrium"],
        ["phosphorus", "chromium", "molybdenum", "technetium"],
        ["sulfur", "manganese", "cadmium", "ruthenium"],
        ["iron", "zinc", "tin", "selenium"],
        ["nickel", "germanium", "tungsten", "tellurium"],
        ["rhenium", "arsenic", "mercury", "polonium"],
        ["lead", "zirconium", "boron", "antimony"],
    ],
    "Manufactured": [
        ["chemicalstorageunits","chemicalprocessors","chemicaldistillery","chemicalmanipulators","pharmaceuticalisolators"],
        ["temperedalloys","heatresistantceramics","precipitatedalloys","thermicalloys","militarygradealloys"],
        ["heatconductionwiring","heatdispersionplate","heatexchangers","heatvanes","protoheatradiators"],
        ["basicconductors","conductivecomponents","conductiveceramics","conductivepolymers","biotechconductors"],
        ["mechanicalscrap","mechanicalequipment","mechanicalcomponents","configurablecomponents","improvisedcomponents"],
        ["gridresistors","hybridcapacitors","electrochemicalarrays","polymercapacitors","militarysupercapacitors"],
        ["wornshieldemitters","shieldemitters","shieldingsensors","compoundshielding","imperialshielding"],
        ["compactcomposites","filamentcomposites","highdensitycomposites","proprietarycomposites","coredynamicscomposites"],
        ["salvagedalloys","galvanisingalloys","phasealloys","protolightalloys","protoradiolicalloys"],
        ['crystalshards', 'flawedfocuscrystals', 'focuscrystals', 'refinedfocuscrystals', 'exquisitefocuscrystals'],
    ],
    "Encoded": [
        ["exceptionalscrambledemissiondata","irregularemissiondata","unexpectedemissiondata","decodedemissiondata","abnormalcompactemissiondata"],
        ["atypicaldisruptedwakeechoes","anomalousfsdtelemetry","strangewakesolutions","eccentrichyperspacetrajectories","dataminedwakeexceptions"],
        ["distoredshieldcyclerecordings","inconsistentshieldsoakanalysis","untypicalshieldscans","aberrantshieldpatternanalysis","peculiarshieldfrequencydata"],
        ["unusualencyptedfiles","taggedencryptioncodes","opensymmetrickeys","atypicalencryptionarchives","adaptiveencryptorscapture"],
        ["anomalousbulkscandata","unidentifiedscanarchives","classifiedscandatabanks","divergentscandata","classifiedscanfragment"],
        ["specializedlegacyfirmware","modifiedconsumerfirmware","crackedindustrialfirmware","securityfirmwarepatch","modifiedembeddedfirmware"],
    ]
}

MATERIAL_CAT_NAMES = {
    "Raw": ["CAT 1", "CAT 2", "CAT 3", "CAT 4", "CAT 5", "CAT 6", "CAT 7"],
    "Manufactured": ["Chemical", "Thermic", "Heat", "Conductive", "Mechanical", "Capacitors", "Shielding", "Composite", "Alloys", "Crystals"],
    "Encoded": ["Emission Data", "Wake Scans", "Shield Data", "Encryption Files", "Data Archives", "Encoded Firmware"],
}

MATERIAL_DATA = {
    "Raw": {
        "boron": { "display_name": "Boron", "class": 0 },
        "carbon": { "display_name": "Carbon:", "class": 0 },
        "iron": { "display_name": "Iron:", "class": 0 },
        "lead": { "display_name": "Lead:", "class": 0 },
        "nickel": { "display_name": "Nickel:", "class": 0 },
        "phosphorus": { "display_name": "Phosphorus:", "class": 0 },
        "rhenium": { "display_name": "Rhenium:", "class": 0 },
        "sulphur": { "display_name": "Sulphur:", "class": 0 },
        "arsenic": { "display_name": "Arsenic:", "class": 1 },
        "chromium": { "display_name": "Chromium:", "class": 1 },
        "germanium": { "display_name": "Germanium:", "class": 1 },
        "manganese": { "display_name": "Manganese:", "class": 1 },
        "vanadium": { "display_name": "Vanadium:", "class": 1 },
        "zinc": { "display_name": "Zinc:", "class": 1 },
        "zirconium": { "display_name": "Zirconium:", "class": 1 },
        "cadmium": { "display_name": "Cadmium:", "class": 2 },
        "mercury": { "display_name": "Mercury:", "class": 2 },
        "molybdenum": { "display_name": "Molybdenum:", "class": 2 },
        "niobium": { "display_name": "Niobium:", "class": 2 },
        "tin": { "display_name": "Tin:", "class": 2 },
        "tungsten": { "display_name": "Tungsten:", "class": 2 },
        "antimony": { "display_name": "Antimony:", "class": 3 },
        "polonium": { "display_name": "Polonium:", "class": 3 },
        "ruthenium": { "display_name": "Ruthenium:", "class": 3 },
        "selenium": { "display_name": "Selenium:", "class": 3 },
        "technetium": { "display_name": "Technetium:", "class": 3 },
        "tellurium": { "display_name": "Tellurium:", "class": 3 },
        "yttrium": { "display_name": "Yttrium:", "class": 3 },
    },
    "Manufactured": {
        'basicconductors': {'display_name': 'Basic Conductors', 'class': 0, 'cat': 3},
        'chemicalstorageunits': {'display_name': 'Chemical Storage Units', 'class': 0, 'cat': 0},
        'compactcomposites': {'display_name': 'Compact Composites', 'class': 0, 'cat': 7},
        'crystalshards': {'display_name': 'Crystal Shards', 'class': 0},
        'gridresistors': {'display_name': 'Grid Resistors', 'class': 0, 'cat': 5},
        'heatconductionwiring': {'display_name': 'Heat Conduction Wiring', 'class': 0, 'cat': 2},
        'mechanicalscrap': {'display_name': 'Mechanical Scrap', 'class': 0, 'cat': 4},
        'salvagedalloys': {'display_name': 'Salvaged Alloys', 'class': 0, 'cat': 8},
        'temperedalloys': {'display_name': 'Tempered Alloys', 'class': 0, 'cat': 1},
        'wornshieldemitters': {'display_name': 'Worn Shield Emitters', 'class': 0, 'cat': 6},
        'chemicalprocessors': {'display_name': 'Chemical Processors', 'class': 1, 'cat': 0},
        'conductivecomponents': {'display_name': 'Conductive Components', 'class': 1, 'cat': 3},
        'filamentcomposites': {'display_name': 'Filament Composites', 'class': 1, 'cat': 7},
        'flawedfocuscrystals': {'display_name': 'Flawed Focus Crystals', 'class': 1},
        'galvanisingalloys': {'display_name': 'Galvanising Alloys', 'class': 1, 'cat': 8},
        'heatdispersionplate': {'display_name': 'Heat Dispersion Plate', 'class': 1, 'cat': 2},
        'heatresistantceramics': {'display_name': 'Heat Resistant Ceramics', 'class': 1, 'cat': 1},
        'hybridcapacitors': {'display_name': 'Hybrid Capacitors', 'class': 1, 'cat': 5},
        'mechanicalequipment': {'display_name': 'Mechanical Equipment', 'class': 1, 'cat': 4},
        'shieldemitters': {'display_name': 'Shield Emitters', 'class': 1, 'cat': 6},
        'thargoidcarapace': {'display_name': 'Thargoid Carapace', 'class': 1},
        'chemicaldistillery': {'display_name': 'Chemical Distillery', 'class': 2, 'cat': 0},
        'conductiveceramics': {'display_name': 'Conductive Ceramics', 'class': 2, 'cat': 3},
        'electrochemicalarrays': {'display_name': 'Electrochemical Arrays', 'class': 2, 'cat': 5},
        'focuscrystals': {'display_name': 'Focus Crystals', 'class': 2},
        'heatexchangers': {'display_name': 'Heat Exchangers', 'class': 2, 'cat': 2},
        'highdensitycomposites': {'display_name': 'High Density Composites', 'class': 2, 'cat': 7},
        'mechanicalcomponents': {'display_name': 'Mechanical Components', 'class': 2, 'cat': 4},
        'phasealloys': {'display_name': 'Phase Alloys', 'class': 2, 'cat': 8},
        'precipitatedalloys': {'display_name': 'Precipitated Alloys', 'class': 2, 'cat': 1},
        'shieldingsensors': {'display_name': 'Shielding Sensors', 'class': 2, 'cat': 6},
        'thargoidenergycell': {'display_name': 'Thargoid Energy Cell', 'class': 2},
        'chemicalmanipulators': {'display_name': 'Chemical Manipulators', 'class': 3, 'cat': 0},
        'compoundshielding': {'display_name': 'Compound Shielding', 'class': 3, 'cat': 6},
        'conductivepolymers': {'display_name': 'Conductive Polymers', 'class': 3, 'cat': 3},
        'configurablecomponents': {'display_name': 'Configurable Components', 'class': 3, 'cat': 4},
        'heatvanes': {'display_name': 'Heat Vanes', 'class': 3, 'cat': 2},
        'polymercapacitors': {'display_name': 'Polymer Capacitors', 'class': 3, 'cat': 5},
        'proprietarycomposites': {'display_name': 'Proprietary Composites', 'class': 3, 'cat': 7},
        'protolightalloys': {'display_name': 'Proto Light Alloys', 'class': 3, 'cat': 8},
        'refinedfocuscrystals': {'display_name': 'Refined Focus Crystals', 'class': 3},
        'thargoidtechnologycomponents': {'display_name': 'Thargoid Technology Components', 'class': 3},
        'thermicalloys': {'display_name': 'Thermic Alloys', 'class': 3, 'cat': 1},
        'biotechconductors': {'display_name': 'Biotech Conductors', 'class': 4, 'cat': 3},
        'coredynamicscomposites': {'display_name': 'Core Dynamics Composites', 'class': 4, 'cat': 7},
        'exquisitefocuscrystals': {'display_name': 'Exquisite Focus Crystals', 'class': 4},
        'imperialshielding': {'display_name': 'Imperial Shielding', 'class': 4, 'cat': 6},
        'improvisedcomponents': {'display_name': 'Improvised Components', 'class': 4, 'cat': 4},
        'militarygradealloys': {'display_name': 'Military Grade Alloys', 'class': 4, 'cat': 1},
        'militarysupercapacitors': {'display_name': 'Military Supercapacitors', 'class': 4, 'cat': 5},
        'pharmaceuticalisolators': {'display_name': 'Pharmaceutical Isolators', 'class': 4, 'cat': 0},
        'protoheatradiators': {'display_name': 'Proto Heat Radiators', 'class': 4, 'cat': 2},
        'protoradiolicalloys': {'display_name': 'Proto Radiolic Alloys', 'class': 4, 'cat': 8},
        'sensorfragment': {'display_name': 'Sensor Fragment', 'class': 4},
        'thargoidorganiccircuitry': {'display_name': 'Thargoid Organic Circuitry', 'class': 4},
    },
    "Encoded": {

    },
}

def simple_tail(fname, loop_at_end=False, sleep_interval=1, stop_flag=b'\034\n'):
    with open(fname, 'rb') as fin:
        line = fin.readline()
        while line:
            at_end = False
            where = fin.tell()
            next_line = fin.readline()
            if not next_line:
                at_end = True
            fin.seek(where)
            yield (line, at_end)
            line = fin.readline()

        while True:
            where = fin.tell()
            line = fin.readline()
            if not line:
                if loop_at_end:
                    time.sleep(sleep_interval)
                    fin.seek(where)
                else:
                    break
            else:
                if line == stop_flag:
                    break
                yield (line, True)

class Mission:
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    def __init__(self, event):
        self.created_at = event["timestamp"]
        self.id = event["MissionID"]
        self.expires_at = event["Expiry"]
        self.faction = event["Faction"]
        self.name = event["Name"]
        self.target_faction = event["TargetFaction"]
        self.kill_count = event["KillCount"]
        self.reward = event["Reward"]
        self.kill_progress = 0
        self.status = self.IN_PROGRESS
    
    def __str__(self):
        return f'Mission({self.id}) for {self.faction} to kill {self.target_faction} - ({self.kill_progress}/{self.kill_count}) {self.created_at}'

    def __repr__(self):
        return self.__str__()

class MissionManager:
    def __init__(self):
        self.missions_by_id = {}
        self.missions_by_faction = {}
    
    def add_mission(self, mission):
        self.missions_by_id[mission.id] = mission
        if mission.faction in self.missions_by_faction: self.missions_by_faction[mission.faction].append(mission)
        else: self.missions_by_faction[mission.faction] = [mission]

    def remove_mission(self, mission_id):
        self.missions_by_id.pop(mission_id, None)
        new_missions_by_faction = {}
        for faction, missions in self.missions_by_faction.items():
            new_missions = [m for m in missions if m.id != mission_id]
            if len(new_missions) > 0:
                new_missions_by_faction[faction] = new_missions
        self.missions_by_faction = new_missions_by_faction
    
    def handle_bounty_update(self, faction):
        for missions in self.missions_by_faction.values():
            for m in missions:
                if m.target_faction == faction and m.kill_progress < m.kill_count:
                    m.kill_progress += 1
                    break # only update the first mission found per faction

    def handle_mission_redirect(self, mission_id):
        m = self.missions_by_id.get(mission_id, None)
        if m != None:
            m.status = Mission.COMPLETED
            if m.kill_count - m.kill_progress > 1:
                "wat"
                # print("KILL COUNT NOT EQUAL - SOMTHING ISN'T UP\n", m)
                # [[print(m) for m in v] for k, v in self.missions_by_faction.items()]
    def get_next_kill_value(self, faction):
        kv = 0
        for missions in self.missions_by_faction.values():
            for m in missions:
                if m.target_faction == faction and m.kill_progress < m.kill_count:
                    kv += m.reward / float(m.kill_count)
                    break # only count the first mission found per faction
        return kv

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

        self.session_pirate_count = 0
        self.system_pirate_count = 0
        self.last_kill_value = 0

        self.first_pirate_killed_at = None
        self.most_recent_update_at = None

        self.in_combat = False
        self.total_missions = 0
        self.bounties = {}
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
            self.session_pirate_count = 0

        elif event_type == "Materials":
            def gen_mat_for_event(type, event):
                table_data = []
                for i, cat in enumerate(MATERIAL_CAT_CLASS_MATRICIES[type]):
                    row = [MATERIAL_CAT_NAMES[type][i]]
                    for cat_item in cat:
                        mat_name = cat_item
                        mat_qty = 0
                        mat = next((mat for mat in event[type] if mat["Name"] == cat_item), None)
                        if mat != None:
                            mat_name = mat.get("Name_Localised", cat_item)
                            mat_qty = mat["Count"]
                        row.append(mat_name)
                        row.append(mat_qty)
                    table_data.append(row)
                return table_data


            self.material_table_data = {
               "Raw": gen_mat_for_event("Raw", event),
               "Manufactured": gen_mat_for_event("Manufactured", event),
               "Encoded": gen_mat_for_event("Encoded", event),
            }

        else:
            print("You forgot to add this event to the HANDLED_EVENTS list:")
            print(event)
    
    def can_handle_event(self, event_type):
        return event_type in self.HANDLED_EVENTS

    def can_ignore_event(self, event_type):
        return event_type in self.IGNORED_EVENTS

    def current_massacre_missions_table(self):
        mbf = self.mission_manager.missions_by_faction
        missions_table = [["Mission giver", "Num Missions", "# Killed", "# Remaining", "# Total"]]
        missions_table_data = []
        for faction, missions in mbf.items():
            kill_count = sum([m.kill_count for m in missions])
            kill_progress = sum([m.kill_progress for m in missions])
            kill_remaining = kill_count - kill_progress
            mission_count = len(missions)
            missions_table_data.append([faction, mission_count, kill_progress, kill_remaining, kill_count])
        
        if len(missions_table_data) > 0:
            if len(missions_table_data) > 1: missions_table_data.sort(reverse=True, key=lambda x: x[3])
            missions_table += missions_table_data
            return AsciiTable(missions_table, " Massacre Missions ").table
        else:
            return None
        
    def game_state(self):
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

        mmt = self.current_massacre_missions_table()
        if mmt != None: summary.append(mmt)

        for mat_type in MATERIAL_DATA.keys():
            table_instance = AsciiTable(self.material_table_data[mat_type], f" {mat_type} ")
            table_instance.inner_heading_row_border = False
            summary.append(table_instance.table)

        return '\n'.join(summary)

game_manager = GameManager()

PORT = 3000
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
                # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()
        
        html = f"<html><head></head><body><text style='white-space: pre; font-family: \"Lucida Console\", \"Courier New\", monospace;'>{game_manager.game_state()}</text></body></html>"

        # Writing the HTML contents with UTF-8
        self.wfile.write(bytes(html, "utf8"))

        return

# Create an object of the above class
handler_object = MyHttpRequestHandler

def server_function(name):
    my_server = socketserver.TCPServer(("", PORT), handler_object)
    my_server.serve_forever()

def create_web_server():
    x = threading.Thread(target=server_function, args=(1,), daemon=True)
    x.start()


username = subprocess.check_output("echo %username%", shell=True).rstrip().decode("utf-8")
logs = glob.glob(f"C:\\Users\\{username}\\Saved Games\\Frontier Developments\\Elite Dangerous\\Journal.*.log")
logs.sort()
last_log = logs.pop()

clear = lambda: os.system('cls')
create_web_server()

# Handle all other logs to catch up the game state
for log in logs:
    for (line, _) in simple_tail(log, False):
        event = json.loads(line.decode('UTF-8').rstrip())
        if game_manager.can_handle_event(event["event"]):
            game_manager.handle_event(event)
        elif not game_manager.can_ignore_event(event["event"]):
            print("Unknown event, please add to HANDLED_EVENTS or IGNORED_EVENTS lists")
            print(event)

# Handle last log and loop
# TODO: Handle a game restart without restarting the script
did_first_clear = False
for (line, at_end) in simple_tail(last_log, True):
    game_updated = False
    event = json.loads(line.decode('UTF-8').rstrip())
    if game_manager.can_handle_event(event["event"]):
        game_manager.handle_event(event)
        game_updated = True
    elif not game_manager.can_ignore_event(event["event"]):
        print("Unknown event, please add to HANDLED_EVENTS or IGNORED_EVENTS lists")
        print(event)
    if (game_updated and at_end) or (at_end and not did_first_clear):
        did_first_clear = True
        clear()
        print(game_manager.game_state())
        # time.sleep(0.15)