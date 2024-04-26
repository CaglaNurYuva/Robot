import os
import subprocess
import tkinter as tk
import signal
import sys

import firebase_admin
from firebase_admin import credentials, firestore
from tkinter import Tk, Button
import time

# Added functionality: it can get initial positions as input from user and updates database accordingly.

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

initialPosition_ref = None
root = None

def handle_initialPosition(table_number,position_x,position_y,rotation_z):
    global initialPosition_ref
    
    # create a str, if table_number is 0, str should be 'Initial'
    # if table_number is not 0, str should be 'table' + table_number  append them
    if table_number == 0:
        str_name = "initial"
    else:
        str_name = f"table{table_number}"
     
    # Query Firestore to find the document where OrderID is equal to "id1"
    query = db.collection("initialPosition").where("location", "==", str_name).get()

    # Check if any documents match the query
    if query:
        for doc in query:
            new_id = doc.id
            db.collection('initialPosition').document(new_id).update({"position_x": position_x})
            db.collection('initialPosition').document(new_id).update({"position_y": position_y})
            db.collection('initialPosition').document(new_id).update({"rotation_z": rotation_z})
            print("Updated in initialPosition!")
            break


    else:
        print("No document found with location equal to str_name")
        initial_data = {"location": str_name, "position_x": position_x, "position_y": position_y, "rotation_z":rotation_z}
       
        db.collection("initialPosition").add(initial_data)
        print("New entry added successfully to the initialPosition!")

    initialPosition_ref = db.collection('initialPosition')



# Define a function to handle document changes
def on_snapshot(col_snapshot, changes, read_time):
    try:
        print("Received document changes:")
        for change in changes:
            if change.type.name == 'ADDED':
                print(f"Added: {change.document.id}")
                print(f"Data: {change.document.to_dict()}")
            elif change.type.name == 'MODIFIED':
                print(f"Modified: {change.document.id}")
                print(f"Data: {change.document.to_dict()}")
            elif change.type.name == 'REMOVED':
                print(f"Removed: {change.document.id}")
        
    except Exception as e:
        print("Error in on_snapshot:", e)
        

def start_mapping():
    command = "ros2 launch my_robot_bringup main__mapping.launch.py"
    process = subprocess.Popen(command, shell=True)
    

def control_robot_manually():
    command = "ros2 run turtlebot3_teleop teleop_keyboard"
    process = subprocess.Popen(command, shell=True)
    

def save_map():
    command = "ros2 run nav2_map_server map_saver_cli -f ros2_ws/src/my_robot_bringup/maps/my_map"
    subprocess.Popen(command, shell=True)


def start_navigation():
    # Terminate all running processes
    
    # When these are terminated, navigation is not worked because some background processes are also killed.
    #subprocess.Popen("pkill -SIGINT -f 'ros2 launch my_robot_bringup main__mapping.launch.py'", shell=True)
    #subprocess.Popen("pkill -SIGINT -f 'ros2 run turtlebot3_teleop teleop_keyboard'", shell=True)

    command = "ros2 launch my_robot_bringup main__navigation.launch.py"
    process = subprocess.Popen(command, shell=True)
    
def get_user_input():
    global root
	
    input_window = tk.Toplevel(root)
    input_window.title("Select Option")

    def create_input_window(table_number):
        global root 
    	
        new_window = tk.Toplevel(root)
        new_window.title(f"Enter Float Values for Table {table_number}")
        
        label_text = f"Position X for {'Initial' if table_number == 0 else f'Table {table_number}'}"
        tk.Label(new_window, text=label_text).grid(row=0, column=0)
        entry1 = tk.Entry(new_window)
        entry1.grid(row=0, column=1)

        tk.Label(new_window, text=f"Position Y for {'Initial' if table_number == 0 else f'Table {table_number}'}").grid(row=1, column=0)
        entry2 = tk.Entry(new_window)
        entry2.grid(row=1, column=1)

        tk.Label(new_window, text=f"Rotation Z for {'Initial' if table_number == 0 else f'Table {table_number}'}").grid(row=2, column=0)
        entry3 = tk.Entry(new_window)
        entry3.grid(row=2, column=1)

        def submit_input():
            try:
                position_x = float(entry1.get())
                position_y = float(entry2.get())
                rotation_z = float(entry3.get())
                # table_number ve diğer posları kullan,initialPosition modifiye et ya da ekle
                handle_initialPosition(table_number, position_x, position_y, rotation_z)
                print(f"Table {table_number} - Position X: {position_x}, Position Y: {position_y}, Rotation Z: {rotation_z}")
                new_window.destroy()  # Close the input window
            except ValueError:
                print("Please enter valid floats.")

        submit_button = tk.Button(new_window, text="Submit", command=submit_input)
        submit_button.grid(row=3, columnspan=2)

    # Create buttons with appropriate names
    tk.Button(input_window, text="Initial", command=lambda: create_input_window(0)).pack()
    for i in range(1, 6):
        tk.Button(input_window, text=f"Table {i}", command=lambda i=i: create_input_window(i)).pack()

    tk.Button(input_window, text="Close", command=input_window.destroy).pack()



def exit_program():
    global root
    # Terminate all running processes
    subprocess.Popen("pkill -SIGINT -f 'ros2 launch my_robot_bringup main__mapping.launch.py'", shell=True)
    subprocess.Popen("pkill -SIGINT -f 'ros2 run turtlebot3_teleop teleop_keyboard'", shell=True)
    subprocess.Popen("pkill -SIGINT -f 'ros2 launch my_robot_bringup main__navigation.launch.py'", shell=True)
    
    # Exit the application
    root.destroy()



def main():
	global initialPosition_ref, root
	
	# Specify the collection to listen to
	initialPosition_ref = db.collection('initialPosition')  
	
	# Listen for changes in the collection
	col_query = initialPosition_ref.on_snapshot(on_snapshot)

    # Commands to execute when the program starts
	startup_commands = [
		"cd ros2_ws && colcon build && source install/setup.bash"
	]

	for command in startup_commands:
		subprocess.run(command, shell=True)

	# Create the main application window
	root = tk.Tk()
	root.title("ROS2 Control Panel")

	# Create buttons for each action
	mapping_button = tk.Button(root, text="Start Mapping", command=start_mapping)
	mapping_button.pack(pady=5)

	control_button = tk.Button(root, text="Control Robot Manually", command=control_robot_manually)
	control_button.pack(pady=5)

	save_map_button = tk.Button(root, text="Save Map", command=save_map)
	save_map_button.pack(pady=5)

	navigation_button = tk.Button(root, text="Start Navigation", command=start_navigation)
	navigation_button.pack(pady=5)

	#start_process_goals_button = tk.Button(root, text="Start Processing Goals", command=start_navigation)
	#start_process_goals_button.pack(pady=5)

	#process_goals_button = tk.Button(root, text="Start Processing Goals", command=start_navigation)
	#process_goals_button.pack(pady=5)



	#end_process_goals_button = tk.Button(root, text="End Processing Goals", command=start_navigation)
	#end_process_goals_button.pack(pady=5)
	# Button to get user input
	input_button = tk.Button(root, text="Get Initial Coordinates", command=get_user_input)
	input_button.pack(pady=5)



	# Create an Exit button
	exit_button = tk.Button(root, text="Exit", command=exit_program)
	exit_button.pack(pady=5)

	# Run the application's event loop
	root.mainloop()

    
    
    

if __name__ == '__main__':
    main()   

