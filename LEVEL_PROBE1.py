import serial
from queue import Queue
import threading,  datetime
import codecs, sys
import statistics
import Controller1, qtgui1
ser = None

global display_cal_range
display_cal_range = '0'


global display_level
display_level = '0'

global display_current, a_max, slp
display_current = '0'
a_max=7605				# current maximum decimal value
slp = 19.56


global str_range
str_range='55'

input_q = Queue()

final_data = []

def bigend(var):
    # code to big endian
    return codecs.encode(codecs.decode(var, 'hex')[::-1], 'hex').decode()

def read_data():
    if ser.isOpen() and Controller1.flag:
        # while True:
            # print("gps............"+ser_gps.read().hex())
            input_q.put(ser.read().hex())


def process_data(empty_value, full_value):
    global str_range
    if input_q.not_empty and Controller1.flag:
        # print("hiiiiiiii")
        if input_q.get() == str_range:
            for _ in range(6):
                str_range = str_range + input_q.get() ##must be inside for loop
            print("Received data:",str_range)
            address = int(str_range[4:6], 16) ##outside for loop
            ref_checksum1 = int(str_range[12:14], 16)
            ref_checksum = hex(ref_checksum1)[2:]
            cal_checksum1 = (int(str_range[4:6], 16) + int(str_range[6:8], 16) + int(str_range[8:10], 16) + int(str_range[10:12], 16)) & 0xFF  ##ANDing with '0xFF'to extract lower byte
            cal_checksum = hex(cal_checksum1)[2:]
            print(address, ref_checksum, cal_checksum)

            ##To validate data
            if address == 6 and cal_checksum == ref_checksum:
                print("valid data")
                cal_range = (int(bigend((str_range)[8:12]), 16) & int('7fff', 16)) / 256
                final_data.append(empty_value-cal_range)
                print("Range:",cal_range, "Tank level:",empty_value-cal_range)
                Controller1.file.write(str(datetime.datetime.now()) + " | valid data | " + '  '.join([str_range[j:j + 2] for j in range(0, len(str_range), 2)]) + " | " + str(cal_range) + " | " + str(empty_value-cal_range)+ "\n")
            else:
                print("invalid data")
                Controller1.file.write(str(datetime.datetime.now()) + " | invalid data | " + '  '.join([str_range[j:j + 2] for j in range(0, len(str_range), 2)]) +"\n")

            if len(final_data) == 100:
                global level, current, a_max, slp
                level = str(round(statistics.mean(final_data), 3))

                depth = round(statistics.mean(final_data), 3) * 1000
                t_diff = empty_value - full_value
                slope = ((a_max - 80.000) / (t_diff - full_value))
                a_val = ((depth / 1000) - full_value) * slope + 80.000

                slope = ((slp - 4.0) / (a_max - 80.000))
                current = str(round(((a_val - 80.000) * slope + 4.000), 3))
                        #print("Mean..................................." + display_data)


            final_data.clear()


        str_range = '55'

def ser_close():
    try:

        ser.close()
        print(ser.is_open)

    except:
        pass

    sys.exit()

if __name__ =='main':
    ser.flushInput()
    ser.flushOutput()

    thread1 = threading.Thread(target=read_data)
    thread2 = threading.Thread(target=process_data)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    ser.close()

