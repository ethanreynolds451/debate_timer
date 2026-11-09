''' 
Debate Timer Version 1.0
- A simple timer for managing UDL debate speeches
- Contains basic functionality for starting, pausing, and resetting the timer, as well as adjusting the timer size and time
- Contains pre-programmed prep time and speeches with displays for protected time and grace periods

Future versions should:
- DONE Clean up and modularize the code
- DONE Fix time slider glitchiness
- Allow custom timer to be set
- Display additional speech information
- Improve GUI layout and design
- Add checkbox options to activate or deactivate information display features
- Add entry box for custom time
- Add impromptu mode

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
        self.speeches = speeches        # A struct with all the speeches and their associated information passed into the constructor 
        self.current_speech = None      # Variable to store speech being currently timed
                                        # A value of None will put the timer in custom mode for user to set their own time

        self.timer_job = None 
        self.timer_value = 0            # Initialize the time to 0 seconds

        self.is_protected_time = False  # Flag to indicate if the timer is currently in a protected time range
        self.is_grace_time = False      # Flag to indicate if the timer is currently in a grace period

        self.initialize_gui()           # Call the function to initialize the GUI

    # This only gets called once at application launch or when a new instance of the timer class is created
    def initialize_gui(self):
        # Create GUI elements
        self.title("UDL Debate Timer")
        self.geometry("800x550")

        # High level frames
        self.control_frame = tk.Frame(self)                                             # Frame for all timer control elements
        self.control_spacer = tk.Frame(self, height=50)                                 # Spacer frame for better layout
        self.timer_display = tk.Label(self, text="00:00", font=("Helvetica", 180))      # Frame for timer display (as label)
        self.info_spacer = tk.Frame(self, height=0)                                     # Spacer frame for better layout
        self.info_frame = tk.Frame(self)                                                # Frame for all informational elements

        # Secondary frames
        self.timer_layout_frame = tk.Frame(self.control_frame)                          # Frame for timer layout controls (eg. size)
        self.speech_selector_frame = tk.Frame(self.control_frame)                       # Frame for speech selection listbox
        self.timer_control_frame = tk.Frame(self.control_frame)                         # Frame for timer control buttons
        self.timer_adjuster_frame = tk.Frame(self.control_frame)                        # Frame for time adjustment controls

        # Timer layout elements (timer_layout_frame)
        self.timer_size = tk.Scale(self.timer_layout_frame, from_=0, to=1000, orient=tk.HORIZONTAL, label="Timer Size", command=self.adjust_timer_size)  
        self.timer_size.set(180)  # Set default timer size
        self.info_size = tk.Scale(self.timer_layout_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Label Size", command=self.adjust_info_size)
        self.info_size.set(36)  # Set default label size

        # Speech selection listbox (speech_selector_frame)
        self.speech_selector = tk.Listbox(self.speech_selector_frame, height=7)
        for speech in self.speeches:
            self.speech_selector.insert(tk.END, speech.name)
        self.speech_selector.bind("<<ListboxSelect>>", self.on_speech_select)

        # Timer control (timer_control_frame)
        self.control_pannel_frame = tk.Frame(self.timer_control_frame)
        self.start_button = tk.Button(self.control_pannel_frame, text="Start", command=self.start_timer_button_callback)
        self.pause_button = tk.Button(self.control_pannel_frame, text="Pause", command=self.pause_timer_button_callback)
        self.reset_button = tk.Button(self.control_pannel_frame, text="Reset", command=self.reset_timer_button_callback)
        self.time_entry_box_label = tk.Label(self.timer_control_frame, text="Custom Time (MM:SS)")
        self.time_entry_box = tk.Entry(self.timer_control_frame)
        self.time_entry_box.bind("<Return>", self.on_time_entry)  # Bind the Return key to the on_time_entry function

        # Time adjustment controls (timer_adjuster_frame)
        self.adjust_time_slider_frame = tk.Frame(self.timer_adjuster_frame)
        self.adjust_time = tk.Scale(self.adjust_time_slider_frame, from_=0, to=60, orient=tk.HORIZONTAL, showvalue=0)
        self.adjust_time_value_label = tk.Label(self.adjust_time_slider_frame, text="00:00")
        self.adjust_time.config(command=self.on_adjust_time_scale_change)
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

        # Display Information (info_frame)
        self.protected_time_label = tk.Label(self.info_frame, text="", font=("Helvetica", 36), fg="green")   # Keep it blank and update if protected
        self.grace_period_label = tk.Label(self.info_frame, text="", font=("Helvetica", 36), fg="red")   # Keep it blank and update if grace period

        # Pack time add and subtract (add_time_frame and subtract_time_frame) buttons in their respective frames
        self.subtract_10_seconds_button.pack(side=tk.TOP)
        self.subtract_5_seconds_button.pack(side=tk.TOP)
        self.subtract_1_second_button.pack(side=tk.TOP)
        self.add_1_second_button.pack(side=tk.TOP)
        self.add_5_seconds_button.pack(side=tk.TOP)
        self.add_10_seconds_button.pack(side=tk.TOP)

        # Pack time adjustment buttons in their frame (timer_adjuster_frame)
        self.adjust_time_value_label.pack(side=tk.TOP)
        self.adjust_time.pack(side=tk.TOP)
        self.subtract_time_frame.pack(side=tk.LEFT)
        self.adjust_time_slider_frame.pack(side=tk.LEFT)
        self.add_time_frame.pack(side=tk.LEFT)

        # Pack timer controls in their frame (timer_control_frame)
        self.speech_selector.pack(side=tk.LEFT)
        self.timer_size.pack(side=tk.TOP)
        self.info_size.pack(side=tk.BOTTOM)
        self.start_button.pack(side=tk.LEFT)
        self.pause_button.pack(side=tk.LEFT)
        self.reset_button.pack(side=tk.LEFT)
        self.control_pannel_frame.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.time_entry_box_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.time_entry_box.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.timer_adjuster_frame.pack(side=tk.LEFT)

        # Pack info labels in their frame (info_frame)
        self.protected_time_label.pack(side=tk.LEFT)
        self.grace_period_label.pack(side=tk.LEFT)

        # Pack second level frames
        self.speech_selector_frame.pack(side=tk.LEFT)
        self.timer_layout_frame.pack(side=tk.LEFT)
        self.timer_control_frame.pack(side=tk.RIGHT)
        self.timer_adjuster_frame.pack(side=tk.RIGHT)

        # Pack top level frames
        self.control_frame.pack(side=tk.TOP)
        self.control_spacer.pack(side=tk.TOP)
        self.timer_display.pack(side=tk.TOP)
        self.info_spacer.pack(side=tk.TOP)
        self.info_frame.pack(side=tk.TOP)

    # Run the tkinter mainloop to start the application
    def mainloop(self):
        super().mainloop()

    ##############################
    ### GUI Callback Functions ###
    ##############################

    # Event handler for speech selection from the listbox
    def on_speech_select(self, event):
        selection = self.speech_selector.curselection()
        if not selection:
            return
        self.select_speech(self.speeches[selection[0]])

    # Event handler for custom time entry in the entry box
    def on_time_entry(self, event):
        # Get the time from the entry box and validate it
        time = self.get_custom_time()
        if not time:
            return
        # If it is a valid time, convert it to seconds and set the timer value
        self.reset_timer()  # Reset the timer to clear any previous state
        self.current_speech = None  # Set current speech to None to indicate custom time mode
        self.timer_value = time
        self.timer_display.config(text=self.format_seconds(self.timer_value))

    # Callback for start button
    def start_timer_button_callback(self):
        self.cancel_timer_job()                                 # Cancel any residual jobs to avoid multi counting
        self.timer_job = self.after(1000, self.update_timer)    # Create a new job to update the timer every second

    # Callback for pause button
    def pause_timer_button_callback(self):
        self.cancel_timer_job()                                 # Stop the current countdown but retain the state variables

    # Callback for reset button
    def reset_timer_button_callback(self):
        self.reset_timer()                                      # Stop the timer, reset trackers, and rest the timer GUI
        if not self.current_speech:                                  # If no speech is selected, do not reset the timer to a speech default time
            # If no speech is selected, assume custom time mode and attempt to get the time from the entry box
            time = self.get_custom_time()
            if time is not None:
                # Only update the timer value if the custom time is valid
                self.timer_value = time
                self.timer_display.config(text=self.format_seconds(self.timer_value))
            return
        selection = self.speech_selector.curselection()         # Get the current speech selection and reselect it to reset the timer to the actual speech default time
        if not selection:
            return
        self.select_speech(self.speeches[selection[0]])

    # Callback for timer size adjustment slider
    def adjust_timer_size(self, value):
        # Change the display size of the timer
        self.timer_display.config(font=("Helvetica", int(value)))

    # Callback for slider drag; Scale only supports numeric value display natively,
    # so we mirror the value in a separate MM:SS label.
    def on_adjust_time_scale_change(self, value):
        self.update_adjust_time_label(int(float(value)))

    # Callback for label size adjustment slider
    def adjust_info_size(self, value):
        # Change the display size of the protected time and grace period labels
        self.protected_time_label.config(font=("Helvetica", int(value)))
        self.grace_period_label.config(font=("Helvetica", int(value)))
        # Hide the labels if the size is set to 0 (easier than putting a hide / show button)
        if value=="0":
            self.protected_time_label.pack_forget()
            self.grace_period_label.pack_forget()
        else:
            self.protected_time_label.pack(side=tk.LEFT)
            self.grace_period_label.pack(side=tk.LEFT)

    # Event handler for time adjustment slider
    def adjust_timer_time(self, event):
        self.timer_value = int(self.adjust_time.get())
        self.timer_display.config(text=self.format_seconds(self.timer_value))
        self.update_adjust_time_label(self.timer_value)

    # Callback for all time increment and decrement buttons
    def nudge_timer(self, delta_seconds):
        max_value = int(float(self.adjust_time.cget("to")))
        new_value = min(max_value, max(0, self.adjust_time.get() + delta_seconds))
        self.adjust_time.set(new_value)
        self.adjust_timer_time(None)

    def format_seconds(self, total_seconds):
        return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"

    def update_adjust_time_label(self, seconds):
        self.adjust_time_value_label.config(text=self.format_seconds(seconds))



    #################################
    ### Internal State Management ###
    #################################

    # Function to select a speech and set the timer accordingly
    def select_speech(self, speech):
        self.cancel_timer_job()
        self.current_speech = speech
        self.is_protected_time = False      # Reset only the protected / grace time flags but keep the timer value
        self.is_grace_time = False
        # Convert full value to seconds and assign
        self.timer_value = int(speech.time.split(":")[0]) * 60 + int(speech.time.split(":")[1])
        self.timer_display.config(text=self.format_seconds(self.timer_value))
        # update the time adjustor start, end, and current value
        self.adjust_time.config(from_=0, to=self.timer_value)
        self.adjust_time.set(self.timer_value)
        self.update_adjust_time_label(self.timer_value)
        self.protected_time_label.config(text="")
        self.grace_period_label.config(text="")

    # Function to extract and validate time from the entry box
    def get_custom_time(self): 
        time_str = self.time_entry_box.get()
        try: 
            minutes = int(time_str.split(":")[0])
            seconds = int(time_str.split(":")[1])
            if minutes < 0 or seconds < 0 or seconds >= 60:
                raise ValueError("Invalid time format")
        except (ValueError, IndexError):
            self.time_entry_box.delete(0, tk.END)
            return None
        time = minutes * 60 + seconds
        return time

    # Function to update the timer value and display every second
    def update_timer(self):
        #Decremnt the timer value and update display   
        if(self.timer_value > 0):
            self.timer_value -= 1
            self.timer_display.config(text=self.format_seconds(self.timer_value))
            self.adjust_time.set(self.timer_value)
            self.update_adjust_time_label(self.timer_value)

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
                        self.timer_display.config(text=self.format_seconds(self.timer_value))
                        self.adjust_time.config(from_=0, to=self.timer_value)
                        self.adjust_time.set(self.timer_value)
                        self.update_adjust_time_label(self.timer_value)
            
        self.timer_job = self.after(1000, self.update_timer)

    # Stop the timer from coutning down by canceling the scheduled update job
    def cancel_timer_job(self):
        # Check that the timer is running before trying to cancel it
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    # Reset the timer to its initial state, stopping any countdown and clearing flags
    def reset_timer(self):
        self.cancel_timer_job()         # Stop the timer from counting down
        self.is_protected_time = False
        self.is_grace_time = False
        self.timer_value = 0
        self.reset_timer_gui()   # Reset the GUI elements to their default state

    # Reset only the GUI elements without affecting the timer state or flags
    def reset_timer_gui(self):
        self.timer_display.config(text="00:00")
        self.update_adjust_time_label(0)
        self.protected_time_label.config(text=f"")
        self.grace_period_label.config(text=f"")

#####################
### Main Function ###
#####################

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

