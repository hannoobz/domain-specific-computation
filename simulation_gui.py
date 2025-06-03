import solara
import plotly.graph_objects as go
# import plotly.express as px # Not used directly, can be removed if go is sufficient
from plotly.subplots import make_subplots
import pandas as pd
# import threading # Not used in the provided snippet for simulation loop
import time # Not used directly in the provided snippet
from typing import Dict, List, Optional # Optional not used, Dict, List are for type hints
from model import MtbResistanceModel
from agents import MtbBacterium
import solara.lab

# Reactive variables for state management
simulation_data = solara.reactive([])
is_running = solara.reactive(False)
current_step = solara.reactive(0)
total_steps = solara.reactive(180)
model_instance = solara.reactive(None) # Optional[MtbResistanceModel]
ui_update_trigger = solara.reactive(0)  # This will force UI updates

# Simulation parameters
day_start = solara.reactive(21)
day_interval = solara.reactive(10)
initial_mtb = solara.reactive(200)
selected_drugs = solara.reactive(["RIF", "INH", "PZA", "EMB"]) # type: solara.Reactive[List[str]]
width = solara.reactive(50)
height = solara.reactive(50)

def reset_simulation():
    """Reset all simulation data"""
    simulation_data.set([])
    current_step.set(0)
    is_running.set(False)
    model_instance.set(None)
    ui_update_trigger.set(ui_update_trigger.value + 1)  # Force UI update

def run_simulation_step():
    """Run a single step of the simulation"""
    model = model_instance.value
    if model is None:
        print("No model instance available")
        return False
    
    try:
        model.step()
        
        # Collect resistance data
        resistant_counts = {"RIF": 0, "INH": 0, "PZA": 0, "EMB": 0}
        persister_count = 0
        replicating_count = 0
        
        # Ensure model.agents is iterable and contains MtbBacterium instances
        current_agents = [agent for agent in model.agents if isinstance(agent, MtbBacterium)]

        for agent in current_agents:
            if agent.resistance_profile.get("RIF", False):
                resistant_counts["RIF"] += 1
            if agent.resistance_profile.get("INH", False):
                resistant_counts["INH"] += 1
            if agent.resistance_profile.get("PZA", False):
                resistant_counts["PZA"] += 1
            if agent.resistance_profile.get("EMB", False):
                resistant_counts["EMB"] += 1
            
            if agent.is_persister:
                persister_count += 1
            if agent.replicating: # Assuming replicating is a boolean attribute
                replicating_count += 1
        
        total_mtb_count = len(current_agents)
        
        # Store step data
        step_data = {
            "day": model.steps,
            "total_mtb": total_mtb_count,
            "resistant_rif": resistant_counts["RIF"],
            "resistant_inh": resistant_counts["INH"],
            "resistant_pza": resistant_counts["PZA"],
            "resistant_emb": resistant_counts["EMB"],
            "persisters": persister_count,
            "replicating": replicating_count,
            "drugs_active": any([model.rif_drug_on, model.inh_drug_on, model.pza_drug_on, model.emb_drug_on])
        }
        
        # Update simulation data
        current_data_list = simulation_data.value.copy()
        current_data_list.append(step_data)
        simulation_data.set(current_data_list)
        current_step.set(model.steps)
        ui_update_trigger.set(ui_update_trigger.value + 1)  # Force UI update
        
        # print(f"Step {model.steps}: Total MTB = {total_mtb_count}, Data points = {len(current_data_list)}")
        return True
        
    except Exception as e:
        print(f"Error in simulation step: {e}")
        # Potentially stop simulation or notify user in UI
        is_running.set(False) # Example: stop simulation on error
        return False

def initialize_simulation():
    """Initialize the simulation model"""
    # Ensure selected_drugs.value is a list of strings as expected by MtbResistanceModel
    drugs_to_use = selected_drugs.value.copy() if selected_drugs.value else []

    model = MtbResistanceModel(
        day_start=day_start.value,
        day_interval=day_interval.value,
        drug_type=drugs_to_use, # Pass the copied list
        initial_mtb=initial_mtb.value,
        width=width.value,
        height=height.value
    )
    model_instance.set(model)
    return model

