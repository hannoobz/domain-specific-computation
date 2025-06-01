from mesa import Agent
import math

class MtbBacterium(Agent):
    def __init__(self, model, resistance_profile=None, initial_is_persister=False):
        self.model = model

        if resistance_profile:
            self.resistance_profile = resistance_profile.copy()
        else:
            self.resistance_profile = {
                "RIF": False,
                "INH": False,
                "PZA": False,
                "EMB": False
            }
        
        self.is_persister = initial_is_persister
        if self.is_persister:
            self.replicating = False
        else:
            self.replicating = True

        self.pos = None

    def _get_effective_kill_rate(self, drug_name_upper):
        model = self.model
        drug_name_lower = drug_name_upper.lower()

        k_max_daily_drug_effect = getattr(model, f"{drug_name_lower}_k_max_kill_daily")
        ec50_ng_ml = getattr(model, f"{drug_name_lower}_ec50_ng_ml")
        hill_coefficient = getattr(model, f"{drug_name_lower}_hill_coefficient")
        drug_concentration_ng_ml = getattr(model, f"{drug_name_lower}_active_concentration_ng_ml")

        conc_pow_hill = math.pow(drug_concentration_ng_ml, hill_coefficient)
        ec50_pow_hill = math.pow(ec50_ng_ml, hill_coefficient)

        if (ec50_pow_hill + conc_pow_hill) == 0:
            effective_kill_rate = 0.0
        else:
            effective_kill_rate = k_max_daily_drug_effect * (conc_pow_hill / (ec50_pow_hill + conc_pow_hill))
        
        return effective_kill_rate

    def step(self):
        model = self.model

        if not self.is_persister:
            is_any_drug_active_in_model = model.rif_drug_on or model.inh_drug_on or model.pza_drug_on or model.emb_drug_on
            if is_any_drug_active_in_model and self.random.random() < model.prob_susceptible_to_persister:
                self.is_persister = True
                self.replicating = False
        else: 
            is_any_drug_active_in_model = model.rif_drug_on or model.inh_drug_on or model.pza_drug_on or model.emb_drug_on
            if (not is_any_drug_active_in_model and self.random.random() < model.prob_persister_to_susceptible_no_drug) or \
               (is_any_drug_active_in_model and self.random.random() < model.prob_persister_to_susceptible_drug_on):
                self.is_persister = False
                self.replicating = True
        
        max_effective_rate_today = 0.0
        active_drugs_susceptible_to = []

        if model.rif_drug_on and not self.resistance_profile["RIF"] and self.replicating:
            active_drugs_susceptible_to.append("RIF")
        if model.inh_drug_on and not self.resistance_profile["INH"] and self.replicating:
            active_drugs_susceptible_to.append("INH")
        if model.pza_drug_on and not self.resistance_profile["PZA"] and self.replicating:
            active_drugs_susceptible_to.append("PZA")
        if model.emb_drug_on and not self.resistance_profile["EMB"] and self.replicating:
            active_drugs_susceptible_to.append("EMB")

        if active_drugs_susceptible_to:
            for drug_name in active_drugs_susceptible_to:
                current_drug_rate = self._get_effective_kill_rate(drug_name)
                if current_drug_rate > max_effective_rate_today:
                    max_effective_rate_today = current_drug_rate
            final_kill_probability_today = 1.0 - math.exp(-max_effective_rate_today)
        else:
            final_kill_probability_today = 0.0
        
        final_kill_probability_today = max(0.0, min(final_kill_probability_today, 1.0))

        if self.random.random() < final_kill_probability_today:
            self.remove()
            return

        if self.replicating and not self.is_persister and self.random.random() < model.replication_prob_per_day:
            child_resistance_profile = self.resistance_profile.copy()

            if not self.resistance_profile["RIF"] and self.random.random() < model.rif_mutation_rate:
                child_resistance_profile["RIF"] = True
            if not self.resistance_profile["INH"] and self.random.random() < model.inh_mutation_rate:
                child_resistance_profile["INH"] = True
            if not self.resistance_profile["PZA"] and self.random.random() < model.pza_mutation_rate:
                child_resistance_profile["PZA"] = True
            if not self.resistance_profile["EMB"] and self.random.random() < model.emb_mutation_rate:
                child_resistance_profile["EMB"] = True
            
            child = MtbBacterium(model=model, resistance_profile=child_resistance_profile, initial_is_persister=False) # Children are born susceptible
            
            if self.pos:
                model.grid.place_agent(child, self.pos)
                model.agents.add(child)


    def remove(self):
        if self.pos: 
             self.model.grid.remove_agent(self)
             self.pos = None 
        if self in self.model.agents:
             self.model.agents.remove(self)