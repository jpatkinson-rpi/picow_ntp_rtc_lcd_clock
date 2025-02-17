#-------------------------------------------------------------------
# NTP Time Decoder for RPi PICO-W
#
# Display decoded Date & Time on HD44780 16x2 LCD 
#
# NTP format: https://en.wikipedia.org/wiki/Network_Time_Protocol
#
# For HD44780 LCD I2C driver use lcd_api.py & pico_i2c_lcd.py
# from https://github.com/T-622/RPI-PICO-I2C-LCD
#-------------------------------------------------------------------

from machine import Pin
from machine import Timer, Pin
from time import sleep
from machine import I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

import network

from machine import RTC

from wifissid import get_wifi_ssid, get_wifi_passphrase

import utime as time
import usocket as socket
import ustruct as struct

DEBUG_TIME = False
DEBUG_DST = False

LCD_I2C_SDA_PIN = 0
LCD_I2C_SCK_PIN = 1
LCD_I2C_ADDR    = 0x27

LCD_NUM_ROWS = 2
LCD_NUM_COLS = 16

# SSID & PASSPHRASE for Wi-Fi
ssid = get_wifi_ssid()
passphrase = get_wifi_passphrase()

daysofweek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months     = [ '-', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]
timezone   = [ 'GMT', 'BST' ]

BST_OFFSET = 60 * 60 # British Summer Time 1 hour offset

# UK NTP Hosts
NTP_HOSTS = [ 'uk.pool.ntp.org', 'ntp2d.mcc.ac.uk', 'ntp2c.mcc.ac.uk','ntp.cis.strath.ac.uk' ]

# NTP uses an epoch of 1 January 1900. Unix uses an epoch of 1 January 1970. 
NTP_EPOCH_OFFSET = 2208988800

dst_flag = 0
wlan = network.WLAN(network.STA_IF)

#################################################
# connect to WLAN
#################################################
def wlan_connect( ssid, passphrase ):  
   global wlan
   wlan.active(True)
   if wlan.status() != 3:
      wlan.connect(ssid, passphrase)
      while wlan.status() != 3:
         pass
   if wlan.status() != 3:
      print("failed to connect to", ssid)
      retval = False
   else:
      status = wlan.ifconfig()
      ipaddress = status[0]
      print('connected to', ssid, ipaddress)
      retval = True
   return retval


#################################################
# disconnect from WLAN
#################################################
def wlan_disconnect():
   global wlan
   wlan.disconnect()
   wlan.active(False)


########################################################
# BST is last Sunday in March to last Sunday in October
# check current time with bst_start_times & bst_end_times
########################################################
def dst_check( unix_format_time, year ):
   global dst_flag
   # BST starts last Sunday in March
   # find last day of March
   # Time format: year, month, day, hour, minute, second, weekday, day of the year, daylight saving
   time_tuple = (year, 3, 31, 2, 0, 0, 0, 0, 0)
   secs = time.mktime(time_tuple)
   tm = time.gmtime(secs)
   if DEBUG_DST == True :
      print("Mar 31st:", tm)
      print("Mar 31st tm_wday=", tm[6])
   # adjust date to last Sunday
   offset = ((tm[6] + 1) % 7) * (24 * 60 * 60)
   if DEBUG_DST == True :
      print( "offset=", offset )
   bst_start_secs = int(secs-offset)
   if DEBUG_DST == True :
      print("bst_start_secs=", bst_start_secs)
      bst_start_gmtime = time.gmtime(bst_start_secs)
      print(bst_start_gmtime)

   # BST ends last Sunday in October
   # find last day of October   
   time_tuple = (year, 10, 31, 2, 0, 0, 0, 0, 0)
   secs = time.mktime(time_tuple)
   tm = time.gmtime(secs)
   if DEBUG_DST == True :
      print("Oct 31st:", tm)
      print("Oct 31st tm_wday=", tm[6])
      
   # adjust date to last Sunday
   offset = ((tm[6] + 1) % 7) * (24 * 60 * 60)
   if DEBUG_DST == True :
      print( "offset=", offset )
   bst_end_secs = int(secs-offset)
   if DEBUG_DST == True :
      print("bst_end_secs=", bst_end_secs)
      bst_end_gmtime = time.gmtime(bst_end_secs)
      print(bst_end_gmtime)

   if DEBUG_DST == True :
      print("unix_format_time=", unix_format_time)

   if unix_format_time > bst_start_secs and unix_format_time < bst_start_secs:
      dst_flag = True
   else:
      dst_flag = False
   return dst_flag


