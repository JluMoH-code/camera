import cv2
import threading

class ThreadedCamera:
    def __init__(self, source):
        self.source = source
        self.capture = cv2.VideoCapture(self.source)
        if not self.capture.isOpened():
            raise ValueError(f"Ошибка: Не удалось открыть видеоисточник {self.source}")

        self.grabbed, self.frame = self.capture.read()
        self.lock = threading.Lock()
        self.stopped = False
        self.thread = threading.Thread(target=self.update, args=(), daemon=True) # daemon=True позволяет завершить программу, даже если поток еще работает

    def start(self):
        print("Запуск потока чтения камеры...")
        self.stopped = False
        self.thread.start()
        return self

    def update(self):
        print("Поток чтения запущен.")
        while not self.stopped:
            grabbed, frame = self.capture.read()
            if not grabbed:
                
                print("Поток чтения: кадр не получен, остановка.")
                self.stop() 
                break
            
            with self.lock:
                self.grabbed = grabbed
                self.frame = frame
        print("Поток чтения остановлен.")
        self.capture.release() 

    def read(self):
        with self.lock:
            frame = self.frame.copy() if self.grabbed and self.frame is not None else None
        return frame

    def stop(self):
        print("Остановка потока чтения камеры...")
        self.stopped = True