from tkinter import *
from tkinter import ttk
from datetime import datetime
from pynput import keyboard
import configparser
import os
import sys
import threading
import pystray
from PIL import Image

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)

    CONFIG_DIR = os.path.join(
        os.environ["APPDATA"],
        "Set Aside Some Time"
    )

    CONFIG_FILE = os.path.join(
        CONFIG_DIR,
        "config.ini"
    )

    LOGO_FILE = os.path.join(
        BASE_DIR,
        "logo.png"
    )

else:
    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    CONFIG_DIR = BASE_DIR

    CONFIG_FILE = os.path.join(
        BASE_DIR,
        "config.ini"
    )

    LOGO_FILE = os.path.join(
        BASE_DIR,
        "logo.png"
    )

os.makedirs(
    CONFIG_DIR,
    exist_ok=True
)

config = configparser.ConfigParser()

config.read(
    CONFIG_FILE
)

if "Settings" not in config:
    raise FileNotFoundError(
        f"Could not read config file:\n{CONFIG_FILE}"
    )

show_seconds = config["Settings"].getboolean(
    "show_seconds"
)

Enable_Disable_Key = int(
    config["Settings"]["enable_disable_key"],
    0
)

extra_key = config["Settings"][
    "enable_disable_key_extra_key"
]

if extra_key == "Shift":
    extra_key = keyboard.Key.shift_l
elif extra_key == "Ctrl":
    extra_key = keyboard.Key.ctrl_l
elif extra_key == "Alt":
    extra_key = keyboard.Key.alt_l
elif extra_key == "None":
    extra_key = None

current_time = ""
showing = False
after_id = None
running = False
Key_Was_Used = False

settings_window = None

extra_key_box = None
key = None
Font = None
show_seconds_var = None
mode = None

root = Tk()
root.overrideredirect(True)

window_width = 200
window_height = 200

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

position = config["Settings"]["position"].strip()

if position == "Top Left":
    x = 0
    y = 0

elif position == "Top Right":
    x = screen_width - window_width
    y = 0

elif position == "Bottom Left":
    x = 0
    y = screen_height - window_height

elif position == "Bottom Right":
    x = screen_width - window_width
    y = screen_height - window_height

else:
    x = screen_width - window_width
    y = screen_height - window_height

root.geometry(
    f"{window_width}x{window_height}+{x}+{y}"
)

root.title(
    "Set Aside Some Time"
)

logo = PhotoImage(
    file=LOGO_FILE
)

root.iconphoto(
    False,
    logo
)

TRANSPARENT_COLOR = "#123456"

root.attributes(
    "-transparentcolor",
    TRANSPARENT_COLOR
)

root.configure(
    bg=TRANSPARENT_COLOR
)

root.attributes(
    "-topmost",
    True
)

canvas = Canvas(
    root,
    width=window_width,
    height=window_height,
    bg=TRANSPARENT_COLOR,
    highlightthickness=0,
    borderwidth=0
)

canvas.pack()


def update_position():
    global position

    if position == "Top Left":
        x = -105
        y = -175

    elif position == "Top Right":
        x = screen_width - window_width
        y = -175

    elif position == "Bottom Left":
        x = -105
        y = screen_height - window_height

    elif position == "Bottom Right":
        x = screen_width - window_width
        y = screen_height - window_height

    else:
        x = screen_width - window_width
        y = screen_height - window_height

    root.geometry(
        f"{window_width}x{window_height}+{x}+{y}"
    )


def update_time():
    global after_id
    global current_time

    if not running:
        return

    if show_seconds:
        current_time = datetime.now().strftime(
            "%I:%M:%S %p"
        )
    else:
        current_time = datetime.now().strftime(
            "%I:%M %p"
        )

    canvas.itemconfig(
        text,
        text=current_time
    )

    canvas.itemconfig(
        text,
        font=(
            config["Settings"]["font"],
            12
        )
    )

    after_id = root.after(
        1000,
        update_time
    )


def top():
    root.attributes(
        "-topmost",
        False
    )

    root.attributes(
        "-topmost",
        True
    )


text = canvas.create_text(
    window_width,
    window_height,
    text=current_time,
    fill="#CCCCCC",
    font=(
        config["Settings"]["font"],
        12
    ),
    anchor="se"
)

canvas.itemconfig(
    text,
    state="hidden"
)


