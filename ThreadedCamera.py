import cv2
import threading

class ThreadedCamera:
    def __init__(self, source, timeout=5):
        self.source = source
        self.timeout = timeout
        self.capture = None
        self.last_frame = None
        self.lock = threading.Lock()
        self.stopped = False
        self.connected = False
        self.thread = None
        self.read_thread = None

    def start(self):
        if not self.stopped:
            self.stop()
        print("Попытка подключения к камере...")
        self.stopped = False
        self.connect_thread = threading.Thread(target=self.try_connect, daemon=True)
        self.connect_thread.start()
        return self

    def try_connect(self):
        try:
            self.capture = cv2.VideoCapture(self.source)
            
            # Таймер для прерывания подключения
            timer = threading.Timer(self.timeout, self.stop_connection)
            timer.start()
            
            if self.capture.isOpened():
                self.connected = True
                print("Подключение успешно")
                self.read_thread = threading.Thread(target=self.update, daemon=True)
                self.read_thread.start()
            else:
                raise ConnectionError("Не удалось открыть поток")
                
        except Exception as e:
            print(f"Ошибка подключения: {str(e)}")
            self.stop()
        finally:
            timer.cancel()

    def stop_connection(self):
        if not self.connected:
            print(f"Таймаут подключения ({self.timeout} сек.)")
            self.stop()

    def update(self):
        print("Чтение потока начато")
        while not self.stopped and self.connected:
            grabbed, frame = self.capture.read()
            if not grabbed:
                print("Потеря соединения с камерой")
                self.stop()
                break
                
            with self.lock:
                self.last_frame = frame.copy()

        print("Поток чтения остановлен")
        if self.capture:
            self.capture.release()

    def read(self):
        with self.lock:
            return self.last_frame if self.last_frame is not None else None

    def stop(self):
        print("Остановка камеры...")
        if not self.stopped:
            self.stopped = True
            self.connected = False
            if self.capture:
                self.capture.release()