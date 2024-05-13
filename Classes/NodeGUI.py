import dearpygui.dearpygui as dpg
import networkx as nx

# Initialize a graph
G = nx.Graph()

dpg.create_context()

# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)

# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    dpg.delete_item(app_data)

def set_callback(self, callback):
    dpg.set_item_callback(self.button_id, callback)

def add_node_callback(sender, app_data, user_data):
    node_name = dpg.get_value(input_id)
    if node_name and node_name not in G:
        G.add_node(node_name)
        print(f"Added node: {node_name}")  # This print statement can be replaced with a logger in a GUI.
    else:
        print("Node already exists or invalid name.")  # Adjust as needed for user feedback in GUI.

def button_callback():
    print("Button has been pressed!")

    
with dpg.window(label="Tutorial", width=2000, height=2000):
    with dpg.node_editor(callback=link_callback, delink_callback=delink_callback):
        with dpg.node(label="Node 1"):
            with dpg.node_attribute(label="Node A1"):
                dpg.add_input_float(label="F1", width=150)

            with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(label="F2", width=150)

        with dpg.node(label="Node 2"):
            with dpg.node_attribute(label="Node A3"):
                dpg.add_input_float(label="F3", width=200)

            with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(label="F4", width=200)


    # dpg.add_button(label="delete custom_series using parent", callback=lambda: dpg.delete_item("win", children_only=True))
    with dpg.window(label="Tutorial", width=2000, height=2000) as window:
        button1 = dpg.add_button(label="Press Me!")

        slider_int = dpg.add_slider_int(label="Slide to the left!", width=100)
        slider_float = dpg.add_slider_float(label="Slide to the right!", width=100)

        # An item's unique identifier (tag) is returned when
        # creating items.
        print(f"Printing item tag's: {window}, {button1}, {slider_int}, {slider_float}")



dpg.create_viewport(title='Custom Title', width=2000, height=2600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()