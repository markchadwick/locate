import pybonjour
import select

from locate.presence import PresenceDaemon

class BonjourPresenceDaemon(PresenceDaemon):
    def __init__(self):
        super(BonjourPresenceDaemon, self).__init__()
        self._sock_refs = {}
        self._dead_socks = []

    def _register_service(self, service_type, instance, port, version, params):
        sock_ref = self._get_sock_ref(
                        name     = service_type,
                        reg_type = '_locate._tcp',
                        port     = port,
                        callback = None)
                        
        self._sock_refs[instance] = sock_ref

    def _unregister_service(self, instance):
        if instance in self._sock_refs:
            self._dead_socks.append(self._sock_refs[instance])
            del self._sock_refs[instance]

    def run(self):
        try:
            while self._running:
                socks = self._sock_refs.values()
                read_sock, write_sock, err_sock = \
                    select.select(socks, [], [], self._socket_timeout)

                for sock_ready in read_sock:
                    if sock_ready in self._sock_refs.values():
                        pybonjour.DNSServiceProcessResult(sock_ready)
                        
                        if sock_ready in self._dead_socks:
                            sock_read.close()
                            self._dead_socks.remove(sock_ready)
        finally:
            for sock in self._sock_refs.values():
                sock.close()

    def _get_sock_ref(self, name, reg_type, port, callback):
        return pybonjour.DNSServiceRegister(
                    name     = name,
                    regtype  = reg_type,
                    port     = port,
                    callBack = callback)
    