def start_simulation():
    """Start the simulation"""
    if is_running.value:
        return
    
    reset_simulation() # This also increments ui_update_trigger
    
    # Initialize the model
    initialize_simulation() # This sets model_instance
    is_running.set(True)
    
    # Run one step immediately to show initial data
    if model_instance.value: # Ensure model was initialized
        run_simulation_step() # This increments ui_update_trigger again
    else:
        print("Failed to initialize model for starting simulation.")
        is_running.set(False)


def run_multiple_steps(num_steps):
    """Run multiple simulation steps"""
    for i in range(num_steps):
        if not is_running.value or not model_instance.value:
            break
        if not run_simulation_step(): # run_simulation_step handles its own errors and returns False
            is_running.set(False) # Ensure simulation stops if a step fails
            break
        if current_step.value >= total_steps.value:
            is_running.set(False)
            break

def stop_simulation(): # Though not used by a button, good for completeness
    """Stop the simulation"""
    is_running.set(False)
    ui_update_trigger.set(ui_update_trigger.value + 1) # Ensure UI reflects stopped state

@solara.component
def SimulationControls():
    """Component for simulation control parameters"""
    
    with solara.Card("Simulation Parameters"):
        with solara.Column():
            solara.SliderInt("Treatment Start Day", value=day_start, min=1, max=100)
            solara.SliderInt("Treatment Interval (days)", value=day_interval, min=1, max=30)
            solara.SliderInt("Initial MTB Count", value=initial_mtb, min=50, max=1000)
            solara.SliderInt("Total Simulation Days", value=total_steps, min=50, max=500)
            
            with solara.Row():
                solara.SliderInt("Grid Width", value=width, min=20, max=100)
                solara.SliderInt("Grid Height", value=height, min=20, max=100)
            
            solara.Text("Select Active Drugs:")
            drug_options = ["RIF", "INH", "PZA", "EMB"]
            
            # Use a local variable for selected_drugs.value for this render pass
            # This ensures that `is_selected` is based on the current reactive value.
            current_selected_drugs_list = selected_drugs.value

            for drug in drug_options:
                is_selected = drug in current_selected_drugs_list
                
                # Define a handler that uses the new state from the checkbox
                def create_on_value_handler(drug_name_to_toggle):
                    def on_value_handler(new_state_is_checked: bool):
                        # Get a fresh copy of the list from the reactive variable
                        current_list = selected_drugs.value.copy()
                        if new_state_is_checked:
                            if drug_name_to_toggle not in current_list:
                                current_list.append(drug_name_to_toggle)
                        else:
                            if drug_name_to_toggle in current_list:
                                current_list.remove(drug_name_to_toggle)
                        selected_drugs.set(current_list)
                        # Optionally, trigger a general UI update if other components
                        # need to react immediately to drug selection changes,
                        # though changes to selected_drugs should already trigger re-renders
                        # for components that depend on it.
                        # ui_update_trigger.set(ui_update_trigger.value + 1)
                    return on_value_handler

                solara.Checkbox(label=drug, value=is_selected, on_value=create_on_value_handler(drug))
    
    with solara.Card("Simulation Control"):
        with solara.Row():
            solara.Button(
                "Start Simulation", 
                on_click=start_simulation, 
                disabled=is_running.value,
                color="primary"
            )
            solara.Button(
                "Step Forward", 
                on_click=lambda: run_simulation_step() if model_instance.value and is_running.value else None, 
                disabled=not is_running.value or not model_instance.value
            )
            solara.Button(
                "Run 10 Steps", 
                on_click=lambda: run_multiple_steps(10), 
                disabled=not is_running.value or not model_instance.value
            )
            solara.Button(
                "Reset", 
                on_click=reset_simulation, 
                # Allow reset even if running, could call stop_simulation first
                # disabled=is_running.value 
            )
        
        # Display simulation status
        # This part re-renders if is_running, current_step, total_steps, or simulation_data changes.
        if is_running.value:
            status_message = f"Simulation active... Day {current_step.value}/{total_steps.value}"
            if simulation_data.value:
                latest_data = simulation_data.value[-1]
                status_message += f" | Current MTB count: {latest_data['total_mtb']}"
            solara.Info(status_message)
        elif simulation_data.value: # Simulation not running, but data exists
            solara.Success(f"Simulation ended. {len(simulation_data.value)} data points. Last day: {current_step.value}")
        else: # Not running, no data
            solara.Warning("Click 'Start Simulation' to initialize the model.")


