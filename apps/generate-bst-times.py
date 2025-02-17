######################################################
# Generate British Summer Time (BST) start & end times
#
# BST starts 2am last Sunday in March
# BST ends 2am last Sunday in October
######################################################
import time

BST_START_YEAR = 2025 # 2025
BST_NUM_YEARS = 30  # Number of years

daysofweek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months = [ '-', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]

bst_start_times = [0] * BST_NUM_YEARS
bst_start_dates = [''] * BST_NUM_YEARS

bst_end_times = [0] * BST_NUM_YEARS
bst_end_dates = [''] * BST_NUM_YEARS


for year in range( BST_START_YEAR, BST_START_YEAR+BST_NUM_YEARS ):
   # BST starts last Sunday in March
   # find last day of March
   # year, month, day, hour, minute, second, weekday, day of the year, daylight saving
   time_tuple = (year, 3, 31, 2, 0, 0, 0, 0, 0)
   secs = time.mktime(time_tuple)
   tm = time.gmtime(secs)
   #print(tm)
   #print("tm_wday=", tm[6])
   # adjust date to last Sunday
   offset = ((tm[6] + 1) % 7) * (24 * 60 * 60)
   #print( "offset=", offset )
   bst_start_secs = int(secs-offset)
   bst_start_gmtime = time.gmtime(bst_start_secs)
   #print(bst_start_gmtime)
   #print( "{:.0f} #".format((bst_start_secs)) + daysofweek[bst_start_gmtime[6]], bst_start_gmtime[2], months[bst_start_gmtime[1]], bst_start_gmtime[0] )   
   bst_start_times[year-BST_START_YEAR] = bst_start_secs
   bst_start_dates[year-BST_START_YEAR] = "{:>2}".format( daysofweek[bst_start_gmtime[6]]) + " {:>2}".format(str(bst_start_gmtime[2])) + " {:>2}".format(months[bst_start_gmtime[1]]) + " {:>4}".format(str(bst_start_gmtime[0]))   

   # BST ends last Sunday in October
   # find last day of October   
   time_tuple = (year, 10, 31, 2, 0, 0, 0, 0, 0)
   secs = time.mktime(time_tuple)
   tm = time.gmtime(secs)
   #print(tm)
   #print("tm_wday=", tm[6])
   # adjust date to last Sunday
   offset = ((tm[6] + 1) % 7) * (24 * 60 * 60)
   #print( "offset=", offset )
   bst_end_secs = int(secs-offset)
   bst_end_gmtime = time.gmtime(bst_end_secs)
   #print(bst_end_gmtime)
   #print( "{:.0f} #".format((bst_end_secs)) + daysofweek[bst_end_gmtime[6]], bst_end_gmtime[2], months[bst_end_gmtime[1]], bst_end_gmtime[0] )   
   bst_end_times[year-BST_START_YEAR] = bst_end_secs
   bst_end_dates[year-BST_START_YEAR] = "{:>2}".format( daysofweek[bst_end_gmtime[6]]) + " {:>2}".format(str(bst_end_gmtime[2])) + " {:>2}".format(months[bst_end_gmtime[1]]) + " {:>4}".format(str(bst_end_gmtime[0]))   

print( "BST_START_YEAR = ", BST_START_YEAR )
print( "BST_NUM_YEARS = ", BST_NUM_YEARS )
print('')
print( "bst_start_times = ", bst_start_times )
print( "bst_start_dates = ", bst_start_dates )
print( "bst_end_times   = ", bst_end_times )
print( "bst_end_dates   = ", bst_end_dates )



