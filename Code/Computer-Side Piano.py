# Import modules
from time import time
from os import listdir, path

# Attempt to import pygame
try:
    import pygame
except ModuleNotFoundError as e:
    print("Missing pygame library!")
    raise e
# Attempt to import pySerial
try:
    import serial
    import serial.tools.list_ports
    import serial.tools.list_ports_common
except ModuleNotFoundError as e:
    print("Missing pySerial library!")
    raise e
# Fix DPI scaling issue on Windows
from sys import platform
if platform == "win32":
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except ModuleNotFoundError:
        pass


# Declare functions
def load_icon():
    """Loads the window icon"""
    # Necessary libraries for decoding and decompressing
    from zlib import decompress
    from base64 import b64decode

    # Decode and decompress the icon from a byte string
    compressed_icon = '''eJzt2y9Lg1EYhvFHHAaNVhGsWmYwG/wIFpP7CAYtgghmmyaTVQST4ILRok3FZhMMBvEPiJjmfXgH4hDcdo7nzHOuG66y9Pz
                         C2DvYzBhjbCB3pI7b7SS+JcXeVavdVeJbUgw/fvz48ePHX97w48ePHz9+/OUNP378+PHjx1/e8OPHjx8/fvzlDT9+/Pjx5+
                         0fUmNquOP1XP0zas2q3zfeqherrK571VTr6sPy8ddUQ13Yl/W3WpaHf15dW/fuXPzufb2p3qx3+3/3O/uu9ef+yX8X93zvr
                         ZqfvbPzuOd7bVI9W1j/YVSB37YsrN3ViCrw26mFtd+okagCv51ZOPuTmot7vvfcf1VC2B/VQuTbQ2zavj/T9tOlqsc+POCW
                         1Kv17n5QG2o0/snBN6tOrDu3+16wosaTXPq3m1LLalvtqwO1Z9Xn5KKaSHcaY6zUfQLcm4sg'''
    decoded_icon = b64decode(compressed_icon)
    icon_string = decompress(decoded_icon)

    # Load the image data as a pygame surface and return the result
    return pygame.image.fromstring(icon_string, (64, 64), 'RGBA')


# Print help text
print("""Controls:
Esc   - Toggle fullscreen
Left  - Previous sound font
Right - Next sound font
Up    - Toggle sound font cycling
""")

# Ask for port
#port = input("Enter port for Arduino (ex: COM4): ")


# Initialize pygame
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.mixer.init()
pygame.init()
screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h

# Get the mixer ready and load the notes from file
pygame.mixer.set_num_channels(26)


# Display window setup
win_width = 64*16
win_height = 64*9
win = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
pygame.display.set_caption("Larger Than Life Piano")

# Load window icon
icon = load_icon()
pygame.display.set_icon(icon)


class Key:

    def __init__(self, x, y, z, width, height, color, *note_files):
        self.rect = pygame.Rect(x, y, width, height)
        self.zorder = z
        self.color = color
        self.note_list = [pygame.mixer.Sound(file) for file in note_files]
        self.index = 0
        self.note = pygame.mixer.Sound(note_files[0])
        self.note.set_volume(5.0)
        self.state = False

    def next(self):
        self.index += 1
        self.index %= len(self.note_list)

    def previous(self):
        self.index -= 1
        self.index %= len(self.note_list)

    def press(self):
        if not self.get_state():
            # Stop existing sound
            for note in self.note_list:
                note.stop()
            # Restart sound playing
            self.note_list[self.index].play()
            # self.note.stop()
            # self.note.play()
            self.note_list[self.index].fadeout(3000)
            # self.note.fadeout(3000)
            self.set_state(True)
            return True

        else:
            return None

    def release(self):
        if self.get_state():
            self.set_state(False)
        else:
            return None

    def set_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state

    def get_x2(self):
        return self.rect.x + self.rect.width

    def draw(self, surface):
        if self.state:
            color = (255, 128, 128)
        else:
            color = self.color

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.line(surface, (0, 0, 0), self.rect.topright, self.rect.bottomright)
        pygame.draw.line(surface, (0, 0, 0), self.rect.topleft, self.rect.bottomleft)
        pygame.draw.line(surface, (0, 0, 0), self.rect.topright, self.rect.topleft)
        pygame.draw.line(surface, (0, 0, 0), self.rect.bottomright, self.rect.bottomleft)

    def within(self, x, y):
        return self.rect.collidepoint(x, y)