@solara.component
def SimpleDataDisplay():
    """Simple data display component"""
    # This component will re-render if simulation_data.value changes.
    current_sim_data = simulation_data.value
    data_length = len(current_sim_data)
    
    if data_length == 0:
        solara.Info("No simulation data available. Start the simulation to generate data.")
        return
    
    df = pd.DataFrame(current_sim_data)
    
    with solara.Card("Simulation Data Log"):
        solara.Text(f"Data points collected: {data_length}")
        if not df.empty:
            solara.Text(f"Day range: {df['day'].min()} to {df['day'].max()}")
            solara.Text(f"MTB population range: {df['total_mtb'].min()} to {df['total_mtb'].max()}")
            
            solara.HTML("<h4>Latest Data Entries:</h4>")
            last_rows = df.tail(5)
            html_table = last_rows.to_html(index=False, classes="table table-striped table-sm")
            solara.HTML(html_table)
        else:
            solara.Text("DataFrame is empty (this should not happen if data_length > 0).")


@solara.component
def SimplePlot():
    """Simple single plot component"""
    # This component will re-render if simulation_data.value changes.
    current_sim_data = simulation_data.value
    data_length = len(current_sim_data)
    
    if data_length < 1: # Need at least one point to plot
        # Optionally, display a placeholder or message if no data for plot
        # solara.Text("Waiting for data to plot...")
        return
    
    df = pd.DataFrame(current_sim_data)
    if df.empty:
        return

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['day'], 
        y=df['total_mtb'], 
        mode='lines+markers',
        name='Total MTB Population',
        line=dict(color='blue', width=3)
    ))
    
    colors = ['red', 'green', 'orange', 'purple']
    resistance_cols = ['resistant_rif', 'resistant_inh', 'resistant_pza', 'resistant_emb']
    drug_names = ['RIF', 'INH', 'PZA', 'EMB']
    
    for col, drug, color in zip(resistance_cols, drug_names, colors):
        if col in df.columns: # Ensure column exists
            fig.add_trace(go.Scatter(
                x=df['day'], 
                y=df[col], 
                mode='lines+markers',
                name=f'{drug} Resistant',
                line=dict(color=color, width=2)
            ))
    
    fig.update_layout(
        title="MTB Population and Resistance Over Time",
        xaxis_title="Day",
        yaxis_title="Count",
        height=500,
        showlegend=True,
        margin=dict(l=40, r=40, t=40, b=40) # Adjust margins
    )
    
    try:
        solara.FigurePlotly(fig)
    except Exception as e:
        solara.Error(f"Plot rendering error: {e}")

@solara.component
def GridVisualization():
    """Grid visualization component"""
    # This component depends on model_instance.value for its data.
    # It will re-render if SimulationPlots causes it to, via ui_update_trigger.
    current_model = model_instance.value
    
    if not current_model or not hasattr(current_model, 'grid'):
        # solara.Text("Grid data not available or model not initialized.")
        return
    
    grid_data_for_heatmap = [] # z value for heatmap
    
    # Create grid representation
    # Assuming model.grid.width and model.grid.height exist
    for y_pos in range(current_model.grid.height): # Iterating typically y (rows) then x (columns) for heatmaps
        row_counts = []
        for x_pos in range(current_model.grid.width):
            cell_contents = current_model.grid.get_cell_list_contents([(x_pos, y_pos)])
            mtb_count_in_cell = 0
            if cell_contents:
                mtb_count_in_cell = len([agent for agent in cell_contents if isinstance(agent, MtbBacterium)])
            row_counts.append(mtb_count_in_cell)
        grid_data_for_heatmap.append(row_counts)
    
    if not grid_data_for_heatmap:
        solara.Text("No data to display in heatmap.")
        return

    fig = go.Figure(data=go.Heatmap(
        z=grid_data_for_heatmap,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="MTB Count")
    ))
    
    fig.update_layout(
        title="MTB Spatial Distribution",
        xaxis_title="X Position",
        yaxis_title="Y Position",
        height=400, # Adjust as needed
        width=400,  # Adjust as needed
        autosize=True # Or set fixed width/height
    )
    
    try:
        solara.FigurePlotly(fig)
    except Exception as e:
        solara.Error(f"Grid visualization error: {e}")


