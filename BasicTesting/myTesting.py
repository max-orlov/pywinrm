__author__ = 'maxim'
from winrm import Session, Response, SessionPool

dest = '192.168.41.217'
cred = ('Administrator', 'Aa123456')

args, args2 = ('ping', '192.168.10.178 -n 5'.split()), ('ping', '8.8.8.8 -n 5'.split())


s = Session(dest, auth=cred)

sp = SessionPool()
print 'a'
key = sp.run_cmd(s, *args)
key2 = sp.run_cmd(s, *args2)
print 'b'

while sp.get_response(key).status_code == -1:
    pass
while sp.get_response(key2).status_code == -1:
    pass

print sp.get_response(key).std_out
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print sp.get_response(key2).std_out
