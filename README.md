#-------------------------------------------------------------------
# NTP Time/Date Decoder for RPi PICO-W
#
# Display decoded Date & Time on HD44780 16x2 LCD 
#
# For HD44780 LCD I2C driver use lcd_api.py & pico_i2c_lcd.py
# from https://github.com/T-622/RPI-PICO-I2C-LCD
#
#-------------------------------------------------------------------

Download HD44780 LCD I2C driver lcd_api.py & pico_i2c_lcd.py from
https://github.com/T-622/RPI-PICO-I2C-LCD

Use apps generate-bst-times.py to create bsttimes.py
    - python3 apps/generate-bst-times.py > bsttimes.py

Enter Wi-Fi SSID & Passphrase details into wifissid.py
Upload lcd_api.py, pico_i2c_lcd.py & main.py, bsttimes.py, wifissid.py to RPi PICO-W

LCD I2C connects to PICO GPIO0 (SDA) and GPIO1 (SCK)

# BOOT SEQUENCE

1: Decoding valid NTP data and display Date/Time
![Alt text](https://github.com/jpatkinson-rpi/picow_ntp_rtc_lcd_clock/blob/main/images/prototype-001.jpg?raw=true "Date/Time decoded")
