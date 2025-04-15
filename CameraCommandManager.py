import struct
from CameraControl import CameraControl
from CommandFormatter import CommandFormatter

class CameraCommandManager:
	BASE_COMMANDS = {
		"zoom-1": "55 66 01 01 00 00 00 05 01 8d 64",
		"zoom--1": "55 66 01 01 00 00 00 05 FF 5c 6a",
		"absolute-zoom": "55 66 01 02 00 01 00 0F 04 05 60 BB",
		"acquire-max-zoom": "55 66 01 00 00 00 00 16 B2 A6",
		"manual-focus-1": "55 66 01 01 00 00 00 06 01 de 31",
		"manual-focus--1": "55 66 01 01 00 00 00 06 ff 0f 3f",
		"take-picture": "55 66 01 01 00 00 00 0c 00 34 ce",
		"record-video": "55 66 01 01 00 00 00 0c 02 76 ee",
		"rotate-100-100": "55 66 01 02 00 00 00 07 64 64 3d cf",
		"auto-centering": "55 66 01 01 00 00 00 08 01 d1 12",
		"gimbal-status": "55 66 01 00 00 00 00 0a 0f 75",
		"auto-focus": "55 66 01 01 00 00 00 04 01 bc 57",
		"hardware-id": "55 66 01 00 00 00 00 02 07 f4",
		"firmware-version": "55 66 01 00 00 00 00 01 64 c4",
		"lock-mode": "55 66 01 01 00 00 00 0c 03 57 fe",
		"follow-mode": "55 66 01 01 00 00 00 0c 04 b0 8e",
		"fpv-mode": "55 66 01 01 00 00 00 0c 05 91 9e",
		"attitude-data": "55 66 01 00 00 00 00 0d e8 05",
		"video-hdmi": "55 66 01 01 00 00 00 0c 06 f2 ae",
		"video-cvbs": "55 66 01 01 00 00 00 0c 07 d3 be",
		"video-off": "55 66 01 01 00 00 00 0c 08 3c 4f",
		"laser-rangefinder": "55 66 01 00 00 00 00 15 D1 96" 
	} 
    
	def __init__(self):
		self.camera = CameraControl()
    
	def base_command(self, command):
		if not (command in self.BASE_COMMANDS):
			return False
		
		request = self.compile_command(self.BASE_COMMANDS[command])
		response = self.camera.request(request)
  
		if not response: return False  
		return CommandFormatter.base_command(response, command)
    
	def angle_to_hex(self, angle):
		packed = struct.pack("<h", angle)
		return " ".join(f"{b:02x}" for b in packed)
	
	def rotate(self, yaw, pitch):
		command = "55 66 01 04 00 00 00 0e "
		yaw_hex = self.angle_to_hex(yaw)
		pitch_hex = self.angle_to_hex(pitch)
		
		command += yaw_hex + " "
		command += pitch_hex + " "
		
		command = self.add_check_sum(command)
		command = self.compile_command(command)
		return self.camera.send(command)
 
	def compile_command(self, command):
		return bytes.fromhex(command)

	def reflect(self, x, bits):
		return int(f"{x:0{bits}b}"[::-1], 2)

	def crc16_kermit(self, data):
		poly = 0x8408  
		crc = 0x0000
		for byte in data:
			reflected_byte = self.reflect(byte, 8)  
			crc ^= reflected_byte
			for _ in range(8):
				if crc & 0x0001:
					crc = (crc >> 1) ^ poly
				else:
					crc >>= 1
				crc &= 0xFFFF  
		crc = self.reflect(crc, 16) 
		return crc

	def add_crc16_kermit_to_hex_string(self, hex_string):
		data = bytes.fromhex(hex_string)
		checksum = self.crc16_kermit(data)
		checksum_bytes = checksum.to_bytes(2, 'little')  
		checksum_hex = checksum_bytes.hex()  
		return f"{hex_string} {checksum_hex[:2]} {checksum_hex[2:]}"

	def add_check_sum(self, command):
		return self.add_crc16_kermit_to_hex_string(command)