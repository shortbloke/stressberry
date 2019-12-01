import subprocess
import time as tme
import os
import signal


def stress_cpu(num_cpus, time):
    subprocess.check_call(
        ["stress", "--cpu", str(num_cpus), "--timeout", "{}s".format(time)]
    )
    return


def cpuburn_test(time):
    try:
        print("Starting cpuburn")
        proc = subprocess.Popen(["cpuburn"], shell=True, preexec_fn=os.setsid)
        proc.communicate(timeout=time)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        print("Exiting cpuburn")
        # return
    return


def cooldown(interval=60, filename=None):
    """Lets the CPU cool down until the temperature does not change anymore.
    """
    prev_tmp = measure_temp(filename=filename)
    while True:
        tme.sleep(interval)
        tmp = measure_temp(filename=filename)
        print(
            "Current temperature: {:4.1f}°C - Previous temperature: {:4.1f}°C".format(
                tmp, prev_tmp
            )
        )
        if abs(tmp - prev_tmp) < 0.2:
            break
        prev_tmp = tmp
    return tmp


def measure_temp(filename=None):
    """Returns the core temperature in Celsius.
    """
    if filename is not None:
        with open(filename, "r") as f:
            temp = float(f.read()) / 1000
    else:
        # Using vcgencmd is specific to the raspberry pi
        out = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        temp = float(out.replace("temp=", "").replace("'C", ""))
    return temp


def measure_core_frequency(filename=None):
    """Returns the CPU frequency in MHz
    """
    if filename is not None:
        with open(filename, "r") as f:
            frequency = float(f.read()) / 1000
    else:
        # Only vcgencmd measure_clock arm is accurate on Raspberry Pi.
        # Per: https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=219358&start=25
        out = subprocess.check_output(["vcgencmd", "measure_clock arm"]).decode("utf-8")
        frequency = float(out.split("=")[1]) / 1000000
    return frequency


def measure_ambient_temperature(sensor_type="2302", pin="23"):
    """Uses Adafruit temperature sensor to measure ambient temperature
    """
    try:
        import Adafruit_DHT  # Late import so that library is only needed if requested
    except ImportError as e:
        print("Install adafruit_dht python module: pip install Adafruit_DHT --user")
        raise e

    sensor_map = {
        "11": Adafruit_DHT.DHT11,
        "22": Adafruit_DHT.DHT22,
        "2302": Adafruit_DHT.AM2302,
    }
    try:
        sensor = sensor_map[sensor_type]
    except KeyError as e:
        print("Invalid ambient temperature sensor")
        raise e
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    # Note that sometimes you won't get a reading and the results will be null
    # (because Linux can't guarantee the timing of calls to read the sensor).
    # The read_retry call will attempt to read the sensor 15 times with a 2 second delay.
    # Care should be taken when reading if on a time sensitive path
    # Temperature is in °C but can also be None
    return temperature


def test(stress_duration, idle_duration, cores, cpuburn):
    """Run test for specified duration with specified idle times
       at the start and end of the test.
    """
    if cores is None:
        cores = os.cpu_count()

    if cpuburn:
        print("Preparing to run cpuburn for [{}] seconds".format(stress_duration))
    else:
        print(
            "Preparing to stress [{}] CPU Cores for [{}] seconds".format(
                cores, stress_duration
            )
        )

    print("Idling for {} seconds...".format(idle_duration))
    tme.sleep(idle_duration)

    if cpuburn:
        cpuburn_test(time=stress_duration)
    else:
        stress_cpu(num_cpus=cores, time=stress_duration)

    print("Idling for {} seconds...".format(idle_duration))
    tme.sleep(idle_duration)
    return
