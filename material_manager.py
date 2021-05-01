from terminaltables import AsciiTable
from terminaltables import SingleTable 

class MaterialManager:
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

    def __init__(self):
        self.material_table_data = {
            "Raw": [],
            "Manufactured": [],
            "Encoded": [],
        }

    def gen_mat_for_event(self, type, event):
        table_data = []
        for i, cat in enumerate(self.MATERIAL_CAT_CLASS_MATRICIES[type]):
            row = [self.MATERIAL_CAT_NAMES[type][i]]
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


    def handle_materials_event(self, event):
        self.material_table_data = {
            "Raw": self.gen_mat_for_event("Raw", event),
            "Manufactured": self.gen_mat_for_event("Manufactured", event),
            "Encoded": self.gen_mat_for_event("Encoded", event),
        }
    
    def current_materials_table(self):
        materials_table = []
        for mat_type in self.MATERIAL_DATA.keys():
            table_instance = AsciiTable(self.material_table_data[mat_type], f" {mat_type} ")
            table_instance.inner_heading_row_border = False
            materials_table.append(table_instance.table)
        return materials_table 