def sh():
    global showing

    if showing:
        showing = False

        canvas.itemconfig(
            text,
            state="hidden"
        )

        stop_clock()

    else:
        showing = True

        canvas.itemconfig(
            text,
            state="normal"
        )

        root.attributes(
            "-topmost",
            False
        )

        root.attributes(
            "-topmost",
            True
        )

        start_clock()


pressed_keys = set()


def on_press(key_pressed):
    global Key_Was_Used

    try:
        pressed_keys.add(
            key_pressed
        )

        if isinstance(
            key_pressed,
            keyboard.KeyCode
        ):
            if key_pressed.vk == Enable_Disable_Key:
                if (
                    extra_key is None
                    or extra_key in pressed_keys
                ):
                    root.after(
                        0,
                        sh
                    )

                    Key_Was_Used = not Key_Was_Used

    except:
        pass


def on_release(key_pressed):
    try:
        pressed_keys.discard(
            key_pressed
        )
    except:
        pass


listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

listener.start()


def stop_clock():
    global running
    global after_id

    running = False

    if after_id is not None:
        try:
            root.after_cancel(
                after_id
            )
        except:
            pass

        after_id = None


def start_clock():
    global running

    if running:
        return

    running = True

    update_time()


def save_settings():
    if (
        extra_key_box is None
        or key is None
        or Font is None
        or show_seconds_var is None
        or mode is None
    ):
        return

    config["Settings"]["position"] = mode.get()

    config["Settings"]["font"] = Font.get()

    config["Settings"]["show_seconds"] = str(
        show_seconds_var.get()
    )

    config["Settings"]["enable_disable_key"] = key.get()

    config["Settings"][
        "enable_disable_key_extra_key"
    ] = extra_key_box.get()

    with open(
        CONFIG_FILE,
        "w"
    ) as configfile:
        config.write(configfile)


def settings_changed(*args):
    global show_seconds
    global Enable_Disable_Key
    global extra_key
    global position

    if (
        extra_key_box is None
        or key is None
        or Font is None
        or show_seconds_var is None
        or mode is None
    ):
        return

    show_seconds = show_seconds_var.get()

    try:
        Enable_Disable_Key = int(
            key.get(),
            0
        )
    except:
        pass

    extra_key_name = extra_key_box.get()

    if extra_key_name == "Shift":
        extra_key = keyboard.Key.shift_l

    elif extra_key_name == "Ctrl":
        extra_key = keyboard.Key.ctrl_l

    elif extra_key_name == "Alt":
        extra_key = keyboard.Key.alt_l

    else:
        extra_key = None

    position = mode.get()

    canvas.itemconfig(
        text,
        font=(
            Font.get(),
            12
        )
    )

    update_position()

    save_settings()

    if running:
        if after_id is not None:
            try:
                root.after_cancel(
                    after_id
                )
            except:
                pass

        update_time()


def close_settings():
    global settings_window

    if settings_window is None:
        return

    window = settings_window
    settings_window = None

    try:
        config["Settings"]["ran_once"] = "True"

        with open(
            CONFIG_FILE,
            "w"
        ) as configfile:
            config.write(configfile)

    except:
        pass

    try:
        window.destroy()
    except:
        pass

    if not showing:
        sh()

