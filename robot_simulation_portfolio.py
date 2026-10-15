import tkinter as tk
from collections import deque

try:
    from yolo_obstacle_detector_portfolio import YOLOObstacleDetector
except ImportError:
    YOLOObstacleDetector = None

COLS = 15
ROWS = 11
CELL = 42
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL
START = (1, 1)
GOAL = (13, 9)

OBSTACLES = {
    (4, 1), (4, 2), (4, 3), (4, 4),
    (7, 2), (8, 2), (9, 2),
    (7, 5), (8, 5), (9, 5),
    (3, 7), (4, 7), (5, 7),
    (10, 7), (11, 7), (12, 7)
}


class RobotSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("AI ROBOT SIMULATION")
        self.root.resizable(False, False)
        self.root.configure(bg="#17212b")

        self.robot = START
        self.auto_running = False
        self.after_id = None
        self.camera_after_id = None
        self.steps = 0

        self.yolo_detector = None
        self.yolo_enabled = False
        self.yolo_obstacle_ahead = False
        self.yolo_status = "YOLO DISABLED"

        tk.Label(
            root, text="AI ROBOT SIMULATION",
            font=("Arial", 18, "bold"), fg="#00bcd4",
            bg="#17212b", pady=12
        ).pack(fill="x")

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT,
            bg="#f4f7f9", highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=5)

        self.status_label = tk.Label(
            root, text="READY - Use arrow keys or start Auto Mode",
            font=("Arial", 10, "bold"), fg="#00bcd4",
            bg="#17212b", pady=8
        )
        self.status_label.pack(fill="x")

        self.position_label = tk.Label(
            root, text="Position: (1, 1) | Steps: 0",
            font=("Arial", 9), fg="white", bg="#17212b"
        )
        self.position_label.pack()

        controls = tk.Frame(root, bg="#17212b")
        controls.pack(pady=8)

        tk.Button(controls, text="↑", width=5,
                  command=lambda: self.move(0, -1)).grid(row=0, column=1, padx=3, pady=3)
        tk.Button(controls, text="←", width=5,
                  command=lambda: self.move(-1, 0)).grid(row=1, column=0, padx=3, pady=3)
        tk.Button(controls, text="↓", width=5,
                  command=lambda: self.move(0, 1)).grid(row=1, column=1, padx=3, pady=3)
        tk.Button(controls, text="→", width=5,
                  command=lambda: self.move(1, 0)).grid(row=1, column=2, padx=3, pady=3)
        tk.Button(controls, text="AUTO MODE", width=12,
                  command=self.start_auto).grid(row=2, column=1, columnspan=2, padx=3, pady=6)

        buttons = tk.Frame(root, bg="#17212b")
        buttons.pack(pady=5, fill="x")
        for col in range(4):
            buttons.grid_columnconfigure(col, weight=1)

        tk.Button(buttons, text="Start Auto", width=12,
                  command=self.start_auto).grid(row=0, column=0, padx=3)
        tk.Button(buttons, text="Pause", width=10,
                  command=self.pause).grid(row=0, column=1, padx=3)
        tk.Button(buttons, text="Reset", width=10,
                  command=self.reset).grid(row=0, column=2, padx=3)

        self.yolo_button = tk.Button(
            buttons, text="Enable YOLO", width=12,
            command=self.enable_yolo
        )
        self.yolo_button.grid(row=0, column=3, padx=3, sticky="ew")

        for key, dx, dy in [
            ("<Up>", 0, -1), ("<Down>", 0, 1),
            ("<Left>", -1, 0), ("<Right>", 1, 0),
            ("w", 0, -1), ("s", 0, 1),
            ("a", -1, 0), ("d", 1, 0)
        ]:
            self.root.bind(key, lambda event, x=dx, y=dy: self.move(x, y))

        self.draw_grid()
        self.draw_objects()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def draw_grid(self):
        self.canvas.delete("grid")
        for x in range(COLS + 1):
            self.canvas.create_line(x * CELL, 0, x * CELL, HEIGHT,
                                    fill="#d5dadd", tags="grid")
        for y in range(ROWS + 1):
            self.canvas.create_line(0, y * CELL, WIDTH, y * CELL,
                                    fill="#d5dadd", tags="grid")
        self.canvas.tag_lower("grid")

    def draw_objects(self):
        self.canvas.delete("objects")
        for x, y in OBSTACLES:
            self.canvas.create_rectangle(
                x * CELL + 3, y * CELL + 3,
                (x + 1) * CELL - 3, (y + 1) * CELL - 3,
                fill="#e74c3c", outline="", tags="objects"
            )

        gx, gy = GOAL
        self.canvas.create_rectangle(
            gx * CELL + 5, gy * CELL + 5,
            (gx + 1) * CELL - 5, (gy + 1) * CELL - 5,
            fill="#f1c40f", outline="#d4a900", tags="objects"
        )
        self.canvas.create_text(
            gx * CELL + CELL / 2, gy * CELL + CELL / 2,
            text="GOAL", font=("Arial", 7, "bold"),
            fill="#333333", tags="objects"
        )

        x, y = self.robot
        self.canvas.create_oval(
            x * CELL + 7, y * CELL + 7,
            (x + 1) * CELL - 7, (y + 1) * CELL - 7,
            fill="#00bcd4", outline="white", width=2, tags="objects"
        )
        self.canvas.create_text(
            x * CELL + CELL / 2, y * CELL + CELL / 2,
            text="R", font=("Arial", 11, "bold"),
            fill="white", tags="objects"
        )
        self.canvas.tag_raise("objects")
        self.position_label.config(text=f"Position: {self.robot} | Steps: {self.steps}")

    def set_status(self, message):
        self.status_label.config(text=message)

    def is_valid(self, position):
        x, y = position
        return 0 <= x < COLS and 0 <= y < ROWS and position not in OBSTACLES

    def move(self, dx, dy):
        if self.auto_running:
            return
        new_position = (self.robot[0] + dx, self.robot[1] + dy)
        if not self.is_valid(new_position):
            self.set_status("BLOCKED - OBSTACLE OR WALL")
            return
        self.robot = new_position
        self.steps += 1
        self.draw_objects()
        if self.robot == GOAL:
            self.set_status("GOAL REACHED!")
            self.pause()
        else:
            self.set_status("MANUAL MOVEMENT")

    def find_path(self):
        queue = deque([(self.robot, [])])
        visited = {self.robot}
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        while queue:
            position, path = queue.popleft()
            if position == GOAL:
                return path
            for dx, dy in directions:
                nxt = (position[0] + dx, position[1] + dy)
                if self.is_valid(nxt) and nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return None

    def start_auto(self):
        if self.robot == GOAL:
            self.set_status("GOAL ALREADY REACHED - RESET FIRST")
            return
        if self.auto_running:
            return
        if not self.find_path():
            self.set_status("NO PATH TO GOAL")
            return
        self.auto_running = True
        self.set_status("AUTO MODE RUNNING")
        self.auto_step()

    def auto_step(self):
        self.after_id = None
        if not self.auto_running:
            return

        # The camera is polled separately; use its latest result here.
        if self.yolo_enabled and self.yolo_detector is not None and self.yolo_obstacle_ahead:
            self.set_status("OBSTACLE DETECTED - ROBOT CONTINUES")
        else:
            self.set_status("AUTO MODE RUNNING")
            
        path = self.find_path()
        if not path:
            self.pause()
            self.set_status("NO SAFE PATH AVAILABLE")
            return

        self.robot = path[0]
        self.steps += 1
        self.draw_objects()

        if self.robot == GOAL:
            self.robot = START
            self.set_status("GOAL REACHED - PATROL RESTARTING")
            self.draw_objects()

        self.set_status("AUTO MODE RUNNING" if not self.yolo_obstacle_ahead else "OBSTACLE DETECTED - YOLO DETECTING")
        self.after_id = self.root.after(400, self.auto_step)

    def pause(self):
        self.auto_running = False
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        self.set_status("PAUSED")

    def reset(self):
        self.pause()
        self.robot = START
        self.steps = 0
        self.draw_grid()
        self.draw_objects()
        self.set_status("RESET - READY")

    def enable_yolo(self):
        if self.yolo_enabled:
            self.disable_yolo()
            return

        if YOLOObstacleDetector is None:
            self.set_status("YOLO IMPORT ERROR - CHECK DETECTOR FILE")
            return

        self.set_status("LOADING YOLO - PLEASE WAIT")
        try:
            self.yolo_detector = YOLOObstacleDetector()
            self.yolo_enabled = True
            self.yolo_obstacle_ahead = False
            self.yolo_button.config(text="Disable YOLO")
            self.set_status("YOLO LIVE DETECTION - CAMERA OPEN")
            self.poll_yolo_camera()
        except Exception as error:
            self.yolo_detector = None
            self.yolo_enabled = False
            self.set_status(f"YOLO ERROR: {error}")

    def poll_yolo_camera(self):
        self.camera_after_id = None
        if not self.yolo_enabled or self.yolo_detector is None:
            return
        try:
            obstacle, frame, status, detected_objects = self.yolo_detector.detect()
            self.yolo_obstacle_ahead = obstacle
            self.yolo_status = status

            if frame is None:
                self.disable_yolo()
                self.set_status(f"YOLO CAMERA ERROR: {status}")
                return

            import cv2
            cv2.imshow("YOLO Live Detection", frame)
            cv2.waitKey(1)

            if self.auto_running and obstacle:
                self.set_status("OBSTACLE DETECTED - YOLO DETECTING")
            elif self.auto_running:
                self.set_status("AUTO MODE RUNNING")
            else:
                self.set_status(status)
        except Exception as error:
            self.disable_yolo()
            self.set_status(f"YOLO ERROR: {error}")
            return

        self.camera_after_id = self.root.after(30, self.poll_yolo_camera)

    def disable_yolo(self):
        self.yolo_enabled = False
        self.yolo_obstacle_ahead = False
        if self.camera_after_id is not None:
            try:
                self.root.after_cancel(self.camera_after_id)
            except tk.TclError:
                pass
            self.camera_after_id = None

        if self.yolo_detector is not None:
            try:
                self.yolo_detector.close()
            except Exception:
                pass
            self.yolo_detector = None

        try:
            import cv2
            cv2.destroyAllWindows()
        except Exception:
            pass

        self.yolo_button.config(text="Enable YOLO")
        self.set_status("YOLO DISABLED")

    def close(self):
        self.pause()
        self.disable_yolo()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotSimulation(root)
    root.mainloop()
