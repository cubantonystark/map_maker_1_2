import threading, time
def my_threaded_func(arg, arg2):
    print ("Running thread! Args:", (arg, arg2))
    time.sleep(10)
    print ("Done!")

def second_threaded_func(arg, arg2):
    print ("Running thread 2! Args:", (arg, arg2))
    while 1==1:
        print ("thread 2")
        time.sleep(1)
    print ("Done!")
thread = threading.Thread(target=my_threaded_func, args=("I'ma", "thread"))
thread = threading.Thread(target=second_threaded_func, args=("I'ma", "thread"))
thread.start()
print ("Spun off thread")