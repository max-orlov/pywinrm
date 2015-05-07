__author__ = 'maxim'
from winrm import Session, Response, SessionPool

# session_key = {
#     "shell_id": None,
#     "command_id": None,
#     "command_done": None
# }
#
# reponse = {
#     "stdout": None,
#     "stderr": None,
#     "return_code": None
# }

args = ('ping', '192.168.10.178 -n 5'.split())
args2 = ('ping', '8.8.8.8 -n 5'.split())
dest = '192.168.41.217'
cred = ('Administrator', 'Aa123456')

s = Session(dest, auth=cred)

sp = SessionPool()
print 'a'
key = sp.run_cmd(s, *args)
print 'b'
key2 = sp.run_cmd(s, *args2)
print 'c'

while sp.get_response(key) is None:
    pass
while sp.get_response(key2) is None:
    pass

print sp.get_response(key).std_out
print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
print sp.get_response(key2).std_out
