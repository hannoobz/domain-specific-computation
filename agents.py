import mesa
import numpy as np

class BackgroundPatchAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        pass

class MtbAgent(mesa.Agent):
    def __init__(self,
                 model,
                 initial_genotype=None,
                 mutation_rate_rpoB=1e-7,
                 basal_replication_rate=0.1,
                 basal_death_rate=0.01,
                 fitness_cost_resistant=0.1
                ):
        super().__init__(model)

        if initial_genotype is None:
            self.genotype = {'rpoB_allele': 'wildtype'}
        else:
            self.genotype = initial_genotype.copy()

        self.mutation_rate_rpoB = mutation_rate_rpoB
        self.fitness_cost_resistant = fitness_cost_resistant

        self.is_resistant_rif = False
        self.current_fitness_cost = 0.0
        self._calculate_phenotype_from_genotype()

        self.basal_replication_rate = basal_replication_rate
        self.basal_death_rate = basal_death_rate

    def _calculate_phenotype_from_genotype(self):
        if self.genotype.get('rpoB_allele', 'wildtype') != 'wildtype':
            self.is_resistant_rif = True
            self.current_fitness_cost = self.fitness_cost_resistant
        else:
            self.is_resistant_rif = False
            self.current_fitness_cost = 0.0

    def _mutate(self, offspring_genotype):
        if offspring_genotype['rpoB_allele'] == 'wildtype':
            if self.model.random.random() < self.mutation_rate_rpoB:
                offspring_genotype['rpoB_allele'] = 'mutated_resistant'
        return offspring_genotype

    def step(self):
        death_probability = self.basal_death_rate
        drug_conc_rif = self.model.get_drug_concentration('Rifampicin', self.pos)
        mic_rif = self.model.get_drug_mic('Rifampicin')

        if not self.is_resistant_rif and drug_conc_rif > mic_rif:
            death_probability += 0.5
        death_probability = min(death_probability, 1.0)

        if self.model.random.random() < death_probability:
            self.model.remove_agent(self)
            return

        effective_replication_rate = self.basal_replication_rate * (1.0 - self.current_fitness_cost)
        replication_probability = max(0, effective_replication_rate)

        if self.model.random.random() < replication_probability:
            offspring_genotype = self._mutate(self.genotype.copy())
            offspring = MtbAgent(
                model=self.model,
                initial_genotype=offspring_genotype,
                mutation_rate_rpoB=self.mutation_rate_rpoB,
                basal_replication_rate=self.basal_replication_rate,
                basal_death_rate=self.basal_death_rate,
                fitness_cost_resistant=self.fitness_cost_resistant
            )
            self.model.place_offspring(offspring, self.pos)

    def remove(self):
        if self.model.grid and hasattr(self, 'pos') and self.pos is not None:
            self.model.grid.remove_agent(self)
        super().remove()
