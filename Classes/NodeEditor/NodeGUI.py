from tkinter import VERTICAL
import dearpygui.dearpygui as dpg
import networkx as nx

# from segmentation.dearpygui_nodeeditor_template.src.base.node_editor import callback_add_node

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

# callback runs when user attempts to connect attributes
def add_node (sender, app_data, user_data):
    # app_data -> (link_id1, link_id2)
    n = str(G.number_of_nodes() + 1)
    G.add_node('{}'.format(n))

    with dpg.node(label='Node {}'.format(n), parent=user_data):
        with dpg.node_attribute(label='In{}.1'.format(n)):
            dpg.add_input_float(label='FIn{}.1'.format(n), width=200)

        with dpg.node_attribute(label='In{}.2'.format(n),  attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_input_float(label='FIn{}.2'.format(n), width=200)

# callback runs when user attempts to connect attributes
def add_node (sender, app_data, user_data):
    # app_data -> (link_id1, link_id2)
    n = str(G.number_of_nodes() + 1)
    G.add_node('{}'.format(n))

    with dpg.node(label='Node {}'.format(n), parent=user_data):
        with dpg.node_attribute(label='In{}.1'.format(n)):
            dpg.add_input_float(label='FIn{}.1'.format(n), width=200)

        with dpg.node_attribute(label='In{}.2'.format(n),  attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_input_float(label='FIn{}.2'.format(n), width=200)


        # with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
        #     dpg.add_input_float(label="F4", width=200)    

# callback runs when user attempts to connect attributes
def del_node_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    dpg.add_node(app_data[0], parent=sender)
    G.add_node(app_data[0])

def set_callback(self, callback):
    dpg.set_item_callback(self.button_id, callback)

# def add_node_callback(sender, app_data, user_data):
#     node_name = dpg.get_value(input_id)
#     if node_name and node_name not in G:
#         G.add_node(node_name)
#         print(f"Added node: {node_name}")  # This print statement can be replaced with a logger in a GUI.
#     else:
#         print("Node already exists or invalid name.")  # Adjust as needed for user feedback in GUI.

def button_callback():
    print("Button has been pressed!")

   
with dpg.window(label="Tutorial", width=500, height=500):
    with dpg.group(horizontal=True):
        with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight,width=400, height=400):
            pass
            # add_node()
            # add_node()

        # with dpg.node(label="Node 1"):
        #     with dpg.node_attribute(label="In1"):
        #         dpg.add_input_float(label="F1", width=150)

        #     with dpg.node_attribute(label="Out1", attribute_type=dpg.mvNode_Attr_Output):
        #         dpg.add_input_float(label="F2", width=150)

        # with dpg.node(label="Node 2"):
        #     with dpg.node_attribute(label="In2"):
        #         dpg.add_input_float(label="F3", width=200)

        #     with dpg.node_attribute(label="Out2", attribute_type=dpg.mvNode_Attr_Output):
        #         dpg.add_input_float(label="F4", width=200)

# with dpg.window(label="Tutorial", width=500, height=500):
    # dpg.add_button(label="delete custom_series using parent", callback=lambda: dpg.delete_item("win", children_only=True))
    
        # button1 = dpg.add_button(label="Press Me!",callback=callback_add_node)

        # with dpg.group(width=100, height=400):
        dpg.add_child_window(height=500, width=500)
        
        b1 = dpg.add_button(label="Press Me!")
        dpg.configure_item(b1, user_data=dpg.last_item(), callback=add_node)
            # slider_int = dpg.add_slider_int(label="Slide to the left!", width=100)
            # slider_float = dpg.add_slider_float(label="Slide to the right!", width=100)

        # An item's unique identifier (tag) is returned when
        # creating items.
        # print(f"Printing item tag's: {window}, {button1}, {slider_int}, {slider_float}")



dpg.create_viewport(title='Custom Title', width=2000, height=2600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()