#################################################
# get time from NTP Server
#################################################
def get_ntp_time():
   retval = False

   NTP_QUERY = bytearray(48)
   NTP_QUERY[0] = 0x1B
  
   addr = None
   host_index = 0
   while addr == None:
      # wait for valid NTP server
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.settimeout(10)
      try:
         addr = socket.getaddrinfo(NTP_HOSTS[host_index], 123)[0][-1]
      except OSError as error:
         print("OSError", error, NTP_HOSTS[host_index])
         host_index += 1
         if host_index == len(NTP_HOSTS):
            host_index = 0
         sock.close()
    
   print( "connected to:", NTP_HOSTS[host_index], addr)

   rc = sock.sendto(NTP_QUERY, addr)
   ntp_msg = sock.recv(48)
   sock.close()
   
   #NTP time bytes 40-44 network unsigned long format
   ntp_time = struct.unpack("!L", ntp_msg[40:44])[0]
   return ntp_time


#######################################################################
# Get NTP time
# convert from NTP to Unix Epoch
# check DST
# store to RTC
#######################################################################
def set_rtc_time():
   status = False
   if wlan_connect( ssid, passphrase):
      ntp_format_time = get_ntp_time()
      unix_format_time = ntp_format_time - NTP_EPOCH_OFFSET
      unix_format_gmtime = time.gmtime( unix_format_time )

      # NTP returns UTC (GMT)
      # check for DST and adjust
      dst_check( unix_format_time, unix_format_gmtime[0] )
      if dst_flag == True:
         unix_format_time += BST_OFFSET
      unix_format_gmtime = time.gmtime( unix_format_time )
      print(unix_format_gmtime)

      # gmtime: year, month, mday, hour, minute, second, weekday, yearday
      year = unix_format_gmtime[0]
      month = unix_format_gmtime[1]
      dayofmonth = unix_format_gmtime[2]
      dayofweek = unix_format_gmtime[6] + 1
      hour = unix_format_gmtime[3]
      minute = unix_format_gmtime[4]
      seconds = unix_format_gmtime[5]

      # RTC datetime: year, month, mday, week_day, hours, minutes, seconds, 0
      rtc.datetime((year, month, dayofmonth, dayofweek, hour, minute, seconds, 0))   
      wlan_disconnect()
      status = True
   else:
      status = False
    
   return status

######################################################
# main program body
######################################################
if __name__ == "__main__":

   yesterday = 0
   init_display = True # initialise display time
   
   # Initialise I2C to LCD
   i2c = I2C( 0, sda=machine.Pin(LCD_I2C_SDA_PIN), scl=machine.Pin(LCD_I2C_SCK_PIN), freq=400000 )
   lcd = I2cLcd( i2c, LCD_I2C_ADDR, LCD_NUM_ROWS, LCD_NUM_COLS )

   lcd.hide_cursor()
   lcd.backlight_on()
   lcd.clear()
   lcd.move_to(0,0)
   lcd.putstr("===NTP Clock===")
   time.sleep(2)
   lcd.clear()
   lcd.move_to(0,0)
   lcd.putstr("Get NTP Time...")
   
   rtc = RTC()
   
   set_rtc_time()
   
   lcd.clear()
   
   while True:

      t = rtc.datetime()
      #year, month, day, weekday, hours, minutes, seconds, subseconds)
      year = t[0]
      month = t[1]
      dayofmonth = t[2]
      dayofweek = t[3]
      hour = t[4]
      minute = t[5]
      seconds = t[6]
      if DEBUG_TIME == True:
         print( "----------------")
         print( hour, minute, seconds, timezone[ dst_flag ] )
         print( daysofweek[dayofweek], dayofmonth, months[month], year )
         print( "----------------")

      # update display time
      if init_display or seconds == 0:
         lcd.move_to( 0, 0 )
         lcd.putstr( " {:>02d}:{:>02d}:{:>02d}   ".format(hour, minute, seconds) )
         lcd.putstr( timezone[dst_flag] )

         lcd.move_to( 0, 1 )
         lcd.putstr( daysofweek[dayofweek] )
         lcd.putstr( " {:>02d} {:>03s} {:>04d} ".format(dayofmonth, months[month], year) )

         init_display = False
      else:
         # update display seconds only
         lcd.move_to( 7, 0 )
         lcd.putstr( "{:>02d}".format(seconds) )

      # update RTC at 3am
      if dayofmonth != yesterday and hour == 3:
         set_rtc_time()
         yesterday = dayofmonth
          
      time.sleep(0.2)
