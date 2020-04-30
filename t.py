# import time
# import atexit

# from apscheduler.schedulers.background import BackgroundScheduler


# def print_date_time():
#     print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=print_date_time, trigger="interval", seconds=3)
# scheduler.start()

# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

# while True:
# 	d = 0
# 	d = d * 2

d = {'res':0}
d['f'] = 'f'
print(d)