# Global configuration constants
XPAD = 16
REVERSE = False
CYCLE_TIME = 30

# Obtain all sound sets.  Any directory starting with a '.' will be ignored.  Files must also be ignored.
SOUND_FOLDER = 'Sound Sets'
note_folders = [path.join(SOUND_FOLDER, i) for i in listdir(SOUND_FOLDER) if i[0] != '.' and path.isdir(path.join(SOUND_FOLDER, i))]

# Move 'piano' to front of list
note_folders.insert(0, note_folders.pop(note_folders.index(path.join(SOUND_FOLDER, 'Piano'))))

files = dict([(i, [f'{folder}/note{i}.wav' for folder in note_folders]) for i in range(13, 0, -1)])

# Generate all keys using the corresponding set of notes
key_list = []
key_list.append(Key(XPAD, 20, 0, 16, 60, (255, 255, 255), *files[13]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 1, 8, 30, (0, 0, 0), *files[12]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 0, 16, 60, (255, 255, 255), *files[11]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 1, 8, 30, (0, 0, 0), *files[10]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 0, 16, 60, (255, 255, 255), *files[9]))

key_list.append(Key(key_list[-1].get_x2(), 20, 0, 16, 60, (255, 255, 255), *files[8]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 1, 8, 30, (0, 0, 0), *files[7]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 0, 16, 60, (255, 255, 255), *files[6]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 1, 8, 30, (0, 0, 0), *files[5]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 0, 16, 60, (255, 255, 255), *files[4]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 1, 8, 30, (0, 0, 0), *files[3]))
key_list.append(Key(key_list[-1].get_x2()-4, 20, 0, 16, 60, (255, 255, 255), *files[2]))

key_list.append(Key(key_list[-1].get_x2(), 20, 0, 16, 60, (255, 255, 255), *files[1]))

if REVERSE:
    key_list.reverse()

# Use this to manually set the port
port_name = 'auto'
# port_name = 'COM3'

# Set up internal window, sized for the keys
if REVERSE:
    win2 = pygame.Surface((key_list[0].get_x2()+XPAD, 64+16*2))
else:
    win2 = pygame.Surface((key_list[-1].get_x2()+XPAD, 64+16*2))


# Create font for displaying text
font = pygame.font.Font(pygame.font.get_default_font(), 16)


