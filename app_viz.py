from mesa.experimental.devs import ABMSimulator
from agents import MtbBacterium
from model import MtbResistanceModel

from mesa.visualization import (
    CommandConsole,
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)


def mtb_potrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 100,
    }

    portrayal["color"] = "tab:red"
    portrayal["marker"] = "o"
    portrayal["zorder"] = 2

    if isinstance(agent, MtbBacterium):
        if agent.is_persister:
            portrayal["color"] = "#8B0000"
            portrayal["zorder"] = 5
            portrayal["size"] = 150
        if agent.resistance_profile["RIF"]:
            portrayal["color"] = "#D4FF00"
            portrayal["zorder"] = 5
            portrayal["size"] = 150
        if agent.resistance_profile["INH"]:
            portrayal["color"] = "#37FF00"
            portrayal["zorder"] = 5
            portrayal["size"] = 150
        if agent.resistance_profile["PZA"]:
            portrayal["color"] = "#0044FF"
            portrayal["zorder"] = 5
            portrayal["size"] = 150
        if agent.resistance_profile["EMB"]:
            portrayal["color"] = "#FF00D9"
            portrayal["zorder"] = 5
            portrayal["size"] = 150


    return portrayal


model_params = {
    "seed": {
        "type": "InputText",
        "value": 0,
        "label": "Random Seed",
    },
    "day_start": {
        "type": "InputText",
        "value": 21,
        "label": "Treatment start day",
    },
    "initial_mtb": {
        "type": "InputText",
        "value": 200,
        "label": "Initial Mtb population",
    },
    "day_interval": {
        "type": "InputText",
        "value": 1,
        "label": "Treatment interval",
    },
    "drug_type": {
        "type": "InputText",
        "value": "RIF",
        "label": "Drug type(s)",
    },
    "width": Slider("Grid Width", 250, 1, 500),
    "height": Slider("Grid Height", 250, 1, 500),
}



def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.figure.set_size_inches(25,25)

def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))
    ax.figure.set_size_inches(5,2)

mtb_susceptible = make_plot_component(
    {
        "Total Mtb": "#000000",
        "Susceptible": "tab:red",
     },
    post_process=post_process_lines,
)

mtb_resistant= make_plot_component(
    {
        "Persister": "#8B0000",
        "Res-RIF": "#D4FF00",
        "Res-INH": "#37FF00",
        "Res-PZA": "#0044FF",
        "Res-EMB": "#FF00D9",
     },
    post_process=post_process_lines,
)

space_component = make_space_component(
    mtb_potrayal, draw_grid=False, post_process=post_process_space
)


simulator = ABMSimulator()
model = MtbResistanceModel(
    simulator = simulator,
    )

page = SolaraViz(
    model,
    components=[mtb_susceptible,space_component, mtb_resistant, CommandConsole],
    model_params=model_params,
    name="Mtb Simulation",
    simulator=simulator,
)
page  # noqa
