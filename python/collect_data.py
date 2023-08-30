import argparse
import textwrap
import os
import json
from datetime import datetime
from pathlib import Path
from time import sleep

import pandas as pd
from pms7003 import Pms7003Sensor, PmsSensorException
from sensirion_sps30 import SPS30

class PMS7003Adapter:
    def __init__(self, port, datetime_strf='%Y-%m-%d %H:%M:%S.%f'):
        self.instance = Pms7003Sensor(port)
        self.datetime_strf = datetime_strf

    def read(self):
        data = self.instance.read()
        return {
            'pm1_0_mass_conc': data['pm1_0'],
            'datetime': datetime.now().strftime(self.datetime_strf)
        }

    def close(self):
        self.instance.close()

class SPS30Adapter:
    def __init__(self, port, datetime_strf='%Y-%m-%d %H:%M:%S.%f'):
        self.instance = SPS30(port)
        self.datetime_strf = datetime_strf
        self.instance.start_measurement()

    def read(self):
        data = self.instance.read_values()
        sleep(1)

        return {
            'pm1_0_mass_conc': data[0],
            'datetime': datetime.now().strftime(self.datetime_strf)
        }


    def close(self):
        self.instance.stop_measurement()


def get_args():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """\
            Collect data using PMS7003.

            Example:

            """
            "python collect_data.py"
            + "--filename='some_dir.json'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--sensor_type",
        type=str,
        help="PMS7003 or SPS30",
        default="SPS30",
        required=False
    )

    parser.add_argument(
        "--sensor_path",
        type=str,
        help="Sensor file path",
        default="/dev/tty.usbserial-AB0LO213",
        required=False
    )

    return parser.parse_args()

if __name__ == '__main__':
    cwd = os.getcwd()
    args = get_args()

    path = Path(cwd) / 'air_cleaner_data' / f'{str(datetime.now()).replace(" ", "_")}.csv'
    print(f"Path: {path}")

    sensor_path_0 = args.sensor_path

    sensor = None
    if args.sensor_type == 'SPS30':
        sensor = SPS30Adapter(sensor_path_0)
    else:
        sensor = PMS7003Adapter(sensor_path_0)

    sensors = [
        sensor
    ]

    datetime_strf = '%Y-%m-%d %H:%M:%S.%f'

    df = pd.DataFrame([])
    df.to_csv(str(path), index=False)

    try:
        while True:
            for i, sensor in enumerate(sensors):
                try:
                    reading = sensor.read()

                    print(reading)
                    df = df.append(reading, ignore_index=True)
                    df.to_csv(str(path), index=False)
                except Exception as e:
                    import pdb; pdb.set_trace()
                    if e.args and e.args[0] == 'unpack requires a buffer of 40 bytes':
                        continue
                    else:
                        raise e
                    # import pdb; pdb.set_trace()
                    # error_json = {
                        # 'error': 'Connection problem',
                        # 'datetime': datetime.now().strftime(datetime_strf)
                    # }
                    # print(error_json)

    except Exception as e:
        import pdb; pdb.set_trace()

        for sensor in sensors:
            sensor.close()
