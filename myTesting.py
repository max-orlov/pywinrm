__author__ = 'maxim'
import StringIO
from winrm import Session
import sys

dic = {
    "dest_addr": '192.168.40.44',
    "cred": ('Administrator', 'Aa123456'),
    "cmd": ('ping', '192.168.10.178 -n 5'.split()),
    "cmd2": ('ping', '8.8.8.8 -n 5'.split()),
    "ipconf": 'ipconfig'
}

s = Session(dic["dest_addr"], auth=dic["cred"])
my_std_out, my_err_out = StringIO.StringIO(), StringIO.StringIO()


def reg():
    print("Start")

    r = s.run_cmd(*dic["cmd"], keep_track=True, out_stream=my_std_out, err_stream=my_err_out)

    print("Done")
    if r.status_code == 0:
        print(my_std_out.getvalue())
    else:
        print(my_err_out.getvalue())


reg()

# TODO: There is an issue for support on python 2.x or python 3.x - the whole project won't compile with python > 3.3
# TODO: but once using lower python version only StringIO works