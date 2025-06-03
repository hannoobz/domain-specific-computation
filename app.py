from model import MtbResistanceModel
from mesa.experimental.devs import ABMSimulator
from agents import MtbBacterium
from collections import defaultdict
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Mtb Simulation')
    
    parser.add_argument('--start', type=int,
                        help='Start value')
    
    parser.add_argument('--interval', type=int, default=1,
                        help='Interval value (default: 1)')
    
    parser.add_argument('--drug-type',type=str, default="RIF PZA INH EMB",
                        help='Drug types (default: RIF PZA INH EMB)')
    
    parser.add_argument('--days', type=int,
                        help='Number of days')
    
    parser.add_argument('--seed', type=int,default=0,
                        help='Seed')
    
    parser.add_argument('--initial', type=int, default=200, help='Initial Population')

    parser.add_argument('--width', type=int, default=250,
                        help='Width')
    
    parser.add_argument('--height', type=int, default=250,
                        help='Height')

    return parser.parse_args()

args = parse_arguments()
start = args.start
interval = args.interval
drug_type = args.drug_type
days = args.days
seed = args.seed
initial = args.initial
width = args.width
height = args.height

def get_resistance_pattern(agent):
    resistant_drugs = []
    drugs = ["RIF", "INH", "PZA", "EMB"]
    
    for drug in drugs:
        if agent.resistance_profile.get(drug, False):
            resistant_drugs.append(drug)
    
    return tuple(resistant_drugs) if resistant_drugs else ("Susceptible",)

def get_agent_classification(agent):
    resistance_pattern = get_resistance_pattern(agent)
    is_persister = getattr(agent, 'is_persister', False)
    
    if resistance_pattern == ("Susceptible",):
        base_type = "Susceptible"
    else:
        base_type = " + ".join(resistance_pattern)
    
    if is_persister:
        return f"{base_type} (Persister)"
    else:
        return base_type

def count_all_patterns(agents):
    resistance_counts = defaultdict(int)
    full_counts = defaultdict(int)
    persister_counts = {"Persisters": 0, "Non-Persisters": 0}
    
    for agent in agents:
        if isinstance(agent, MtbBacterium):
            resistance_pattern = get_resistance_pattern(agent)
            resistance_counts[resistance_pattern] += 1
            
            full_classification = get_agent_classification(agent)
            full_counts[full_classification] += 1
            
            if agent.is_persister:
                persister_counts["Persisters"] += 1
            else:
                persister_counts["Non-Persisters"] += 1
    
    return resistance_counts, full_counts, persister_counts

def print_detailed_summary(resistance_counts, full_counts, persister_counts, total_count, day):
    print(f"Day {day}: Total Mtb = {total_count}")
    if not resistance_counts:
        print("  No agents remaining")
        return
    print(f"  Persisters: {persister_counts['Persisters']}, Non-Persisters: {persister_counts['Non-Persisters']}")
    print()
    print("  Resistance Patterns:")
    sorted_resistance = sorted(resistance_counts.items(), 
                             key=lambda x: (0 if x[0] == ("Susceptible",) else len(x[0]), x[0]))
    
    for pattern, count in sorted_resistance:
        if pattern == ("Susceptible",):
            print(f"    Susceptible: {count}")
        else:
            pattern_str = " + ".join(pattern)
            print(f"    {pattern_str}: {count}")
    
    print()
    
    print("  Detailed Breakdown:")
    sorted_full = sorted(full_counts.items(), 
                        key=lambda x: (0 if x[0].startswith("Susceptible") else 
                                     len([d for d in ["RIF", "INH", "PZA", "EMB"] if d in x[0]]), x[0]))
    
    for classification, count in sorted_full:
        print(f"    {classification}: {count}")

model = MtbResistanceModel(
    seed=int(seed),
    day_start= start,
    day_interval=interval,
    drug_type= drug_type,
    initial_mtb=initial,
    width=width,
    height=height,
    simulator=ABMSimulator(),
)

print(f"Starting simulation. Treatment from day {model.day_start_treatment}, interval {model.day_treatment_interval} day(s).")
print(f"Active drugs initially configured: {model.active_drugs_config}")
print(f"Initial Mtb count: {len(model.agents)}")
print("=" * 60)

for i in range(days):
    model.step()
    
    resistance_counts, full_counts, persister_counts = count_all_patterns(model.agents)
    total_mtb_count = len(model.agents)
    
    print_detailed_summary(resistance_counts, full_counts, persister_counts, total_mtb_count, i+1)
    print("-" * 60)

print(f"\nSimulation complete after {days} days.")

final_resistance_counts, final_full_counts, final_persister_counts = count_all_patterns(model.agents)
final_total_count = len(model.agents)

print("=" * 60)
print("FINAL COMPREHENSIVE SUMMARY")
print("=" * 60)
print_detailed_summary(final_resistance_counts, final_full_counts, final_persister_counts, final_total_count, days)