import networkx as nx
import matplotlib.pyplot as plt
import dearpygui.dearpygui as dpg

# Initialize a graph
G = nx.Graph()

def add_node(sender, app_data, user_data):
    node_name = dpg.get_value("NodeName")
    if node_name and node_name not in G:
        G.add_node(node_name)
        dpg.log_info(f"Added node: {node_name}", logger="AppLogger")
        show_graph()
    else:
        dpg.log_error("Node already exists or invalid name.", logger="AppLogger")

def show_graph():
    plt.figure(figsize=(5, 5))
    nx.draw(G, with_labels=True, font_weight='bold', node_color='skyblue')
    plt.title("Graph Visualization")
    plt.savefig("graph.png")
    plt.close()
    dpg.delete_item("GraphPlot", children_only=True)
    with dpg.drawlist(parent="GraphPlotWindow", width=300, height=300):
        dpg.draw_image("graph.png", [0, 0], [300, 300])

dpg.create_context()

with dpg.handler_registry():
    dpg.add_key_press_handler(key=dpg.mvKey_Escape, callback=lambda s, a, u: dpg.stop_dearpygui())

with dpg.window(label="Main Window") as main_window:
    dpg.add_input_text(tag="NodeName", label="Node Name")
    dpg.add_button(label="Add Node", callback=add_node)
    # logger_id = dpg.add_logger(level=dpg.mvLogLevel_Debug, auto_scroll=True, tag="AppLogger")
    dpg.add_drawlist(width=300, height=300, parent=main_window, tag="GraphPlotWindow")


dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

show_graph()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
