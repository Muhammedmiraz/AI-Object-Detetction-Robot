AI Object Detection Robot

A Python-based robot simulation that combines real-time object detection using YOLO with grid-based robot navigation and obstacle avoidance.

Project Overview

This project demonstrates how computer vision and pathfinding can be combined in a software simulation. The robot navigates a virtual grid containing obstacles, while a webcam and a pretrained YOLO model detect objects in the surrounding camera view.

Note: This is a software simulation project. It does not control a physical robot. Camera detections and virtual-grid navigation are separate components unless explicitly connected in the code.

Features

* Real-time object detection using YOLO
* Webcam integration with OpenCV
* Grid-based robot simulation using Tkinter
* Virtual obstacles and a goal position
* Automated navigation and manual movement controls
* Pause and reset controls

Technologies Used

* Python
* OpenCV
* Ultralytics YOLO
* Tkinter
* Pathfinding algorithms

Requirements

* Python 3
* A webcam for live object detection
* The required Python packages
* The YOLO model file used by the project (yolov8n.pt)

Installation

1. Clone or download this repository.
2. Open the project folder in VS Code.
3. Install the required packages:

pip install opencv-python ultralytics

4. Ensure yolov8n.pt is available in the project folder.
5. Run the simulation:

python robot_simulation_portfolio.py

How to Use

1. Start the simulation.
2. Enable YOLO to begin camera-based object detection.
3. Use the movement controls for manual navigation.
4. Use Auto Mode to test automated movement through the virtual grid.
5. Observe the robot’s position, virtual obstacles, and goal.

Project Purpose

This project was developed to practise Python programming, computer vision, object detection, pathfinding, and simulation-based robotics.

Future Improvements

* Connect camera detections to virtual-grid navigation.
* Improve obstacle avoidance and navigation decisions.
* Add more simulation scenarios and testing.
* Improve the user interface and detection status display.

Project Demo

![AI Object Detection Robot with YOLO Live Detection](YOLO%20Live%20Detection.jpeg)

Author
Muhammed Miraz P

Developed as a personal learning project in AI, machine learning, and robotics.
