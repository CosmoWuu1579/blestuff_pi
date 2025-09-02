import socket
import json
from datetime import datetime
from miniVNA import miniVNATiny, VNACalibrationBlock


class MiniVNAController:
    def __init__(self,
                 bt_mac="FC:01:7C:92:05:6C",
                 bt_port=4,
                 calibration_file="./REFL_miniVNATiny.cal",
                 serial_port='/dev/ttyUSB0',
                 baud_rate=921600):
        self.bt_mac = bt_mac
        self.bt_port = bt_port
        self.calibration_file = calibration_file
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        # Instantiate the instrument interface
        self.vna = miniVNATiny()
        # (If you want to make port/baud_rate dynamic, adjust miniVNATiny.__init__)

    def load_calibration(self):
        calBlock = self.vna.loadCalibrationRAWData(self.calibration_file)
        if calBlock is None:
            raise RuntimeError("Failed to load calibration file!")
        self.vna.calculateCalibrationTemperature(calBlock)
        calContext = self.vna.createCalibrationContextForCalibrationPoints(calBlock)
        cal_block_corr = self.vna.createCalibrationPoints(calContext, calBlock)
        mainCalibrationBlock = VNACalibrationBlock()
        mainCalibrationBlock.set_calib_param(calBlock)
        mainCalibrationBlock.set_calib_file_name(self.calibration_file)
        mainCalibrationBlock.setCalibrationPoints(cal_block_corr)
        mainCalibrationBlock.setTemperature(self.vna.temperature)
        self.mainCalibrationBlock = mainCalibrationBlock

    def sweep_to_json(self, start_freq, stop_freq, num_steps, save_json=True):
        # Resample calibration block to current sweep settings
        rcb = self.vna.createResizedCalibrationBlock(self.mainCalibrationBlock, fStart=start_freq, fStop=stop_freq, numSteps=num_steps, scanMode="REFL")
        data = self.vna.scan_reflection_mode_new(start_freq=start_freq, stop_freq=stop_freq, num_freq_sample=num_steps)
        context = self.vna.createCalibrationContextForCalibratedSamples(rcb)
        context.set_conversion_temperature(data.getDeviceTemperature())
        calSamples = self.vna.createCalibratedSamples(context, data)
        frequencies = [s.getFrequency() for s in calSamples.getCalibratedSamples() if s is not None]
        vna_output_data = {
            "frequencies": frequencies,
            "RL": calSamples.get_all_mmRL_values(),
            "RLPHASE": calSamples.get_all_mmRLPHASE_values()
        }
        now = datetime.now()
        file_name_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        file_name_vna_output = f"vna_data_{file_name_time_str}.json"
        if save_json:
            with open(file_name_vna_output, "w") as json_file:
                json.dump(vna_output_data, json_file, indent=4)
        self.last_json_file = file_name_vna_output
        return file_name_vna_output, vna_output_data

    def send_json(self, json_path=None):
        if json_path is None:
            json_path = self.last_json_file
        print(f"Attempting Bluetooth send to {self.bt_mac}:{self.bt_port} ...")
        try:
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            sock.settimeout(10)
            sock.connect((self.bt_mac, self.bt_port))
            with open(json_path, "rb") as f:
                data = f.read(1024)
                while data:
                    sock.sendall(data)
                    data = f.read(1024)
            sock.close()
            print("Bluetooth send: SUCCESS.")
        except OSError as e:
            print(f"Bluetooth send failed: {e}. Data saved locally at {json_path}")
            return False
        return True

    def sweep_and_send(self, start_freq, stop_freq, num_steps):
        print("Loading calibration...")
        self.load_calibration()
        print(f"Sweeping: {start_freq} Hz to {stop_freq} Hz, {num_steps} steps ...")
        json_path, _ = self.sweep_to_json(start_freq, stop_freq, num_steps)
        print(f"Sending JSON file: {json_path}")
        self.send_json(json_path)



if __name__ == "__main__":
    
    controller = MiniVNAController(
        bt_mac="FC:01:7C:92:05:6C",
        bt_port=4,
        calibration_file="./REFL_miniVNATiny.cal",
        serial_port='/dev/ttyUSB0',
        baud_rate=921600
    )
    
    controller.sweep_to_json(start_freq=1e6, stop_freq=30e6, num_steps=201)