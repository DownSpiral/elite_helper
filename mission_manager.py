from terminaltables import AsciiTable
from terminaltables import SingleTable 

class Mission:
    MASSACRE_MISSION_TYPES = ["Mission_Massacre", "Mission_MassacreWing", "Mission_Massacre_RankFed"]
    ASSASSINATION_MISSION_TYPES = ["Mission_Assassinate"]
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    def __init__(self, event):
        self.created_at = event["timestamp"]
        self.id = event["MissionID"]
        self.expires_at = event.get("Expiry", None)
        self.faction = event["Faction"]
        self.name = event["Name"]
        self.reward = event.get("Reward", 0)
        self.status = self.IN_PROGRESS

        self.target_faction = event.get("TargetFaction", None)
        self.kill_progress = 0
        self.kill_count = event.get("KillCount", 0)
    
    def __str__(self):
        if self.name in self.MASSACRE_MISSION_TYPES:
            return f'Mission({self.id}) for {self.faction} to kill {self.target_faction} - ({self.kill_progress}/{self.kill_count}) {self.created_at}'
        else:
            return f'Mission({self.id}) for {self.faction} of type {self.name} {self.created_at}'

    def __repr__(self):
        return self.__str__()

class MissionManager:
    def __init__(self):
        self.missions_by_id = {}
        self.assassination_missions_by_id = {}

    def add_mission(self, mission):
        self.missions_by_id[mission.id] = mission

    def remove_mission(self, mission_id):
        self.missions_by_id.pop(mission_id, None)

    def handle_mission_redirect(self, mission_id):
        m = self.missions_by_id.get(mission_id, None)
        if m != None:
            m.status = Mission.COMPLETED

    def filter_by_active_ids(self, mission_ids):
        no_longer_active = set(self.missions_by_id.keys()) - set(mission_ids)
        [self.remove_mission(id) for id in no_longer_active]

    def missions_by_faction(self, types):
        mbf = {}
        filtered = [m for m in self.missions_by_id.values() if m.name in types]
        for mission in filtered:
            if mission.faction in mbf: mbf[mission.faction].append(mission)
            else: mbf[mission.faction] = [mission]
        return mbf

    def missions_of_type(self, types):
        return [m for m in self.missions_by_id.values() if m.name in types]

    def handle_bounty_update(self, target_faction):
        for faction, missions in self.missions_by_faction(Mission.MASSACRE_MISSION_TYPES).items():
            for m in missions:
                if m.target_faction == target_faction and m.kill_progress < m.kill_count:
                    m.kill_progress += 1
                    break # only update the first mission found per faction
                
    def get_next_kill_value(self, faction):
        kv = 0
        for missions in self.missions_by_faction(Mission.MASSACRE_MISSION_TYPES).values():
            for m in missions:
                if m.target_faction == faction and m.kill_progress < m.kill_count:
                    kv += m.reward / float(m.kill_count)
                    break # only count the first mission found per faction
        return kv

    def current_assassination_targets_table(self):
        missions_table = [["Name", "Faction", "Location"]]
        for m in self.missions_of_type(Mission.ASSASSINATION_MISSION_TYPES):
            missions_table.append([m.name])

    def current_massacre_missions_table(self):
        mbf = self.missions_by_faction(Mission.MASSACRE_MISSION_TYPES)
        missions_table = [["Mission giver", "# Remaining"]]
        missions_table_data = []
        for faction, missions in mbf.items():
            kill_count = sum([m.kill_count for m in missions])
            kill_progress = sum([m.kill_progress for m in missions])
            kill_rem = kill_count - kill_progress
            kill_rem_individual = "-".join([str(m.kill_count - m.kill_progress) for m in missions if m.kill_count - m.kill_progress != 0])
            kill_remaining = "{:3} ({})".format(str(kill_count - kill_progress), kill_rem_individual)
            missions_table_data.append([faction, kill_remaining, kill_rem])
        
        if len(missions_table_data) > 0:
            if len(missions_table_data) > 1: missions_table_data.sort(reverse=True, key=lambda x: x[-1])
            missions_table += [m[:-1] for m in missions_table_data]
            return AsciiTable(missions_table, " Massacre Missions ").table
        else:
            return None