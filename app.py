import mesa
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)

from agents import MtbAgent, BackgroundPatchAgent
from model import MtbEnvironmentModel
SUSCEPTIBLE_COLOR = "#00DD00"
RESISTANT_COLOR = "#FF0000"
BACKGROUND_COLOR = "#F0F0F0" 

def mtb_agent_portrayal(agent):
    if agent is None or not hasattr(agent, 'pos') or agent.pos is None:
        return None

    if isinstance(agent, MtbAgent):
        portrayal = {"size": 25, "marker": "o", "zorder": 2}
        if agent.is_resistant_rif:
            portrayal["color"] = RESISTANT_COLOR
        else:
            portrayal["color"] = SUSCEPTIBLE_COLOR
        return portrayal
    elif isinstance(agent, BackgroundPatchAgent):
        return {"size": 75, "marker": "s", "color": BACKGROUND_COLOR, "zorder": 1}
    return None

def post_process_grid(ax):
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.get_figure().set_size_inches(7, 7)

mtb_model_params = {
    "seed": {"type": "InputText", "value": "None", "label": "Random Seed (int or None)"},
    "width": {"type": "InputText", "value": "30", "label": "Grid Width"},
    "height": {"type": "InputText", "value": "30", "label": "Grid Height"},
    "initial_mtb_population": Slider("Initial Mtb Population", 50, 0, 200, 10),
    "drug_start_step": Slider("Drug Start Step", 20, 0, 100, 5),
    "drug_duration_steps": Slider("Drug Duration (steps)", 100, 10, 200, 10),
    "drug_applied_concentration": Slider("RIF Applied Conc.", 5.0, 0.0, 20.0, 0.5),
    "rif_mic": Slider("RIF MIC (Susceptible)", 1.0, 0.1, 5.0, 0.1),
    "rpoB_mutation_rate": Slider("RIF Mutation Rate (log10)", -6, -9, -5, 0.1),
    "basal_replication_rate_mtb": Slider("Mtb Rep. Rate", 0.1, 0.01, 0.3, 0.01),
    "basal_death_rate_mtb": Slider("Mtb Death Rate", 0.01, 0.001, 0.05, 0.001),
    "fitness_cost_rif_resistant": Slider("Fitness Cost (RIF Resist.)", 0.1, 0.0, 0.3, 0.01),
    "max_iters": {"type": "InputText", "value": "200", "label": "Max Iterations (Steps)"},
}

space_component = make_space_component(
    mtb_agent_portrayal,
    draw_grid=True,
    post_process=post_process_grid
)

plot_styling_dict = {
    "TotalMtb": "black",
    "SusceptibleMtb_RIF": SUSCEPTIBLE_COLOR,
    "ResistantMtb_RIF": RESISTANT_COLOR,
    "RifampicinConcentration": "blue"
}
chart_component = make_plot_component(plot_styling_dict)

initial_model_instance_params = {
    "width": "30", "height": "30", "initial_mtb_population": "50",
    "drug_start_step": "20", "drug_duration_steps": "100",
    "drug_applied_concentration": "5.0", "rif_mic": "1.0",
    "rpoB_mutation_rate": "-6", 
    "basal_replication_rate_mtb": "0.1", "basal_death_rate_mtb": "0.01",
    "fitness_cost_rif_resistant": "0.1", "max_iters": "200", "seed": "None",
    "drug_name": "Rifampicin"
}
mtb_sim_model_instance = MtbEnvironmentModel(**initial_model_instance_params)

page_components = [chart_component]
if hasattr(mtb_sim_model_instance, 'grid') and mtb_sim_model_instance.grid is not None:
    page_components.insert(0, space_component)

page = SolaraViz(
    mtb_sim_model_instance,
    components=page_components,
    model_params=mtb_model_params,
    name="Simplified Mtb Evolution (with Background)",
)

page