@solara.component
def SimulationPlots():
    """Component for displaying simulation plots - watches ui_update_trigger and other data"""
    
    # Explicitly depend on these reactive variables to trigger re-render
    trigger_value = ui_update_trigger.value 
    data_len = len(simulation_data.value)
    model_exists = model_instance.value is not None

    # solara.Text(f"Debug: Update #{trigger_value} - Data points: {data_len} - Model: {'Yes' if model_exists else 'No'}")

    if data_len == 0 and not model_exists:
        solara.Info("Start the simulation to view data and visualizations.")
        return
    
    with solara.Card("Data Visualization Dashboard"):
        with solara.lab.Tabs():
            with solara.lab.Tab("Population Chart"):
                if data_len > 0:
                    SimplePlot()
                else:
                    solara.Text("Run simulation steps to see population chart.")
            
            with solara.lab.Tab("Spatial Distribution"):
                if model_exists:
                    GridVisualization()
                else:
                    solara.Text("Start simulation to see spatial distribution.")

            with solara.lab.Tab("Data Log"):
                if data_len > 0:
                    SimpleDataDisplay()
                else:
                    solara.Text("Run simulation steps to see data log.")


@solara.component 
def MetricCard(title: str, value: str, color: str = "#1976d2"): # Value can be string for flexibility
    """Custom metric card component"""
    with solara.Card(style="text-align: center; padding: 10px;"): # Apply style to card itself
        solara.HTML(f"""
            <div>
                <h4 style="margin: 0; color: #666; font-size: 14px;">{title}</h4>
                <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: {color};">{value}</p>
            </div>
        """)

@solara.component
def SimulationSummary():
    """Component for displaying simulation summary"""
    # This component will re-render if simulation_data.value changes.
    current_sim_data = simulation_data.value
    
    if not current_sim_data:
        return # Or show placeholder text
    
    latest_data = current_sim_data[-1]
    
    with solara.Card("Current Simulation Status", margin=0): # Remove default margin if needed
        with solara.ColumnsResponsive(6, [6,6,6,6], [4,4,4,4,4,4]): # Adjust columns for different screen sizes
            MetricCard("Day", str(latest_data.get('day', 'N/A')), "#1976d2")
            MetricCard("Total MTB", str(latest_data.get('total_mtb', 'N/A')), "#1976d2")
            MetricCard("RIF Resistant", str(latest_data.get('resistant_rif', 'N/A')), "#d32f2f")
            MetricCard("INH Resistant", str(latest_data.get('resistant_inh', 'N/A')), "#d32f2f")
            MetricCard("PZA Resistant", str(latest_data.get('resistant_pza', 'N/A')), "#d32f2f")
            MetricCard("EMB Resistant", str(latest_data.get('resistant_emb', 'N/A')), "#d32f2f")
            MetricCard("Persisters", str(latest_data.get('persisters', 'N/A')), "#f57c00")
            MetricCard("Replicating", str(latest_data.get('replicating', 'N/A')), "#388e3c")

@solara.component
def Page():
    """Main application page"""
    
    solara.Title("MTB Drug Resistance Simulation")
    
    with solara.Sidebar():
        SimulationControls() # Contains parameters and control buttons
    
    with solara.Column(gap="10px"): # Add gap between elements in the main column
        SimulationSummary()  # Shows latest metrics
        SimulationPlots()    # Shows charts, grid, and data log in tabs

# To run this application, save this file (e.g., simulation_gui.py)
# and ensure model.py and agents.py are in the same directory or accessible.
# Then execute in terminal:
# solara run simulation_gui.py