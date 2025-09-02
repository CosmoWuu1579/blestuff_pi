import platform
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
import math
from enum import Enum
import copy


import socket
import json
from datetime import datetime
from src.Raspberry_Pi_0_W_scripts.miniVNA_Tiny_Calibration_R_Pi_0 import miniVNATiny, VNACalibrationBlock, VNADeviceInfoBlock

# /home/jcah/gitrepos/telemetry/src/Raspberry_Pi_0_W_scripts/miniVNA_Tiny_Calibration_R_Pi_0.py


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
    
        # controller = MiniVNAController(
                # bt_mac="FC:01:7C:92:05:6C",
                # bt_port=4,
                # calibration_file="./REFL_miniVNATiny.cal",
                # serial_port='/dev/ttyUSB0',
                # baud_rate=921600
        # )

        # controller.sweep_to_json(start_freq=1e6, stop_freq=30e6, num_steps=201)


        plt.ion()
        # freq_hz = 50000000  # 50MHz

        fStart = 1e6
        fStop = 1e9
        numSteps = 200

        print("miniVNA Tiny is going to initialize")
        m_vna = miniVNATiny()
        time.sleep(0.1)
        print(f"serial port settings: {m_vna.ser_port}")
        print(f"miniVNA Tinay is connected to Port {m_vna.port_name}")
        print(f"Baud rate is {m_vna.baud_rate}")
        time.sleep(0.1)
        m_vna.get_device_supply()
        time.sleep(0.1)
        m_vna.get_device_firmwareInfo()
        time.sleep(0.1)
        m_vna.get_device_temperature()
        # time.sleep(0.1)
        # dds_ticks_per_mhz = m_vna.frequency_to_tuning_word(freq_hz)
        # print(f"DDS Ticks/MHz: {dds_ticks_per_mhz}")
        # print(" Going to start generator")
        # time.sleep(1)
        # m_vna.start_generator(frequencyI = 0, frequencyQ = 0, num_freq_sample = 1)
        # time.sleep(1)
        # m_vna.scan_reflection_mode(start_freq = 1000000, stop_freq = 2000000 , num_freq_sample = 100)

        # Load calibration data
        # file_name = rf"src/Raspberry_Pi_0_W_scripts/REFL_miniVNATiny.cal"
        file_name = rf"src/REFL_miniVNA_Tiny_7000cal_3ovrscn.cal"
        calBlock = m_vna.loadCalibrationRAWData(file_name)

        # Check if calibration data was loaded successfully
        if calBlock is None:
                print("ERROR: Failed to load calibration file. Please check:")
                print(f"  1. File exists at: {file_name}")
                print(f"  2. File format is correct")
                print(f"  3. javaobj library is properly installed")
                m_vna.ser_port.close()
                exit(1)

        m_vna.calculateCalibrationTemperature(calBlock)
        calContext = m_vna.createCalibrationContextForCalibrationPoints(calBlock)
        cal_block_corr = m_vna.createCalibrationPoints(calContext, calBlock)
        
        mainCalibrationBlock = VNACalibrationBlock()
        mainCalibrationBlock.set_calib_param(calBlock)
        mainCalibrationBlock.set_calib_file_name(file_name)
        mainCalibrationBlock.setCalibrationPoints(cal_block_corr)
        mainCalibrationBlock.setTemperature(m_vna.temperature)

        # sv1 = SaveVar()
        # sv1.append_named_json_object(mainCalibrationBlock, name="mainCalibrationBlock")

        # VNACalibrationBlock
        rcb = m_vna.createResizedCalibrationBlock(mainCalibrationBlock, fStart=fStart, fStop=fStop, numSteps=numSteps,
                                              scanMode="REFL")
        time.sleep(1)

        data = m_vna.scan_reflection_mode_new(start_freq=fStart, stop_freq=fStop, num_freq_sample=numSteps)
        # sv1.append_named_json_object(data, name="data")

        context = m_vna.createCalibrationContextForCalibratedSamples(rcb)
        # sv1.append_named_json_object(context, name="context")

        dib = VNADeviceInfoBlock()
        # sv1.append_named_json_object(dib, name="dib")

        context.set_conversion_temperature(data.getDeviceTemperature())

        calSamples = m_vna.createCalibratedSamples(context, data)
        # Assuming 'block' is an instance of VNACalibratedSampleBlock or similar
        samples = calSamples.getCalibratedSamples()
        frequencies = [sample.getFrequency() for sample in samples if sample is not None]
        # print(frequencies)
        # sv_vna_data = SaveVar()
        np_frequencies = np.array(frequencies)
        calSamples.getCalibratedSamples()
        # print(calSamples.get_all_mmRL_values())
        # print(calSamples.get_all_mmRLPHASE_values())

        now = datetime.now()
        # Format as string suitable for filename, e.g., "2025-06-02_23-20-00"
        file_name_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        # Create filename with extension
        file_name_vna_output = f"vna_data_{file_name_time_str}.json"

        vna_output_data = {
                "frequencies": frequencies,
                "RL": calSamples.get_all_mmRL_values(),
                "RLPHASE": calSamples.get_all_mmRLPHASE_values()
        }
        
        # print(vna_output_data["frequencies"])
        #print(f"vna_output_data[RL]: {vna_output_data["RL"]}")
        #print(f"vna_output_data[RLPHASE]: {vna_output_data["RLPHASE"]}")
        # Save the data dictionary to a JSON file
        with open(file_name_vna_output, "w") as json_file:
                json.dump(vna_output_data, json_file, indent=4)

        system = platform.system()  # 'Windows', 'Linux', 'Darwin', etc.
        print(system)

        if system == "Linux":
                fig, ax = plt.subplots(2, 1, figsize=(10, 6))
                ax[0].plot(np_frequencies / 1e6, calSamples.get_all_mmRL_values(), marker='o', linestyle='-', color='b')
                ax[0].set_title('Reflection Loss (dB)')
                ax[0].set_xlabel('Frequency(MHz)')
                #ax[0].set_xlim(1, 2)
                #ax[0].set_ylim(-12, -4)  # Adjust y-axis limits as needed
                ax[0].set_ylabel('Reflection Loss (dB)')
                ax[0].grid(True)
                ax[1].plot(np_frequencies / 1e6, calSamples.get_all_mmRLPHASE_values(), marker='o', linestyle='-', color='r')
                ax[1].set_title('Reflection Phase (degrees)')
                ax[1].set_xlabel('Frequency(MHz)')
                ax[1].set_ylabel('Reflection Phase (degrees)')
                #ax[1].set_xlim(1, 2)
                #ax[1].set_ylim(50, 170)  # Adjust y-axis limits as needed
                ax[1].grid(True)
                plt.tight_layout()
                plt.ioff()
                plt.draw()
                plt.savefig(file_name[:-4] + ".png")
                plt.show()

        # plt.show()
        server_address = "FC:01:7C:92:05:6C"  # PC Bluetooth MAC address
        port = 4

        try:
                print(f"Attempting to connect to Bluetooth server at {server_address}:{port}")
                sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                sock.settimeout(10)  # 10 second timeout
                sock.connect((server_address, port))

                print("Bluetooth connection established, sending file...")
                with open(file_name_vna_output, "rb") as f:
                    data = f.read(1024)
                    while data:
                        sock.sendall(data)
                        data = f.read(1024)

                print("File sent successfully")
                sock.close()
                print("Socket closed on client side")
        except OSError as e:
                print(f"Bluetooth connection failed: {e}")
                print(f"Could not connect to {server_address}:{port}")
                print("Data has been saved locally to:", file_name_vna_output)
                print("You can transfer the file manually or fix the Bluetooth connection")
        except Exception as e:
                print(f"Unexpected error during Bluetooth transfer: {e}")
                print("Data has been saved locally to:", file_name_vna_output)

        print("Program End")
