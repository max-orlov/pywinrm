__author__ = 'maxim'
from timeout import timeout, TimeoutException
from winrm import Session, Response, NonBlockingRequests

dest_addr = '192.168.40.44'
cred = ('Administrator', 'Aa123456')

args, args2 = ('ping', '192.168.10.178 -n 5'.split()), ('ping', '8.8.8.8 -n 5'.split())
ipconfig = ('ipconfig')
s = Session(dest_addr, auth=cred)

@timeout(50)
def reg():
    print "starting regular test"
    r = s.run_cmd('ipconfig')
    # print r.status_code
    # print r.std_out
    # print r.std_err
    print "regular test is done"
    return True


def custom():
    nbr = NonBlockingRequests()
    print 'called'
    key = nbr.run_cmd(s, *args)
    # key2 = nbr.run_cmd(s, *args2)
    print 'done calling'

    while nbr.get_response(key).status_code == -1:

        print nbr.get_response(key).std_out
        print "~~~~~~~~~~~~~~~~~~~~"
        # print nbr.get_response(key2).std_out

    print nbr.get_response(key).std_out
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    # print nbr.get_response(key2).std_out

# reg()
#
# is_good = False
# try:
#     reg()
#     is_good = True
# except TimeoutException:
#     print "Stuck of regulary" + TimeoutException.message
#
# if is_good:
custom()

