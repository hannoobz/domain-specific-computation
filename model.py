from mesa import Model
from mesa.space import SingleGrid
from agents import MtbBacterium
from mesa.datacollection import DataCollector
from mesa.experimental.devs import ABMSimulator
import math

class MtbResistanceModel(Model):
    def __init__(self,
                drug_type="RIF INH PZA EMB",
                day_start=21,
                day_interval=1,
                width=250,
                height=250,
                initial_mtb=200,
                initial_persister_fraction=0.01,
                prob_susceptible_to_persister=0.001,
                prob_persister_to_susceptible_no_drug=0.01,
                prob_persister_to_susceptible_drug_on=0.0001,
                seed=None,
                simulator: ABMSimulator = None,
                ):
        super().__init__(seed=seed)

        self.simulator = simulator
        self.simulator.setup(self)

        self.grid = SingleGrid(int(width), int(height), torus=False)
        self.steps = 0

        self.initial_persister_fraction = initial_persister_fraction
        self.prob_susceptible_to_persister = prob_susceptible_to_persister
        self.prob_persister_to_susceptible_no_drug = prob_persister_to_susceptible_no_drug
        self.prob_persister_to_susceptible_drug_on = prob_persister_to_susceptible_drug_on

        # RIFAMPICIN (RIF)
        self.rif_k_max_kill_daily = 0.055 * 24
        self.rif_ec50_ng_ml = 18.4
        self.rif_hill_coefficient = 1.0
        self.rif_active_concentration_ng_ml = 50.0

        # ISONIAZID (INH)
        self.inh_k_max_kill_daily = 0.041 * 24
        self.inh_ec50_ng_ml = 32.1
        self.inh_hill_coefficient = 1.0
        self.inh_active_concentration_ng_ml = 50.0

        # PYRAZINAMIDE (PZA)
        self.pza_k_max_kill_daily = 0.043 * 24
        self.pza_ec50_ng_ml = 45.5 * 1000000
        self.pza_hill_coefficient = 1.0
        self.pza_active_concentration_ng_ml = 60000.0

        # ETHAMBUTOL (EMB)
        self.emb_k_max_kill_daily = 0.053 * 24
        self.emb_ec50_ng_ml = 79.5
        self.emb_hill_coefficient = 1.0
        self.emb_active_concentration_ng_ml = 100.0

        kg_max_intracellular_hourly = 0.033
        kg_max_intracellular_daily_rate = kg_max_intracellular_hourly * 24
        self.replication_prob_per_day = 1 - math.exp(-kg_max_intracellular_daily_rate)

        self.rif_mutation_rate = 3.3e-6
        self.inh_mutation_rate = 3.2e-7
        self.pza_mutation_rate = 1e-5
        self.emb_mutation_rate = 6.4e-7

        self.rif_drug_on = False
        self.inh_drug_on = False
        self.pza_drug_on = False
        self.emb_drug_on = False

        self.day_start_treatment = int(day_start)
        self.day_treatment_interval = int(day_interval)
        self.active_drugs_config = self._parse_drug_type(drug_type)
        initial_mtb = int(initial_mtb)
        if initial_mtb > self.grid.width * self.grid.height:
            print(f"Warning: initial_mtb ({initial_mtb}) exceeds SingleGrid capacity ({self.grid.width * self.grid.height}). "
                f"Setting initial_mtb to {self.grid.width * self.grid.height}.")
            initial_mtb = self.grid.width * self.grid.height

        for i in range(initial_mtb):
            is_initial_persister = self.random.random() < self.initial_persister_fraction
            mtb_agent = MtbBacterium(model=self, initial_is_persister=is_initial_persister)
            
            if not self.grid.empties:
                print(f"Warning: No empty cells left to place all initial MTB. Placed {i} agents.")
                break
            
            empty_cell = self.random.choice(list(self.grid.empties))
            self.grid.place_agent(mtb_agent, empty_cell)
            self.agents.add(mtb_agent)

        model_reporters = {
            "Total Mtb": lambda m: len(m.agents),
            "Susceptible": lambda m: len(m.agents.select(
                lambda a: a.is_persister==False
                            and a.resistance_profile["RIF"]==False
                            and a.resistance_profile["INH"]==False
                            and a.resistance_profile["PZA"]==False
                            and a.resistance_profile["EMB"]==False
                            )),
            "Persister": lambda m: len(m.agents.select(lambda a: a.is_persister)),
            "Res-RIF": lambda m: len(m.agents.select(lambda a: a.resistance_profile["RIF"])),
            "Res-INH": lambda m: len(m.agents.select(lambda a: a.resistance_profile["INH"])),
            "Res-PZA": lambda m: len(m.agents.select(lambda a: a.resistance_profile["PZA"])),
            "Res-EMB": lambda m: len(m.agents.select(lambda a: a.resistance_profile["EMB"])),
        }
        self.datacollector = DataCollector(model_reporters)
        self.running = True
        self.datacollector.collect(self)


    def _parse_drug_type(self, drug_type_input):
        drug_type_input = list(drug_type_input.split(" "))
        active_drugs_map = {"RIF": False, "INH": False, "PZA": False, "EMB": False}

        if isinstance(drug_type_input, str):
            drug_upper = drug_type_input.upper()
            if drug_upper in active_drugs_map:
                active_drugs_map[drug_upper] = True
        elif isinstance(drug_type_input, list):
            for drug_str in drug_type_input:
                drug_upper = drug_str.upper()
                if drug_upper in active_drugs_map:
                    active_drugs_map[drug_upper] = True
        return active_drugs_map


    def step(self):
        is_treatment_day = False
        if self.steps >= self.day_start_treatment:
            if (self.steps - self.day_start_treatment) % self.day_treatment_interval == 0:
                is_treatment_day = True

        administered_today_list = []
        if is_treatment_day:
            self.rif_drug_on = self.active_drugs_config.get("RIF", False)
            if self.rif_drug_on: administered_today_list.append("RIF")

            self.inh_drug_on = self.active_drugs_config.get("INH", False)
            if self.inh_drug_on: administered_today_list.append("INH")

            self.pza_drug_on = self.active_drugs_config.get("PZA", False)
            if self.pza_drug_on: administered_today_list.append("PZA")

            self.emb_drug_on = self.active_drugs_config.get("EMB", False)
            if self.emb_drug_on: administered_today_list.append("EMB")

        else:
            self.rif_drug_on = False
            self.inh_drug_on = False
            self.pza_drug_on = False
            self.emb_drug_on = False

        self.agents.shuffle_do("step")
        self.datacollector.collect(self)