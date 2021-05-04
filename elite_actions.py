from ahk import AHK
import time

class EliteActions:
    def __init__(self):
        self.ahk = AHK(executable_path="C:\\Users\\ericd\\Downloads\\AutoHotkey_1.1.33.08\\AutoHotkeyU64.exe")

    def prepare(self):
        win = self.ahk.find_window(title=b'Elite - Dangerous (CLIENT)')
        win.activate()

    def quit_to_menu(self):
        self.prepare()
        self.ahk.key_press('escape')
        time.sleep(1)
        self.ahk.key_press('up')
        time.sleep(1)
        self.ahk.key_press('enter')
        time.sleep(15)
        self.ahk.key_press('enter')
        time.sleep(10)

    def enter_solo_mode(self):
        self.prepare()
        self.ahk.key_press('enter')
        time.sleep(1)
        self.ahk.key_press('right')
        time.sleep(1)
        self.ahk.key_press('right')
        time.sleep(1)
        self.ahk.key_press('enter')
        time.sleep(20)

    def deploy_hardpoints(self):
        self.prepare()
        self.ahk.key_press('u')
        time.sleep(1)

    def launch_fighter(self):
        self.prepare()
        # Open fighter menu
        self.ahk.key_press('3')
        time.sleep(1)

        # Reset selection and hover over fighter
        # self.ahk.key_press('q') # tab left
        # time.sleep(1)
        # self.ahk.key_press('e') # tab right
        # time.sleep(1)
        # self.ahk.key_press('s') # move down
        # time.sleep(1)

        # Select fighter to launch
        self.ahk.key_press('space')
        time.sleep(1)
        self.ahk.key_press('space')
        time.sleep(1)
        self.ahk.key_press('space')
        time.sleep(5)
        self.ahk.key_press('escape')
        time.sleep(1)

        self.set_fighter_engage_at_will()

    def set_fighter_engage_at_will(self):
        self.prepare()
        # Set to engage at will
        self.ahk.key_press('Numpad2')
        time.sleep(1)

    def reload_solo_game(self):
        self.quit_to_menu()
        self.enter_solo_mode()
        self.deploy_hardpoints()
        self.set_fighter_engage_at_will()

ea = EliteActions()
ea.launch_fighter()