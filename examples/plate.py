
from pyxdaq.xdaq import get_XDAQ, XDAQ
from pyxdaq.stim import enable_stim
from pyxdaq.constants import StimStepSize, StimShape, StartPolarity, TriggerEvent, TriggerPolarity
from pyxdaq.impedance import Frequency, Strategy
import math
import csv

xdaq = get_XDAQ(rhs=True)

print(xdaq.ports)
"""
XDAQ supports up to 4 X3SR32 Headstages, each headstage has 2 streams and each stream has 16 channels
HDMI Port 0: Stream 0 (ch 0-16), Stream 1 (ch 16-31)
HDMI Port 1: Stream 2 (ch 0-16), Stream 3 (ch 16-31)
HDMI Port 2: Stream 4 (ch 0-16), Stream 5 (ch 16-31)
HDMI Port 3: Stream 6 (ch 0-16), Stream 7 (ch 16-31)
The get_XDAQ function will connect to the XDAQ and detect the number of headstages connected
"""

def find_step_size(target_na):
    """
    Find the best step size to reach the target current
    """
    best_error = float('inf')
    best = None
    for step_size in StimStepSize:
        if math.isnan(step_size.nA):
            continue
        steps = min(255, round(target_na / step_size.nA))  # 255 is the maximum current step
        error = abs(target_na - step_size.nA * steps)
        if error < best_error:
            best_error = error
            best = step_size
    return best


def create_monophasic_pulse(mA: float, frequency: float):
    """
    Create a basic pulse with duty cycle 50%, current can be positive or negative.
         |-----|     |-----|
         |     |     |     |
    -----|     |-----|     |-----

    |--period--| = 1/frequency
    """
    half_period_ms = 1e3 / frequency / 2
    return (lambda **kwargs: kwargs)(
        # Polarity of the first phase
        polarity=StartPolarity.cathodic if mA < 0 else StartPolarity.anodic,
        # Shape of the pulse
        shape=StimShape.Monophasic,
        # Delay between the trigger and the start of the pulse
        delay_ms=0,
        # Duration of the first phase, there are only one phase in Monophasic shape
        phase1_ms=half_period_ms,
        phase2_ms=0,
        phase3_ms=0,
        step_size=find_step_size(abs(mA) * 1e6),
        # Current of the positive and negative phase, both value should be positive
        amp_neg_mA=0 if mA > 0 else -mA,
        amp_pos_mA=mA if mA > 0 else 0,
        # Please refer to Intan Manual for ampsettle and charge recovery
        pre_ampsettle_ms=0,
        post_ampsettle_ms=half_period_ms,
        post_charge_recovery_ms=0,
        # The duration after the pulse before the next pulse
        post_pulse_ms=half_period_ms,
        # Sending pulses continuously when the trigger is high
        trigger=TriggerEvent.Level,
        trigger_pol=TriggerPolarity.High,
        # Since we are using Level trigger, sending one pulse each time
        pulses=1,
    )


# Swap out the pulses function with this one to send biphasic pulses
def create_biphasic_pulse(mA: float, frequency: float):
    """
    Create a biphasic pulse
             |---------|                   |---------|
             |         |                   |         |
    ---------|         |         |---------|         |
                       |         |                   |
                       |---------|                   |---------
    |-delay--|                             |
             |-phase1--|                   |-phase1--| ...
                       |-phase2--|         |
                                 | post    |
                                   pulse   |

    |-----------------period---------------| = 1/frequency
    """
    period_ms = 1e3 / frequency
    return (lambda **kwargs: kwargs)(
        polarity=StartPolarity.cathodic if mA < 0 else StartPolarity.anodic,
        shape=StimShape.Biphasic,
        delay_ms=0,
        phase1_ms=period_ms / 3,
        phase2_ms=period_ms / 3,
        phase3_ms=0,
        step_size=find_step_size(abs(mA) * 1e6),
        amp_neg_mA=abs(mA),
        amp_pos_mA=abs(mA),
        pre_ampsettle_ms=0,
        post_ampsettle_ms=period_ms / 3,
        post_charge_recovery_ms=0,
        post_pulse_ms=period_ms / 3,
        trigger=TriggerEvent.Level,
        trigger_pol=TriggerPolarity.High,
        pulses=1,
    )

