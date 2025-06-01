import mesa
try:
    from agents import MtbAgent, BackgroundPatchAgent
except ImportError:
    print("CRITICAL: MtbAgent or BackgroundPatchAgent not found. Ensure agents.py is correct.")
    MtbAgent = None
    BackgroundPatchAgent = None

import numpy as np

class MtbEnvironmentModel(mesa.Model):
    def __init__(self,
                 width="30", height="30",
                 initial_mtb_population="50",
                 drug_name="Rifampicin",
                 drug_start_step="50",
                 drug_duration_steps="200",
                 drug_applied_concentration="10.0",
                 rif_mic="1.0",
                 rpoB_mutation_rate="1e-7",
                 basal_replication_rate_mtb="0.1",
                 basal_death_rate_mtb="0.01",
                 fitness_cost_rif_resistant="0.1",
                 max_iters="500",
                 seed="None"):

        try:
            self.p_width = int(width)
            self.p_height = int(height)
            self.p_initial_mtb_population = int(initial_mtb_population)
            self.p_drug_start_step = int(drug_start_step)
            self.p_drug_duration_steps = int(drug_duration_steps)
            self.p_drug_applied_concentration = float(drug_applied_concentration)
            self.p_rif_mic = float(rif_mic)
            self.p_rpoB_mutation_rate = 10**float(rpoB_mutation_rate)
            self.p_basal_replication_rate_mtb = float(basal_replication_rate_mtb)
            self.p_basal_death_rate_mtb = float(basal_death_rate_mtb)
            self.p_fitness_cost_rif_resistant = float(fitness_cost_rif_resistant)
            self.max_iters = int(max_iters)
            parsed_seed = None
            if isinstance(seed, str):
                if seed.lower() == "none": parsed_seed = None
                elif seed.isdigit(): parsed_seed = int(seed)
            elif isinstance(seed, (int, float)): parsed_seed = int(seed)
            super().__init__(seed=parsed_seed)
        except ValueError as e:
            print(f"FATAL: Error converting UI parameters: {e}")
            raise

        self.drug_name = drug_name
        self.drug_present_in_environment = False
        self.current_drug_concentration = 0.0
        self.grid = mesa.space.MultiGrid(self.p_width, self.p_height, torus=True)

        if MtbAgent is None or BackgroundPatchAgent is None:
            raise ImportError("MtbAgent or BackgroundPatchAgent not properly imported.")

        for x in range(self.grid.width):
            for y in range(self.grid.height):
                patch = BackgroundPatchAgent(model=self)
                self.grid.place_agent(patch, (x,y))

        for _ in range(self.p_initial_mtb_population):
            agent = MtbAgent(
                model=self,
                initial_genotype={'rpoB_allele': 'wildtype'},
                mutation_rate_rpoB=self.p_rpoB_mutation_rate,
                basal_replication_rate=self.p_basal_replication_rate_mtb,
                basal_death_rate=self.p_basal_death_rate_mtb,
                fitness_cost_resistant=self.p_fitness_cost_rif_resistant
            )
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Steps": lambda m: m.steps,
                "TotalMtb": lambda m: len([a for a in m.agents if isinstance(a, MtbAgent)]),
                "SusceptibleMtb_RIF": lambda m: sum(1 for a in m.agents if isinstance(a, MtbAgent) and not a.is_resistant_rif),
                "ResistantMtb_RIF": lambda m: sum(1 for a in m.agents if isinstance(a, MtbAgent) and a.is_resistant_rif),
                "RifampicinConcentration": lambda m: m.current_drug_concentration
            }
        )
        self.running = True
        self.datacollector.collect(self)

    def get_drug_concentration(self, drug_name_query, pos=None):
        if drug_name_query == self.drug_name:
            return self.current_drug_concentration
        return 0.0

    def get_drug_mic(self, drug_name_query):
        if drug_name_query == self.drug_name:
            return self.p_rif_mic
        return float('inf')

    def place_offspring(self, offspring_agent, parent_pos):
        if self.grid.is_cell_empty(parent_pos):
             self.grid.place_agent(offspring_agent, parent_pos)
        else:
            possible_moves = self.grid.get_neighborhood(parent_pos, moore=True, include_center=False, radius=1)
            empty_neighbors = [p for p in possible_moves if self.grid.is_cell_empty(p)]
            target_pos = self.random.choice(empty_neighbors) if empty_neighbors else parent_pos
            self.grid.place_agent(offspring_agent, target_pos)

    def remove_agent(self, agent_to_remove):
        if isinstance(agent_to_remove, MtbAgent):
            agent_to_remove.remove()

    def step(self):
        if self.steps == self.p_drug_start_step:
            self.drug_present_in_environment = True
            self.current_drug_concentration = self.p_drug_applied_concentration
        elif self.steps == (self.p_drug_start_step + self.p_drug_duration_steps):
            self.drug_present_in_environment = False
            self.current_drug_concentration = 0.0

        mtb_agents_to_step = [agent for agent in self.agents if isinstance(agent, MtbAgent)]
        for agent in self.random.sample(mtb_agents_to_step, len(mtb_agents_to_step)):
            agent.step()

        self.datacollector.collect(self)

        if self.steps >= self.max_iters or len([a for a in self.agents if isinstance(a, MtbAgent)]) == 0:
            self.running = False
