#!/usr/bin/env python3
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import tf_transformations

def create_pose_stamped(navigator, position_x, position_y, rotation_z):
    q_x, q_y, q_z, q_w = tf_transformations.quaternion_from_euler(0.0, 0.0, rotation_z)
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = position_x
    goal_pose.pose.position.y = position_y
    goal_pose.pose.position.z = 0.0
    goal_pose.pose.orientation.x = q_x
    goal_pose.pose.orientation.y = q_y
    goal_pose.pose.orientation.z = q_z
    goal_pose.pose.orientation.w = q_w
    return goal_pose
    
def initialize_initial_pose(nav,position_x, position_y, rotation_z):
	# --- Set initial pose ---
    # !!! Comment if the initial pose is already set !!!
    initial_pose = create_pose_stamped(nav, position_x, position_y, rotation_z)
    nav.setInitialPose(initial_pose)

    # --- Wait for Nav2 ---
    nav.waitUntilNav2Active()
    
    
def go_to_goal(nav,position_x, position_y, rotation_z):
	# --- Create some Nav2 goal poses ---
    goal_pose = create_pose_stamped(nav, position_x, position_y, rotation_z)

    # --- Going to one pose ---
    nav.goToPose(goal_pose)
    while not nav.isTaskComplete():
            feedback = nav.getFeedback()
            
    # --- Get the result ---
    print(nav.getResult())
    


def main():
    # --- Init ROS2 communications and Simple Commander API ---
    rclpy.init()
    nav = BasicNavigator()
    initialize_initial_pose(nav, -2.0,-0.5,0.0)
    go_to_goal(nav, 1.79, 0.0, 0.0)

	

    rclpy.shutdown()

if __name__ == '__main__':
    main()   

    
