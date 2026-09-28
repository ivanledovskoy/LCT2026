import machine
import time

if False:
    pin_a = machine.Pin(2, machine.Pin.OUT)
    pin_b = machine.Pin(4, machine.Pin.OUT)
    pin_click = machine.Pin(3, machine.Pin.OUT)
else:
    pin_a = machine.Pin(2, machine.Pin.OPEN_DRAIN)
    pin_b = machine.Pin(4, machine.Pin.OPEN_DRAIN)
    pin_click = machine.Pin(3, machine.Pin.OPEN_DRAIN)
    pin_reset = machine.Pin(0, machine.Pin.OPEN_DRAIN)


def rsleep():
    time.sleep_us(100_000)

def setup_ab(a, b):
    pin_a.value(a)
    pin_b.value(b)
    rsleep()

def reset():
    setup_ab(0, 0)
    pin_reset.value(0)
    time.sleep_us(100)
    pin_reset.value(1)
    time.sleep_us(100_000)

CLICK_SLEEP_MS=100
def click(duration_ms=CLICK_SLEEP_MS, do_last_sleep=True):
    pin_click.value(0)  # DOWN
    time.sleep_ms(duration_ms)
    pin_click.value(1) # UP
    if do_last_sleep:
        time.sleep_ms(CLICK_SLEEP_MS)

def set_number(n):
    a, b = pin_a.value(), pin_b.value()
    if n <= 5:
        for _ in range(n):
            if (a, b) == (0, 0):
                a, b = (1, 0)
                setup_ab(a, b)
            elif (a, b) == (1, 0):
                a, b = (1, 1)
                setup_ab(a, b)
            elif (a, b) == (0, 1):
                a, b = (0, 0)
                setup_ab(a, b)
            elif (a, b) == (1, 1):
                a, b = (0, 1)
                setup_ab(a, b)
    else:
        for _ in range(10-n):
            if (a, b) == (0, 0):
                a, b = (0, 1)
                setup_ab(a, b)
            elif (a, b) == (1, 0):
                a, b = (0, 0)
                setup_ab(a, b)
            elif (a, b) == (0, 1):
                a, b = (1, 1)
                setup_ab(a, b)
            elif (a, b) == (1, 1):
                a, b = (1, 0)
                setup_ab(a, b)


import rp2

# Does not work, but signal detect is OK :DDDD
@rp2.asm_pio(
    autopush=True,
    push_thresh=24,                 
    in_shiftdir=rp2.PIO.SHIFT_LEFT 
)
def ws2812_capture():
    wrap_target()
    wait(1, pin, 0)
    nop() [3]
    in_(pins, 1)
    wait(0, pin, 0)
    wrap()

rx_pin = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_DOWN)

sm = rp2.StateMachine(0, ws2812_capture, freq=12_000_000, in_base=rx_pin)
sm.active(0)

reset()

N = [0,0,0,0]

for i in range(4):
    BEST = (-1, -1)
    for n in range(10):
        N[i] = n

        reset()
        for j in range(3):
            set_number(N[j])
            click()
        
        set_number(N[3])
        sm.active(1)
        click(do_last_sleep=False)
        t0 = time.ticks_us()
        
        while True:
            if sm.rx_fifo():
                t = time.ticks_us() - t0
                while sm.rx_fifo():
                    raw_word = sm.get()
                
                print(f"GPIO16: {raw_word:06x}")
                break
        
        sm.active(0)
        sm.restart()
        while sm.rx_fifo():
            sm.get()

        print(f"timeof({N}) = {t}")
        if BEST[1] < t:
            BEST = (n, t)
    
    N[i] = BEST[0]
    print(f"KEY START IS {N[:i+1]}")

print(f"THE KEY IS : {N}")

