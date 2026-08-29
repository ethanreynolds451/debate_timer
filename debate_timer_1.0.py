''' 
Debate Timer Version 1.0
- A simple timer for managing UDL debate speeches
- Contains basic functionality for starting, pausing, and resetting the timer, as well as adjusting the timer size and time
- Contains pre-programmed prep time and speeches with displays for protected time and grace periods

Future versions should:
- Clean up and modularize the code
- Fix time slider glitchiness
- Allow custom timer to be set
- Display additional speech information
- Improve GUI layout and design
- Add checkbox options to activate or deactivate information display features

Ideas for additional features:
- Load and save speech configurations from files
- Reproduce sound effects for grace period / timer end
- Dynamically adjust the clock size to fill the screen
- Add graphical timer display, such as a circular countdown timer
'''

import tkinter as tk
from dataclasses import dataclass

@dataclass
class Speech:
    time: str
    grace_period: str
    protected: str
    name: str
    speaker: str
    side: str

class DebateTimer(tk.Tk):
    def __init__(self, speeches):
        super().__init__()
        self.speeches = speeches
        self.current_speech = None

        self.timer_job = None
        self.timer_value = 0
        self.is_grace_time = False

        # Create GUI elements
        self.title("UDL Debate Timer")
        self.geometry("800x550")

        # High level frames
        self.control_frame = tk.Frame(self)
        self.control_spacer = tk.Frame(self, height=50)  # Spacer frame for better layout
        self.timer_display = tk.Label(self, text="00:00", font=("Helvetica", 180))
        self.info_spacer = tk.Frame(self, height=0)  # Spacer frame for better layout
        self.info_frame = tk.Frame(self)

        # Secondary frames
        self.timer_adjuster_frame = tk.Frame(self.control_frame)

        self.timer_size = tk.Scale(self.control_frame, from_=0, to=1000, orient=tk.HORIZONTAL, label="Timer Size", command=self.adjust_timer_size)  
        self.timer_size.set(180)  # Set default timer size

        self.speech_selector = tk.Listbox(self.control_frame, height=7)
        for speech in self.speeches:
            self.speech_selector.insert(tk.END, speech.name)
        self.speech_selector.bind("<<ListboxSelect>>", self.on_speech_select)

        # Timer control 
        self.start_button = tk.Button(self.control_frame, text="Start", command=self.start_timer)
        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause_timer)
        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_timer)

        # Time adjustment controls
        self.adjust_time = tk.Scale(self.timer_adjuster_frame, from_=0, to=60, orient=tk.HORIZONTAL, label="Adjust Time")
        self.adjust_time.bind("<ButtonRelease-1>", self.adjust_timer_time)
        self.adjust_time.bind("<KeyRelease>", self.adjust_timer_time)
        self.add_time_frame = tk.Frame(self.timer_adjuster_frame)
        self.subtract_time_frame = tk.Frame(self.timer_adjuster_frame)
        self.add_10_seconds_button = tk.Button(self.add_time_frame, text="+10s", command=lambda: self.nudge_timer(10))
        self.subtract_10_seconds_button = tk.Button(self.subtract_time_frame, text="-10s", command=lambda: self.nudge_timer(-10))
        self.add_5_seconds_button = tk.Button(self.add_time_frame, text="+5s", command=lambda: self.nudge_timer(5))
        self.subtract_5_seconds_button = tk.Button(self.subtract_time_frame, text="-5s", command=lambda: self.nudge_timer(-5))
        self.add_1_second_button = tk.Button(self.add_time_frame, text="+1s", command=lambda: self.nudge_timer(1))
        self.subtract_1_second_button = tk.Button(self.subtract_time_frame, text="-1s", command=lambda: self.nudge_timer(-1))

        # Display Information
        self.protected_time_label = tk.Label(self.info_frame, text="", font=("Helvetica", 36), fg="green")   # Keep it blank and update if protected
        self.grace_period_label = tk.Label(self.info_frame, text="", font=("Helvetica", 36), fg="red")   # Keep it blank and update if grace period

        # Pack time add and subtract
        self.subtract_10_seconds_button.pack(side=tk.TOP)
        self.subtract_5_seconds_button.pack(side=tk.TOP)
        self.subtract_1_second_button.pack(side=tk.TOP)
        self.add_1_second_button.pack(side=tk.TOP)
        self.add_5_seconds_button.pack(side=tk.TOP)
        self.add_10_seconds_button.pack(side=tk.TOP)

        # Pack time adjustment buttons in their frame
        self.subtract_time_frame.pack(side=tk.LEFT)
        self.adjust_time.pack(side=tk.LEFT)
        self.add_time_frame.pack(side=tk.LEFT)

        # Pack controls in their frame
        self.speech_selector.pack(side=tk.LEFT)
        self.timer_size.pack(side=tk.LEFT)
        self.start_button.pack(side=tk.LEFT)
        self.pause_button.pack(side=tk.LEFT)
        self.reset_button.pack(side=tk.LEFT)
        self.timer_adjuster_frame.pack(side=tk.LEFT)

        # Pack info labels in their frame
        self.protected_time_label.pack(side=tk.LEFT)
        self.grace_period_label.pack(side=tk.LEFT)
        
        # Pack GUI elements
        self.control_frame.pack(side=tk.TOP)
        self.control_spacer.pack(side=tk.TOP)
        self.timer_display.pack(side=tk.TOP)
        self.info_spacer.pack(side=tk.TOP)
        self.info_frame.pack(side=tk.TOP)

    def mainloop(self):
        super().mainloop()

    def on_speech_select(self, event):
        selection = self.speech_selector.curselection()
        if not selection:
            return
        self.select_speech(self.speeches[selection[0]])

    def select_speech(self, speech):
        self.cancel_timer()
        self.current_speech = speech
        # Convert full value to seconds and assign
        self.timer_value = int(speech.time.split(":")[0]) * 60 + int(speech.time.split(":")[1])
        self.timer_display.config(text=f"{self.timer_value // 60:02d}:{self.timer_value % 60:02d}")
        # update the time adjustor start, end, and current value
        self.adjust_time.config(from_=0, to=self.timer_value)
        self.adjust_time.set(self.timer_value)

    def update_timer(self):
        #Decremnt the timer value and update display   
        if(self.timer_value > 0):
            self.timer_value -= 1
            self.timer_display.config(text=f"{self.timer_value // 60:02d}:{self.timer_value % 60:02d}")
            self.adjust_time.set(self.timer_value)

            # Check if the time falls into a protected time range for the current speech and if so update the label
            # Format: "START1:END1,START2:END2,..."
            if(self.current_speech and not self.is_grace_time and self.current_speech.protected and self.current_speech.protected != "0:00" or ""):
                protected_ranges = self.current_speech.protected.split(",")
                in_protected_time = False
                for range in protected_ranges:
                    start, end = range.split("-")
                    start_seconds = int(start.split(":")[0]) * 60 + int(start.split(":")[1])
                    end_seconds = int(end.split(":")[0]) * 60 + int(end.split(":")[1])
                    if(self.timer_value >= start_seconds and self.timer_value <= end_seconds):
                        in_protected_time = True
                        break
                if(in_protected_time):
                    self.protected_time_label.config(text=f"Protected Time")
                else:
                    self.protected_time_label.config(text=f"")
            else:
                self.protected_time_label.config(text=f"")


            # Check grace period flag
            if(self.is_grace_time):
                self.grace_period_label.config(text=f"Grace Period")
                self.protected_time_label.config(text=f"")
            else:
                self.grace_period_label.config(text=f"")

        else:
            # If the timer has elapsed
            self.timer_display.config(text="00:00")
            self.grace_period_label.config(text=f"")
            self.protected_time_label.config(text=f"")

            # Check for grace period and if so start it automatically
            if(not self.is_grace_time):
                if(self.current_speech and self.current_speech.grace_period and self.current_speech.grace_period != "0:00" or ""):
                    grace_time = int(self.current_speech.grace_period.split(":")[0]) * 60 + int(self.current_speech.grace_period.split(":")[1])
                    if(grace_time > 0):
                        self.is_grace_time = True
                        self.grace_period_label.config(text=f"Grace Period")
                        self.timer_value = grace_time
                        self.timer_display.config(text=f"{self.timer_value // 60:02d}:{self.timer_value % 60:02d}")
                        self.adjust_time.config(from_=0, to=self.timer_value)
                        self.adjust_time.set(self.timer_value)
            
        self.timer_job = self.after(1000, self.update_timer)

    def start_timer(self):
        self.cancel_timer()
        self.timer_job = self.after(1000, self.update_timer)

    def pause_timer(self):
        self.cancel_timer()

    def cancel_timer(self):
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    def reset_timer(self):
        selection = self.speech_selector.curselection()
        if not selection:
            return
        self.select_speech(self.speeches[selection[0]])

    def adjust_timer_size(self, value):
        # Change the display size of the timer
        self.timer_display.config(font=("Helvetica", int(value)))

    def adjust_timer_time(self, event):
        self.timer_value = int(self.adjust_time.get())
        self.timer_display.config(text=f"{self.timer_value // 60:02d}:{self.timer_value % 60:02d}")

    def nudge_timer(self, delta_seconds):
        max_value = int(float(self.adjust_time.cget("to")))
        new_value = min(max_value, max(0, self.adjust_time.get() + delta_seconds))
        self.adjust_time.set(new_value)
        self.adjust_timer_time(None)

if __name__ == "__main__":
    speeches = [
        Speech("15:00", "0:00", "", "Prep", "", ""),
        Speech("4:00", "0:30", "0:00-0:30,3:30-4:00", "Government Constructive", "Gov", "Prime Minister"),
        Speech("5:00", "0:30", "0:00-0:30,4:30-5:00", "Opposition Constructive", "Opp", "Leader of Opposition"),
        Speech("5:00", "0:30", "0:00-0:30,4:30-5:00", "Government Refutation", "Gov", "Member of Government"),
        Speech("5:00", "0:30", "0:00-0:30,4:30-5:00", "Opposition Refutation", "Opp", "Member of Opposition"),
        Speech("2:00", "0:30", "0:00-2:00", "Opposition Summary", "Opp", "Leader of Opposition"),
        Speech("3:00", "0:30", "0:00-3:00", "Government Summary", "Gov", "Prime Minister"),
    ]

    app = DebateTimer(speeches)

    app.mainloop()

