import socket
import errno

class CameraControl():	
	def __init__(self):
		self.UDP_IP = "192.168.144.25"
		self.UDP_PORT = 37260
		self.buffer_size = 1024
		self.timeout = 1
		
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.settimeout(self.timeout)
		
	def send(self, command):
		self.sock.sendto(command, (self.UDP_IP, self.UDP_PORT))
		return True

	def _clear_receive_buffer(self):
		packets_cleared = 0
		try:
			self.sock.setblocking(False)
			while True:
				try:
					data, addr = self.sock.recvfrom(self.buffer_size)
					# print(f"Очищено из буфера от {addr}: {data.hex(' ')}") # Раскомментируйте для отладки
					packets_cleared += 1
				except BlockingIOError:
					break
				except socket.error as e:
					if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
						break
					else:
						print(f"Ошибка сокета при очистке буфера: {e}")
						break
				except Exception as e:
					print(f"Непредвиденная ошибка при очистке буфера: {e}")
					break
		finally:
			self.sock.setblocking(True)
			self.sock.settimeout(self.timeout)

	def request(self, command):
		self._clear_receive_buffer()
		if not self.send(command): return False
		try:
			data, addr = self.sock.recvfrom(self.buffer_size)
			# print(f"Получено от {addr}: {data.hex(' ')}")
		except socket.timeout:
			print("Таймаут ожидания ответа.")
			return False
		except socket.error as e:
			print(f"Ошибка приема: {e}")
			return False
			
		return data

if __name__ == "__main__":
	# camera = CameraControl()
	# command = CameraCommandManager.base_commands()["fpv-mode"]
	# command = CameraCommandManager.compile_command(command)
	# res = camera.send(command)
	# print(res)
	pass