def create_settings_window():
    global settings_window
    global extra_key_box
    global key
    global Font
    global show_seconds_var
    global mode

    if (
        settings_window is not None
        and settings_window.winfo_exists()
    ):
        settings_window.deiconify()
        settings_window.lift()
        settings_window.focus_force()
        return

    settings_window = Toplevel(
        root
    )

    settings_window.title(
        "Settings | Set Aside Some Time"
    )

    settings_window.geometry(
        "520x330"
    )

    settings_window.resizable(
        False,
        False
    )

    settings_window.attributes(
        "-alpha",
        0.9
    )

    settings_window.iconphoto(
        False,
        logo
    )

    style = ttk.Style()
    style.theme_use(
        "clam"
    )

    main = ttk.Frame(
        settings_window,
        padding=20
    )

    main.pack(
        fill="both",
        expand=True
    )

    title = ttk.Label(
        main,
        text="Settings",
        font=(
            "Segoe UI",
            18,
            "bold"
        )
    )

    title.grid(
        row=0,
        column=0,
        columnspan=3,
        sticky="w",
        pady=(0, 20)
    )

    ttk.Label(
        main,
        text="Shortcut Key"
    ).grid(
        row=1,
        column=0,
        sticky="w"
    )

    extra_key_box = ttk.Combobox(
        main,
        values=[
            "None",
            "Shift",
            "Ctrl",
            "Alt"
        ],
        state="readonly",
        width=8
    )

    extra_key_box.set(
        config["Settings"][
            "enable_disable_key_extra_key"
        ]
    )

    extra_key_box.grid(
        row=1,
        column=1,
        sticky="w"
    )

    key = ttk.Entry(
        main,
        width=10
    )

    key.insert(
        0,
        config["Settings"][
            "enable_disable_key"
        ]
    )

    key.grid(
        row=1,
        column=2,
        sticky="w",
        padx=(2, 0)
    )

    ttk.Label(
        main,
        text="Shortcut used to enable and disable the time. (Use Virtual-Key Codes)",
        foreground="gray"
    ).grid(
        row=2,
        column=0,
        columnspan=3,
        sticky="w",
        pady=(0, 10)
    )

    ttk.Label(
        main,
        text="Font"
    ).grid(
        row=3,
        column=0,
        sticky="w"
    )

    Font = ttk.Entry(
        main,
        width=20
    )

    Font.insert(
        0,
        config["Settings"]["font"]
    )

    Font.grid(
        row=3,
        column=1,
        sticky="w"
    )

    ttk.Label(
        main,
        text="To change the timer font.",
        foreground="gray"
    ).grid(
        row=4,
        column=0,
        columnspan=3,
        sticky="w",
        pady=(0, 10)
    )

    show_seconds_var = BooleanVar(
        value=config["Settings"].getboolean(
            "show_seconds"
        )
    )

    ttk.Checkbutton(
        main,
        text="Show Seconds",
        variable=show_seconds_var
    ).grid(
        row=6,
        column=0,
        sticky="w"
    )

    ttk.Label(
        main,
        text="Enable or disable seconds.",
        foreground="gray"
    ).grid(
        row=6,
        column=1,
        sticky="w"
    )

    ttk.Label(
        main,
        text="Position"
    ).grid(
        row=7,
        column=0,
        sticky="w",
        pady=(10, 0)
    )

    mode = ttk.Combobox(
        main,
        values=[
            "Top Left",
            "Top Right",
            "Bottom Left",
            "Bottom Right"
        ],
        state="readonly",
        width=17
    )

    mode.set(
        config["Settings"]["position"]
    )

    mode.grid(
        row=7,
        column=1,
        sticky="w",
        pady=(10, 0)
    )

    ttk.Label(
        main,
        text="Choose where the time comes.",
        foreground="gray"
    ).grid(
        row=8,
        column=0,
        columnspan=3,
        sticky="w"
    )

    extra_key_box.bind(
        "<<ComboboxSelected>>",
        settings_changed
    )

    key.bind(
        "<KeyRelease>",
        settings_changed
    )

    Font.bind(
        "<KeyRelease>",
        settings_changed
    )

    show_seconds_var.trace_add(
        "write",
        settings_changed
    )

    mode.bind(
        "<<ComboboxSelected>>",
        settings_changed
    )

    settings_window.protocol(
        "WM_DELETE_WINDOW",
        close_settings
    )

    settings_window.lift()
    settings_window.focus_force()


def open_settings(icon, item):
    root.after(
        0,
        create_settings_window
    )


def exit_app(icon, item):
    listener.stop()

    try:
        icon.stop()
    except:
        pass

    root.after(
        0,
        root.destroy
    )


def create_tray_icon():
    image = Image.open(
        LOGO_FILE
    ).convert("RGBA")

    menu = pystray.Menu(
        pystray.MenuItem(
            "Settings",
            open_settings
        ),
        pystray.MenuItem(
            "Exit",
            exit_app
        )
    )

    icon = pystray.Icon(
        "Set Aside Some Time",
        image,
        "Set Aside Some Time",
        menu
    )

    icon.run()


update_position()

if config["Settings"].getboolean(
    "ran_once"
):
    showing = True

    canvas.itemconfig(
        text,
        state="normal"
    )

    start_clock()

else:
    showing = False

    canvas.itemconfig(
        text,
        state="hidden"
    )

    create_settings_window()


tray_thread = threading.Thread(
    target=create_tray_icon,
    daemon=True
)

tray_thread.start()

root.mainloop()