def send_pulses(
    xdaq: XDAQ,
    stream: int,
    channel: int,
    duration_ms: float,
    pulse_current_mA: float,
    pulse_frequency: float,
):
    # The software trigger id, 0~7, can be shared by multiple stim
    software_trigger_id = 0

    # The enable_stim function will return a function to disable the stim
    disable_stim = enable_stim(
        xdaq=xdaq,
        stream=stream,
        channel=channel,
        # Trigger source, 24~31 is the software trigger 0~7
        trigger_source=24 + software_trigger_id,
        **create_biphasic_pulse(pulse_current_mA, pulse_frequency)
        # **create_monophasic_pulse(pulse_current_mA, pulse_frequency)
    )

    # Enable software trigger
    xdaq.manual_trigger(software_trigger_id, True)

    # Calculate the number of steps to run, the number of steps should be multiple of 128 to avoid alignment error
    run_steps = (int(duration_ms / 1000 * xdaq.sampleRate.rate) + 127) // 128 * 128

    # Start running
    xdaq.setStimCmdMode(True)
    # Speed up the process by discarding the reading of the data block
    # It's possible to run without blocking the script, but this will require more complex logic
    # See runAndReadDataBlock function for more fine-grained control
    xdaq.runAndReadDataBlock(run_steps, discard=True)
    xdaq.setStimCmdMode(False)
    # Stop running

    # Disable software trigger after the run
    xdaq.manual_trigger(software_trigger_id, False)
    # Disable the stim, a stim can run multiple times, here we set the stim every time for demonstration
    disable_stim()

    return run_steps

#corrects for issues in percieved vs actual channel count due to PCB design
def translate_channels(list):
    order = [14, 12, 4, 5, 10, 11, 2, 3, 8, 9, 0, 1, 13, 6, 7, 15]
    translated_list = []
    for num in list:
        translated_list.append(order[num])

    return translated_list

#performs impedance check of all channels at 1000hz
def run_measure_impedance(writer, col1):
    magnitude1000, phase1000 = xdaq.measure_impedance(
            frequency=Frequency(1000),
    # 0.2 seconds per measurement
    strategy=Strategy.from_duration(0.2),
    channels=translate_channels([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),
    progress=False
    )
    for j in range(16):
        print(f'___Impedance at channel {j}, 1000 Hz: {magnitude1000[target_stream,j]:.2f} Ohm')

    row = [col1] + [f"{magnitude1000[target_stream, channel_num]:.2f} Ohm" for channel_num in range(16)]
    writer.writerow(row)

#########################################################################################################################

# Prompt for file name
base_foldername = input("Enter the folder where the data is stored (i.e., 01may24_1): ")

# creates csv file
csv_file_path = f"/Users/christopherwarren/pyxdaq/data/{base_foldername}/rawdata/{base_foldername}_platingdata.csv"
header_row = ['Stimulated Channel'] + [f'Channel {i}' for i in range(16)]

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header_row)

    target_stream = 0
    # target_channels = translate_channels([      1,       2,       3,       4,       5,       6,       7,       9,      10,      11,      12,      13,      14,      15])
    # target_iter =                        [      1,       2,       2,       4,       4,       6,       8,       1,       2,       2,       4,       4,       6,       8] # 150000 ms per iter
    # target_currents =                    [0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00002, 0.00002, 0.00002, 0.00002, 0.00002, 0.00002, 0.00002] # mA

    target_channels = translate_channels([      1,       2,       3,       4,       5,       6,       7,       8,       9,      10,      11,      12,      13,      14,      15])
    target_iter =                        [      1,       2,       2,       4,       8,       1,       2,       2,       4,       8,       1,       2,       2,       4,       8] # 150000 ms per iter
    target_currents =                    [0.00001, 0.00001, 0.00001, 0.00001, 0.00001, 0.00002, 0.00002, 0.00002, 0.00002, 0.00002, 0.00004, 0.00004, 0.00004, 0.00004, 0.00004] # mA


    # print('Checking starting impedance at 1000 Hz')
    # run_measure_impedance(writer, 'None')

    for index in range(len(target_channels)):
        for i in range(target_iter[index]):
            target_duration = 150000 # ms - 2.5 minutes
            target_pulse_current = target_currents[index] # mA
            target_pulse_frequency = 50 # Hz
            print(f'Run {i+1}, Channel {target_channels[index]}: Sending {target_pulse_frequency}Hz {target_pulse_current}mA pulses for {target_duration}ms (dutycycle 50%)')
            run_steps = send_pulses(
                xdaq,
                stream=target_stream,
                channel=target_channels[index],
                duration_ms=target_duration,
                pulse_current_mA=target_pulse_current,
                pulse_frequency=target_pulse_frequency
            )
        # print(f'Channel {target_channels[index]} complete. Checking impedance at 1000 Hz')
        # run_measure_impedance(writer, target_channels[index])

print(f"Impedance data saved to {csv_file_path}")
