#(C) 2019 Anirban Banerjee
#Based on https://github.com/BrendanSimon/micropython_experiments/blob/master/keypad/keypad_timer.py
#GNU GPL version 3

from micropython import const
from pyb import Pin, Timer

class Keypad():
    ## Key states
    KEY_UP      = const (0)
    KEY_DOWN    = const (1)

    def __init__(self, rows, cols, timerFreq):
        ## Initialise all keys to the UP state.
        self.keys = [{'state': self.KEY_UP, 'autort': 9} for key in range(len(rows)*len(cols))]
        #self.keys = [{ 'char': key, 'state': self.KEY_UP, 'autort': 9} for key in keys ]
        self.cols = cols
        ## Initialise row pins as outputs.
        self.row_pins = [ Pin(pin_name, mode=Pin.OUT) for pin_name in rows ]
        ## Initialise column pins as inputs.
        self.col_pins = [ Pin(pin_name, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin_name in self.cols ]
        self.keypadTimer = Timer(5, freq=timerFreq)
        self.scan_row = 0
        self.key_char = None
        self.keypadTimer.callback(self.keypadTimerCallback)
        self.row_pins[self.scan_row].value(1)

    def get_key(self):
        key_char = self.key_char
        self.key_char = None    ## consume last key pressed
        return key_char

    def keypadTimerCallback(self, keypadTimer):
        key_code = self.scan_row * len(self.cols)
        for col in range(len(self.cols)):
            ## Process pin state.
            key_event = None
            if self.col_pins[col].value():
                if self.keys[key_code + col]['state'] == self.KEY_UP:
                    key_event = self.KEY_DOWN
                    self.keys[key_code + col]['state'] = key_event
                else:
                    #already state is KEY_DOWN, increment state value
                    self.keys[key_code + col]['state'] += 1
            else:
                key_event = self.KEY_UP
                self.keys[key_code + col]['autort'] = 9
                self.keys[key_code + col]['state'] = key_event

            ## Process key event
            if key_event == self.KEY_DOWN:
                self.key_char = (key_code + col)
                #self.key_char = self.keys[key_code + col]['char']

            if self.keys[key_code + col]['state'] > self.keys[key_code + col]['autort']:
                #mimic a key release if kept pressed -- set state of the key to 0
                #this will cause key_event to be set to '1' next time
                #the down press is sampled.
                #the key has been kept pressed for the autorepeat threshold duration (10)
                #set autorepeat threshold to a low value to repeat fast
                self.keys[key_code + col]['autort'] = 1
                self.keys[key_code + col]['state'] = self.KEY_UP

        ## Deassert row.
        self.row_pins[self.scan_row].value(0)

        ## Update row.
        self.scan_row += 1
        if self.scan_row >= len(self.row_pins):
            self.scan_row = 0

        ## Assert next row.
        self.row_pins[self.scan_row].value(1)

