import re
import base64
import sys
import xml.etree.ElementTree as ET

from winrm.protocol import Protocol


class Response(object):
    """Response from a remote command execution"""

    def __init__(self, args):
        self.std_out, self.std_err, self.status_code = args
        self.std_out_buffer, self.std_err_buffer = [], []

    def __repr__(self):
        # TODO put tree dots at the end if out/err was truncated
        return '<Response code {0}, out "{1}", err "{2}">'.format(
            self.status_code, self.std_out[:20], self.std_err[:20])


class Session(object):
    # TODO implement context manager methods
    def __init__(self, target, auth, transport='plaintext'):
        username, password = auth
        self.url = self._build_url(target, transport)
        self.protocol = Protocol(self.url, transport=transport,
                                 username=username, password=password)

    def get_protocol(self):
        return self.protocol

    def run_cmd(self, command, args=(), out_stream=sys.stdout, err_stream=sys.stderr, keep_track=False):
        # TODO optimize perf. Do not call open/close shell every time
        shell_id = self.protocol.open_shell()
        command_id = self.protocol.run_command(shell_id, command, args)
        rs = Response(self.protocol.get_command_output(shell_id, command_id, out_stream, err_stream, keep_track))
        self.protocol.cleanup_command(shell_id, command_id)
        self.protocol.close_shell(shell_id)
        return rs

    def run_ps(self, script, out_stream=sys.stdout, err_stream=sys.stderr, keep_track=False):
        """base64 encodes a Powershell script and executes the powershell
        encoded script command
        """

        # must use utf16 little endian on windows
        base64_script = base64.b64encode(script.encode("utf_16_le"))
        rs = self.run_cmd("powershell -encodedcommand %s" % (base64_script), out_stream, err_stream, keep_track)
        if len(rs.std_err):
            # if there was an error message, clean it it up and make it human
            # readable
            rs.std_err = self.clean_error_msg(rs.std_err)
        return rs

    def clean_error_msg(self, msg):
        """converts a Powershell CLIXML message to a more human readable string
        """

        # if the msg does not start with this, return it as is
        if msg.startswith("#< CLIXML\r\n"):
            # for proper xml, we need to remove the CLIXML part
            # (the first line)
            msg_xml = msg[11:]
            try:
                # remove the namespaces from the xml for easier processing
                msg_xml = self.strip_namespace(msg_xml)
                root = ET.fromstring(msg_xml)
                # the S node is the error message, find all S nodes
                nodes = root.findall("./S")
                new_msg = ""
                for s in nodes:
                    # append error msg string to result, also
                    # the hex chars represent CRLF so we replace with newline
                    new_msg += s.text.replace("_x000D__x000A_", "\n")
            except Exception as e:
                # if any of the above fails, the msg was not true xml
                # print a warning and return the orignal string
                print("Warning: there was a problem converting the Powershell"
                      " error message: %s" % (e))
            else:
                # if new_msg was populated, that's our error message
                # otherwise the original error message will be used
                if len(new_msg):
                    # remove leading and trailing whitespace while we are here
                    msg = new_msg.strip()
        return msg

    def strip_namespace(self, xml):
        """strips any namespaces from an xml string"""
        try:
            p = re.compile("xmlns=*[\"\"][^\"\"]*[\"\"]")
            allmatches = p.finditer(xml)
            for match in allmatches:
                xml = xml.replace(match.group(), "")
            return xml
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def _build_url(target, transport):
        match = re.match(
            '(?i)^((?P<scheme>http[s]?)://)?(?P<host>[0-9a-z-_.]+)(:(?P<port>\d+))?(?P<path>(/)?(wsman)?)?',
            target)  # NOQA
        scheme = match.group('scheme')
        if not scheme:
            # TODO do we have anything other than HTTP/HTTPS
            scheme = 'https' if transport == 'ssl' else 'http'
        host = match.group('host')
        port = match.group('port')
        if not port:
            port = 5986 if transport == 'ssl' else 5985
        path = match.group('path')
        if not path:
            path = 'wsman'
        return '{0}://{1}:{2}/{3}'.format(scheme, host, port, path.lstrip('/'))


# class NonBlockingRequests():
#     """
#     A class which enables a non blocking support for commands running.
#     """
#     def __init__(self):
#         self._sessions = {}
#
#     def run_cmd(self, session, command, args, keep_track=False):
#         """
#         A function which launches the given command on the cmd in a non blocking manner.
#         :param session: The session to use for this command.
#         :param command: The command itself.
#         :param args: the args which the command receives.
#         :param keep_track: Whether printout any arriving std_out or std_err
#         :return: the key for the current command execution.
#         """
#         shell_id = session.get_protocol().open_shell()
#         command_id = session.get_protocol().run_command(shell_id, command, args)
#         command_key = "{0}:{1}".format(shell_id, command_id)
#         self._sessions[command_key] = {"session": session, "response": Response(["", "", -1])}
#         Thread(target=self._run_cmd, args=[command_key, keep_track]).start()
#         return command_key
#
#     def _run_cmd(self, command_key, keep_track):
#         """
#         Helper function for the run_cmd of the non blocking type.
#
#         :param command_key: the key of the current command.
#         :param keep_track: Whether printout any arriving std_out or std_err
#         :return: None
#         """
#         session = self._sessions[command_key]["session"]
#         shell_id, command_id = command_key[:command_key.index(':')], command_key[command_key.index(':') + 1:]
#         self._sessions[command_key]["response"] = session.get_results(shell_id, command_id, keep_track)
#
#     def run_ps(self, session, script, keep_track=False):
#         """
#         A function which launches the given power shell script in a non blocking manner.
#
#         :param session: The session to use for this command.
#         :param script: The script to run
#         :param keep_track: Whether printout any arriving std_out or std_err
#         :return: the key for the running script
#         """
#         command_key = hash(session)
#         self._sessions[command_key] = {"session": session, "response": Response(["", "", -1])}
#         Thread(target=self._run_ps, args=[command_key, script, keep_track]).start()
#
#     def _run_ps(self, command_key, script, keep_track):
#         """
#         Helper function for the run_ps of the non blocking type.
#         :param command_key: Receives the key of the script to execute.
#         :param script: the script to execute.
#         :param keep_track: Whether printout any arriving std_out or std_err
#         :return: None.
#         """
#         base64_script = base64.b64encode(script.encode("utf_16_le"))
#         session = self._sessions[command_key]["sessions"]
#         self._sessions[command_key]["response"] = session.run_cmd("powershell -encodedcommand %s" % (base64_script),
#                                                                   keep_track)
#         rs = self._sessions[command_key]["response"]
#         if len(rs.std_err):
#             self._sessions[command_key]["response"].std_err = session.clean_error_msg(rs.std_err)
#
#     def get_response(self, command_key):
#         """
#         You will only receive the response received so far. You might not get the entire output.
#
#         :param command_key: the key for the response.
#         :return: the response
#         """
#         return self._sessions[command_key]["response"]
#
#     def get_session(self, command_key):
#         """
#         Retrieves the sessions of the given command key
#         :param command_key: the key for the session.
#         :return: the session
#         """
#         return self._sessions[command_key]["session"]
#
#     def delete_dialog(self, command_key):
#         """
#         Deletes the entire dialog from the log.
#
#         :param command_key: the key of the command.
#         :return: None
#         """
#         del self._sessions[command_key]