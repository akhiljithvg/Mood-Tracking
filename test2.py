import tkinter as tk
from tkinter import Toplevel, Label, Button
from PIL import Image, ImageTk, ImageSequence
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg


mood_values = {
    'Angry': 0,
    'Sad': 1,
    'Neutral': 2,
    'Happy': 3
}

def add_emoji(ax, emoji_path, position, size=0.1):


    img = mpimg.imread(emoji_path)
    imagebox = OffsetImage(img, zoom=size)
    ab = AnnotationBbox(imagebox, position, frameon=False, pad=0)
    ax.add_artist(ab)

    image = plt.imread(emoji_path)
    ax.imshow(image, aspect='auto', extent=(
        position[0] - size, position[0] + size, position[1] - size, position[1] + size), zorder=10)


# Initialize Firebase
cred = credentials.Certificate('firebase_config/moodtrack-74b92-firebase-adminsdk-l1apr-5958842968.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

ALLOWED_USERS = ["akhil", "kashi", "blacka", "abhinaya", "saksha", "rashmi",  "shreya"]
mood_values = {'😊': 5, '😐': 4, '😢': 2, '😡': 0}

current_user = None

def custom_messagebox(title, message, bg_color):
    msg_box = Toplevel()
    msg_box.title(title)
    msg_box.configure(bg=bg_color)  # Set background color of Toplevel

    # Create a frame to hold the content
    frame = tk.Frame(msg_box, bg=bg_color)
    frame.pack(padx=20, pady=20)

    # Add the message label
    label = Label(frame, text=message, bg=bg_color, fg='white', font=("Helvetica", 12))
    label.pack(pady=20)

    # Add the OK button
    ok_button = Button(frame, text="OK", command=msg_box.destroy, bg=bg_color, fg='white', font=("Helvetica", 12))
    ok_button.pack(pady=10)

    # Center the message box
    msg_box.update_idletasks()
    width = msg_box.winfo_reqwidth()
    height = msg_box.winfo_reqheight()
    screen_width = msg_box.winfo_screenwidth()
    screen_height = msg_box.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    msg_box.geometry(f'{width}x{height}+{x}+{y}')
    
    msg_box.grab_set()
    msg_box.wait_window()

def record_mood(mood):
    global current_user

    if current_user is None:
        custom_messagebox("Login Required", "Hey, Who are you?", "black")
        return

    date_str = datetime.now().strftime('%Y-%m-%d')
    time_str = datetime.now().strftime('%H:%M:%S')

    try:
        mood_entries = db.collection('mood_data')\
                         .where('Username', '==', current_user)\
                         .where('Date', '==', date_str)\
                         .stream()

        if any(mood_entries):
            custom_messagebox("Duplicate Entry", "You have already recorded your mood for today.", "black")
            return

        data = {
            'Username': current_user,
            'Date': date_str,
            'Time': time_str,
            'Mood': mood
        }
        db.collection('mood_data').add(data)

        custom_messagebox("Mood Tracker", "wohooo! bye bye 😍", "black")

    except Exception as e:
        custom_messagebox("Error", f"Failed to record mood: {e}", "black")

    logout()

def calculate_happiness_scale(moods):
    total_points = sum(mood_values[mood] for mood in moods)
    total_count = len(moods)
    happiness_scale = (total_points / total_count) * 2 if total_count != 0 else 0
    return happiness_scale

def get_happiness_scale(username):
    mood_entries = db.collection('mood_data').where('Username', '==', username).stream()
    moods = [entry.to_dict()['Mood'] for entry in mood_entries]
    happiness_scale = calculate_happiness_scale(moods)
    return happiness_scale

def show_happiness_scale(scale):
    meter_window = tk.Toplevel()
    meter_window.title("Happiness Meter")
    meter_window.configure(bg='black')

    # Enable full screen for the meter window
    meter_window.attributes('-fullscreen', True)

    # Allow exiting fullscreen with Escape key
    meter_window.bind('<Escape>', lambda e: meter_window.attributes('-fullscreen', False))

    meter_frame = tk.Frame(meter_window, bg='black')
    meter_frame.pack(pady=20, padx=20)

    tk.Label(meter_frame, text=f"Your happiness scale is {scale:.1f} out of 10.", fg="white", bg="black", font=("Helvetica", 16)).pack(pady=50)

    meter_img_path = 'resources/happymeter.png'  # Adjust the path to the actual image
    try:
        meter_img = Image.open(meter_img_path)
        meter_img = meter_img.resize((400, 200), Image.LANCZOS)
        meter_photo = ImageTk.PhotoImage(meter_img)

        canvas = tk.Canvas(meter_frame, width=400, height=200, bg='black', highlightthickness=0)
        canvas.pack()
        canvas.create_image(0, 0, anchor='nw', image=meter_photo)
        
        # Calculate the position of the pointer
        pointer_x = 20 + scale * 36  # Scale value to fit the meter range
        canvas.create_polygon(pointer_x, 180, pointer_x-10, 200, pointer_x+10, 200, fill='blue')

        # Keep a reference to the image to avoid it being garbage collected
        canvas.image = meter_photo
    except Exception as e:
        tk.Label(meter_frame, text=f"Error loading image: {e}", fg="white", bg="black", font=("Helvetica", 12)).pack(pady=10)

    tk.Button(meter_frame, text="Back", command=meter_window.destroy, bg="black", fg="white").pack(pady=40)


















def show_happy_report():
    def apply_plot_style(ax):
        ax.set_facecolor('black')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_color('none')
        ax.spines['bottom'].set_color('none')
        ax.tick_params(axis='both', which='both', colors='white')

    report_window = tk.Toplevel()
    report_window.title("Happy Report")
    report_window.configure(bg='black')
    report_window.attributes('-fullscreen', True)
    report_window.bind('<Escape>', lambda e: report_window.attributes('-fullscreen', False))

    report_frame = tk.Frame(report_window, bg='black')
    report_frame.pack(side='top', fill='both', expand=True)

    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    day_names = [d.strftime('%A') for d in last_7_days]

    try:
        mood_entries = db.collection('mood_data')\
                         .where('Username', '==', current_user)\
                         .where('Date', 'in', [d.strftime('%Y-%m-%d') for d in last_7_days])\
                         .order_by('Date', direction=firestore.Query.ASCENDING)\
                         .stream()

        mood_by_day = {d.strftime('%A'): 'No data' for d in last_7_days}

        for entry in mood_entries:
            entry_data = entry.to_dict()
            date_str = entry_data['Date']
            mood = entry_data['Mood']
            day_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A')
            mood_by_day[day_name] = mood

        moods = [mood_by_day[day] for day in day_names]
        mood_numeric = [mood_values.get(mood, -1) for mood in moods]

        fig, ax = plt.subplots(figsize=(10, 6))  # Set a figure size to better fit the plot
        fig.patch.set_facecolor('black')
        ax.plot(day_names, mood_numeric, marker='o', linestyle='-', color='red')

        apply_plot_style(ax)

        emoji_paths = {
            0: 'emojis/angry.gif',
            1: 'emojis/sad.gif',
            2: 'emojis/neutral.gif',
            3: 'emojis/happy.gif'
        }

        for i, mood_val in enumerate(mood_numeric):
            if mood_val in emoji_paths:
                emoji_path = emoji_paths[mood_val]
                add_emoji(ax, emoji_path, (i, mood_val), size=0.07)

        ax.set_xticks(range(len(day_names)))
        ax.set_xticklabels(day_names, color='white')
        ax.set_yticks([0, 1, 2, 3])
        ax.set_yticklabels(['Angry', 'Sad', 'Neutral', 'Happy'], color='white')
        ax.set_ylim(-2, 6)

        ax.set_title('Mood Over the Last 7 Days', color='white')
        ax.grid(False)

        # Adjust layout to prevent clipping of labels
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        canvas = FigureCanvasTkAgg(fig, master=report_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    except Exception as e:
        tk.Label(report_frame, text=f"Error loading report: {e}", fg="white", bg="black", font=("Helvetica", 12)).pack()

    button_frame = tk.Frame(report_window, bg='black')
    button_frame.pack(side='bottom', fill='x')
    tk.Button(button_frame, text="Back", command=report_window.destroy, bg="black", fg="white").pack(pady=20)








def login():
    global current_user
    username = username_entry.get().strip()
    if username in ALLOWED_USERS:
        current_user = username
        login_frame.pack_forget()
        happiness_scale = get_happiness_scale(username)
        reset_main_app()
        main_app(happiness_scale)
    else:
        custom_messagebox("Invalid User", "Access denied. Please enter a valid username.", "black")

def logout():
    global current_user
    current_user = None
    username_entry.delete(0, tk.END)  # Clear the username entry field
    main_app_frame.pack_forget()
    login_frame.pack(fill='both', expand=True)

def reset_main_app():
    for widget in main_app_frame.winfo_children():
        widget.destroy()

class AnimatedGIF:
    def __init__(self, master, path, size, mood, **kwargs):
        self.master = master
        self.path = path
        self.size = size
        self.mood = mood
        self.kwargs = kwargs
        self.index = 0 
        self.frames = []

        try:
            print(f"Loading {path}...")
            im = Image.open(path)
            for frame in ImageSequence.Iterator(im):
                frame = frame.resize(size, Image.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(frame))
            print(f"Loaded {len(self.frames)} frames from {path}")
        except Exception as e:
            print(f"Unexpected error loading {path}: {e}")

        if self.frames:
            self.label = tk.Button(master, image=self.frames[0], command=lambda: record_mood(self.mood), bg="black", relief='flat', highlightthickness=0, bd=0)
            self.label.pack(side='left', padx=40)
        else:
            self.label = tk.Label(master, text=f"Error loading {path}", bg="black", fg="white")
            self.label.pack(side='left', padx=40)

        self.animate_id = None
        self.animate()

    def animate(self):
        if self.frames:
            self.index = (self.index + 1) % len(self.frames)
            self.label.configure(image=self.frames[self.index])
            self.animate_id = self.master.after(40, self.animate)

    def stop_animation(self):
        if self.animate_id:
            self.master.after_cancel(self.animate_id)

def main_app(happiness_scale):
    main_app_frame.pack(fill='both', expand=True)
    tk.Label(main_app_frame, text=f"Welcome {current_user} ❤", fg="white", bg="black", font=("Helvetica", 16)).pack(pady=20)
    tk.Label(main_app_frame, text=f"How was your {datetime.now().strftime('%A')}?", fg="white", bg="black", font=("Helvetica", 16)).pack(pady=20)

    emoji_frame = tk.Frame(main_app_frame, bg='black')
    emoji_frame.pack(pady=60)

    emoji_size = (135, 135)
    happy_gif = AnimatedGIF(emoji_frame, "emojis/happy.gif", emoji_size, '😊', bg="black")

    emoji_size = (135, 135)
    neutral_gif = AnimatedGIF(emoji_frame, "emojis/neutral.gif", emoji_size, '😐', bg="black")

    emoji_size = (130, 130)
    sad_gif = AnimatedGIF(emoji_frame, "emojis/sad.gif", emoji_size, '😢', bg="black")

    emoji_size = (120, 120)
    angry_gif = AnimatedGIF(emoji_frame, "emojis/angry.gif", emoji_size, '😡', bg="black")


    button_frame = tk.Frame(main_app_frame, bg="black")
    button_frame.pack(pady=20)


    tk.Button(button_frame, text="Happiness scale", command=lambda: show_happiness_scale(happiness_scale), bg="green", fg="white", font=("Helvetica", 12)).pack(side='left', padx=150)
    tk.Button(button_frame, text="Happiness Graph", command=show_happy_report, bg="blue", fg="white", font=("Helvetica", 12)).pack(side='left', padx=0)
    tk.Button(button_frame, text="Logout", command=logout, bg="red", fg="white", font=("Helvetica", 12)).pack(side='left', padx=150)
root = tk.Tk()
root.title("Office Mood Tracker")
root.configure(bg='black')

# Enable fullscreen mode
root.attributes('-fullscreen', True)

# Allow exiting fullscreen with Escape key
root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

login_frame = tk.Frame(root, bg='black')
login_frame.pack(fill='both', expand=True)

tk.Label(login_frame, text=" ENTER YOUR USERNAME ", fg="white", bg="black", font=("Helvetica", 14)).pack(pady=(60, 10))
username_entry = tk.Entry(login_frame)
username_entry.pack(pady=20)

tk.Button(login_frame, text="Lets Go", command=login, bg="blue", fg="white", font=("Helvetica", 12)).pack(pady=10)

main_app_frame = tk.Frame(root, bg='black')

root.mainloop()
