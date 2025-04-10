from pyzkfp import ZKFP2
import sys
import time
import json
import base64
from loguru import logger
from PIL import Image
import io

class Scanner:
    def __init__(self):
        self.zkfp2 = ZKFP2()
        self.is_connected = False
        self.logger = logger

        self._setup_logger()

    def _setup_logger(self):
        logger.remove()
        logger.add(
            sys.stderr,  # Log to stderr
            format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | "
                   "<level>{level: <8}</level> | "
                   "<cyan><b>{line}</b></cyan> - "
                   "<white><b>{message}</b></white>",
            colorize=True
        )

    def connect_to_device(self) -> bool:
        try:
            self.zkfp2 = ZKFP2()
            self.zkfp2.Init()

            count = self.zkfp2.GetDeviceCount()
            if count == 0:
                self.logger.error("No fingerprint devices found")
                return False

            self.logger.info(f"{count} devices found. Connecting to the first device...")
            self.zkfp2.OpenDevice(0)
            self.zkfp2.Light("green")
            self.is_connected = True

            self.zkfp2.DBClear()
            self.logger.success("Device connected successfully")
            return True

        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def capture(self):
        if not self.is_connected:
            return {'status': 'error', 'message': 'Device not connected'}

        self.logger.info("Waiting for fingerprint... (place finger on scanner)")
        detected_image = None
        start_time = time.time()
        timeout = 30  # 30-second timeout
        while not detected_image and (time.time() - start_time) < timeout:
            try:
                result = self.zkfp2.AcquireFingerprintImage()
                if result:
                    detected_image = result
                    # Convert raw bytes to a PIL Image (grayscale)
                    image = Image.frombytes("L", (self.zkfp2.width, self.zkfp2.height), detected_image)
                    # Save to a BytesIO object as PNG
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    # Encode to base64
                    image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                    return {
                        'status': 'success',
                        'message': 'Fingerprint captured successfully',
                        'image': image_base64
                    }
                else:
                    time.sleep(0.1)
            except Exception as e:
                self.zkfp2.Light("red")
                self.logger.error(f"Error during fingerprint capture: {e}")
                return {'status': 'error', 'message': f'Capture failed: {str(e)}'}
        
        # If we exit the loop, it means we timed out
        return {'status': 'error', 'message': f'Timeout: No fingerprint detected within {timeout} seconds'}

    def close_device(self):
        if self.is_connected and hasattr(self.zkfp2, 'CloseDevice'):
            try:
                self.zkfp2.CloseDevice()
            except Exception as e:
                self.logger.error(f"Error closing device: {e}")

if __name__ == "__main__":
    scanner = Scanner()
    try:
        if scanner.connect_to_device():
            result = scanner.capture()
            print(json.dumps(result))  # Always print result to stdout
            scanner.close_device()
        else:
            print(json.dumps({'status': 'error', 'message': 'Failed to connect to device'}))
    except Exception as e:
        print(json.dumps({'status': 'error', 'message': f'Script failed: {str(e)}'}))