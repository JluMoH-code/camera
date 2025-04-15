import struct

class CommandFormatter:
    
    def base_command(response, command):       
        if not command in CommandFormatter.RESPONSE_FORMATTER_BASE_COMMANDS:
            return False
                
        return CommandFormatter.RESPONSE_FORMATTER_BASE_COMMANDS[command](response)
    
    def zoom_1(response):
        data = CommandFormatter.data_from_response(response)
        return struct.unpack('<h', data)[0] / 10
    
    def zoom__1(response):
        data = CommandFormatter.data_from_response(response)
        return struct.unpack('<h', data)[0] / 10

    def absolute_zoom(response):
        return response

    def acquire_max_zoom(response):
        return response

    def manual_focus_1(response):
        return response

    def manual_focus__1(response):
        return response

    def take_picture(response):
        return True

    def record_video(response):
        return True

    def rotate_100_100(response):
        return response

    def auto_centering(response):
        return response

    def gimbal_status(response):
        return response

    def auto_focus(response):
        data = CommandFormatter.data_from_response(response)
        return int(data.hex())

    def hardware_id(response):
        data = CommandFormatter.data_from_response(response)
        return data[:10]

    def firmware_version(response):
        data = CommandFormatter.data_from_response(response)
        
        camera_hex = data[0:4]
        gimbal_hex = data[4:8]
        
        camera = f"{camera_hex[2]}.{camera_hex[1]}.{camera_hex[0]}"
        gimbal = f"{gimbal_hex[2]}.{gimbal_hex[1]}.{gimbal_hex[0]}"
        
        return [camera, gimbal]

    def lock_mode(response):
        return response
    
    def follow_mode(response):
        return response

    def fpv_mode(response):
        return response

    def attitude_data(response):
        data_hex = CommandFormatter.data_from_response(response)
        
        if len(data_hex) < 6: return [None, None, None, None, None, None]
        
        yaw = struct.unpack('<h', data_hex[0:2])[0] / 10
        pitch = struct.unpack('<h', data_hex[2:4])[0] / 10
        roll = struct.unpack('<h', data_hex[4:6])[0] / 10
  
        if len(data_hex) == 12:
            yaw_velocity = struct.unpack('<h', data_hex[6:8])[0] / 10
            pitch_velocity = struct.unpack('<h', data_hex[8:10])[0] / 10
            roll_velocity = struct.unpack('<h', data_hex[10:12])[0] / 10
  
            return [yaw, pitch, roll, yaw_velocity, pitch_velocity, roll_velocity]
        else:
            return [yaw, pitch, roll, None, None, None]

    def video_hdmi(response):
        return response

    def video_cvbs(response):
        return response

    def video_off(response):
        return response

    def laser_rangefinder(response):
        return response

    def data_from_response(response):
        response_bytes = bytes.fromhex(response.hex())

        data_len_byte = response_bytes[3:4]
        data_len = struct.unpack('>B', data_len_byte)[0]

        return response_bytes[8:(8+data_len)]

    RESPONSE_FORMATTER_BASE_COMMANDS = {
		"zoom-1": zoom_1,
        "zoom--1": zoom__1,
        "absolute-zoom": absolute_zoom,
        "acquire-max-zoom": acquire_max_zoom, 
        "manual-focus-1": manual_focus__1,
        "manual-focus--1": manual_focus__1, 
        "take-picture": take_picture,
        "record-video": record_video,
        "rotate-100-100": rotate_100_100,
        "auto-centering": auto_centering,
        "gimbal-status": gimbal_status,
        "auto-focus": auto_focus,
        "hardware-id": hardware_id,
        "firmware-version": firmware_version,
        "lock-mode": lock_mode,
        "follow-mode": follow_mode,
        "fpv-mode": fpv_mode,
        "attitude-data": attitude_data,
        "video-hdmi": video_hdmi,
        "video-cvbs": video_cvbs,
        "video-off": video_off,
        "laser-rangefinder": laser_rangefinder,
	}