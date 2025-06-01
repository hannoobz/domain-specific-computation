from model import MtbResistanceModel
from agents import MtbBacterium 

model = MtbResistanceModel(
    day_start=21,
    day_interval=10,
    # drug_type=["PZA"],
    drug_type=["RIF", "INH", "PZA", "EMB"],
    initial_mtb=200,
    width=50,
    height=50
)

print(f"Starting simulation. Treatment from day {model.day_start_treatment}, interval {model.day_treatment_interval} day(s).")
print(f"Active drugs initially configured: {model.active_drugs_config}")
print(f"Initial Mtb count: {len(model.agents)}")
print("-" * 30)

for i in range(180): 
    model.step()
    resistant_counts = {
        "RIF": 0,
        "INH": 0,
        "PZA": 0,
        "EMB": 0
    }
    
    if model.agents:
        for agent in model.agents:
            if isinstance(agent, MtbBacterium):
                if agent.resistance_profile.get("RIF", False):
                    resistant_counts["RIF"] += 1
                if agent.resistance_profile.get("INH", False):
                    resistant_counts["INH"] += 1
                if agent.resistance_profile.get("PZA", False):
                    resistant_counts["PZA"] += 1
                if agent.resistance_profile.get("EMB", False):
                    resistant_counts["EMB"] += 1
            
    total_mtb_count = len(model.agents)
    print(f"Day {model.steps}: "
          f"Total Mtb = {total_mtb_count}, "
          f"Res-RIF = {resistant_counts['RIF']}, "
          f"Res-INH = {resistant_counts['INH']}, "
          f"Res-PZA = {resistant_counts['PZA']}, "
          f"Res-EMB = {resistant_counts['EMB']}")

print("-" * 30)
print(f"\nSimulation complete after {model.steps} steps.")

final_resistant_counts = {"RIF": 0, "INH": 0, "PZA": 0, "EMB": 0}
if model.agents:
    for agent in model.agents:
        if isinstance(agent, MtbBacterium):
            if agent.resistance_profile.get("RIF", False): final_resistant_counts["RIF"] += 1
            if agent.resistance_profile.get("INH", False): final_resistant_counts["INH"] += 1
            if agent.resistance_profile.get("PZA", False): final_resistant_counts["PZA"] += 1
            if agent.resistance_profile.get("EMB", False): final_resistant_counts["EMB"] += 1

final_total_count = len(model.agents)
print(f"Final state: Total Mtb = {final_total_count}, "
      f"Res-RIF = {final_resistant_counts['RIF']}, "
      f"Res-INH = {final_resistant_counts['INH']}, "
      f"Res-PZA = {final_resistant_counts['PZA']}, "
      f"Res-EMB = {final_resistant_counts['EMB']}")