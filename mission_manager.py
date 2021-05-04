from terminaltables import AsciiTable
from terminaltables import SingleTable 

class AssassinationMission:
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    def __init__(self, event):
        self.created_at = event["timestamp"]
        self.id = event["MissionID"]
        self.expires_at = event["Expiry"]
        self.faction = event["Faction"]
        self.name = event["Name"]
        self.target_faction = event["TargetFaction"]
        self.reward = event["Reward"]
        self.kill_progress = 0
        self.status = self.IN_PROGRESS
    
    def __str__(self):
        return f'Mission({self.id}) for {self.faction} to kill {self.target_faction} - ({self.kill_progress}/{self.kill_count}) {self.created_at}'

    def __repr__(self):
        return self.__str__()

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
        self.assassination_missions_by_id = {}

    # There is a better way to do this, but doing this for now...
    def add_assassinate_mission(self, mission):
        self.assassination_missions_by_id[mission.id] = mission

    def remove_assassinate_mission(self, mission_id):
        self.assassination_missions_by_id.pop(mission_id, None)

    def handle_assassinate_mission_redirect(self, mission_id):
        m = self.assassination_missions_by_id.get(mission_id, None)
        if m != None:
            m.status = Mission.COMPLETED
    
    def add_massacre_mission(self, mission):
        self.missions_by_id[mission.id] = mission
        if mission.faction in self.missions_by_faction: self.missions_by_faction[mission.faction].append(mission)
        else: self.missions_by_faction[mission.faction] = [mission]

    def remove_massacre_mission(self, mission_id):
        self.missions_by_id.pop(mission_id, None)
        new_missions_by_faction = {}
        for faction, missions in self.missions_by_faction.items():
            new_missions = [m for m in missions if m.id != mission_id]
            if len(new_missions) > 0:
                new_missions_by_faction[faction] = new_missions
        self.missions_by_faction = new_missions_by_faction

    def filter_by_active_ids(self, mission_ids):
        no_longer_active = set(self.missions_by_id.keys()) - set(mission_ids)
        [self.remove_massacre_mission(id) for id in no_longer_active]
    
    def handle_bounty_update(self, faction):
        for missions in self.missions_by_faction.values():
            for m in missions:
                if m.target_faction == faction and m.kill_progress < m.kill_count:
                    m.kill_progress += 1
                    break # only update the first mission found per faction

    def handle_massacre_mission_redirect(self, mission_id):
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

    def current_massacre_missions_table(self):
        mbf = self.missions_by_faction
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