# Main loop
last_alive = 0
running = True
connected = False
arduino = None
user_pressed_key = None
fullscreen = False
auto_cycle = False
last_cycle = time()
while running:
    # Attempt to connect to Arduino over serial (if not already connected)
    if not connected:
        arduino = None

        if port_name == 'auto':
            # Attempt to automatically select the correct port from the available devices
            for port in list(serial.tools.list_ports.comports()):
                # Skip bluetooth connections--one of them is taking FIVE whole seconds to check
                if 'bluetooth' in port.description.lower():
                    continue

                # Attempt connection to device
                print("Trying:", port.device)
                try:
                    arduino = serial.Serial(port.device, 9600, timeout=0.1)
                except serial.SerialException as err:
                    print(err)
                    pass
                else:
                    # Attempt to verify that this device is the piano using the 'alive' message

                    # Might require a few attempts
                    for i in range(20):
                        try:
                            msg = arduino.readline().decode().splitlines()
                        except serial.SerialException as err:
                            print(err)
                            continue
                        print(msg)
                        if "alive" in msg:
                            connected = True
                            break

                    # Connection attempt failed
                    if connected:
                        break
                    else:
                        arduino.close()
                        arduino = None

        else:
            # Port name has been manually set, use that instead
            try:
                arduino = serial.Serial(port_name, 9600, timeout=0.1)
            except serial.SerialException:
                if arduino is not None:
                    arduino.close()
                arduino = None
            else:
                connected = True

        if arduino is not None:
            last_alive = time()
            print("Connected to", arduino.port)

    # Apply auto-cycle, if enabled
    if auto_cycle:
        if time() - last_cycle > CYCLE_TIME:
            last_cycle = time()
            for key in key_list:
                key.next()

    # Handle events
    for event in pygame.event.get():
        # Program quit event
        if event.type == pygame.QUIT:
            running = False

        # Window resize event
        if event.type == pygame.VIDEORESIZE:
            new_w, new_h = event.w, event.h
            if fullscreen:
                # pass
                win = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
            else:
                win = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)

        # Mouse button pressed - user clicked on keyboard key via program
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get mouse position and convert to internal window coordinates
            mouse_x, mouse_y = pygame.mouse.get_pos()
            x_prime = int(mouse_x * win2.get_width() / win.get_width())
            y_prime = int(mouse_y * win2.get_height() / win.get_height())

            # Find the top-level key the user clicked on, if any
            found_key = None
            topZ = -1
            for i, k in enumerate(key_list):
                if k.within(x_prime, y_prime) and (k.zorder > topZ):
                    topZ = k.zorder
                    found_key = i

            user_pressed_key = found_key

            # Play note, if applicable
            if found_key is not None:
                key_list[found_key].press()

        # Mouse button released - user released key
        if event.type == pygame.MOUSEBUTTONUP:
            if user_pressed_key is not None:
                key_list[user_pressed_key].release()
            user_pressed_key = None

        # Keyboard key pressed
        if event.type == pygame.KEYDOWN:
            # Escape key - toggle fullscreen
            if event.key == pygame.K_ESCAPE:
                if fullscreen:
                    # Disable fullscreen
                    win = pygame.display.set_mode((win_width, win_height), pygame.RESIZABLE)
                    fullscreen = False
                else:
                    # Enable fullscreen
                    win = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.RESIZABLE)
                    fullscreen = True

            # Right arrow - switch to next note set
            elif event.key == pygame.K_RIGHT:
                for key in key_list:
                    key.next()

            # Left arrow - switch to previous note set
            elif event.key == pygame.K_LEFT:
                for key in key_list:
                    key.previous()

            # Up arrow - toggle auto-cycle
            elif event.key == pygame.K_UP:
                last_cycle = time()
                auto_cycle = not auto_cycle

    # Handle serial (if connected)
    if connected:
        # Read in all messages
        try:
            msg = arduino.readline().decode()
        except serial.SerialException:
            # Exception indicates the connection was lost
            connected = False
            print("Lost connection")
        else:
            # Parse and handle all received messages (each message separated by line break)
            for sub_msg in msg.splitlines():
                if sub_msg != '':
                    if 'alive' not in sub_msg:
                        print("Received:", sub_msg)
                    result = sub_msg.split("|")
                    # Received 'alive' status
                    if result[0] == "alive":
                        last_alive = time()

                    # Received a change in key state
                    elif result[0] == "keyDown":
                        pressed_key = int(result[1])
                        key_list[pressed_key].press()

                    elif result[0] == "keyUp":
                        pressed_key = int(result[1])
                        try:
                            key_list[pressed_key].release()
                        except IndexError:
                            print(f"(Unknown key index: {pressed_key})")

    # Assume connection has been lost if there's no response after ten seconds
    if time() - last_alive > 10.0:
        connected = False

    # Update screen
    # First pass: layer 0 keys
    for key in key_list:
        if key.zorder == 0:
            key.draw(win2)

    # Second pass: layer 1 keys
    for key in key_list:
        if key.zorder == 1:
            key.draw(win2)

    # Draw internal rectangle to display and blit
    pygame.transform.scale(win2, (win.get_width(), win.get_height()), win)

    # Add Arduino connection indicator
    pygame.draw.rect(win,
                     (0, 255, 0) if connected else (255, 0, 0),
                     (0, 0, 32, 32))

    # Add indicator for current sound set
    text = font.render(note_folders[key_list[0].index], True, (255, 255, 255), (0, 0, 0))
    win.blit(text, (8, win.get_height()-text.get_height()-8))

    # Add auto-cycle indicator
    if auto_cycle and int(time()*2) % 2:
        pygame.draw.polygon(win, (0, 128, 255),
                            ((32, 12),
                             (32, 20),
                             (48, 20),
                             (48, 32),
                             (64, 16),
                             (48, 0),
                             (48, 12),
                             (32, 12)))

    # Update screen
    pygame.display.flip()

# Close pygame
pygame.quit()
