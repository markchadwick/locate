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

        else:
            print '- ' * 30
            print "Unknown Instance!"

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



#    def __init__(self):
        
        
#        self.instance = instance
#        self.port = port
#        self.callback = callback
#        self.timeout = timeout
        
#        self.name = name
#        self.reg_type = self.__class__.instance_to_ref(instance)
        
#        self.running = True

#    @classmethod
#    def instance_to_ref(self, instance):
#        if isinstance(instance, type):
#            presence_type = instance.__name__
#        else:
#            presence_type = instance.__class__.__name__
#        return "_%s._tcp" % (presence_type)

#    def run(self):
#        sd_ref = pybonjour.DNSServiceRegister(
#                    name=self.name,
#                    regtype=self.reg_type,
#                    port=self.port,
#                    callBack=self._service_registered_callback)
#        try:
#            while self.running:
#                ready = select.select([sd_ref], [], [], self.timeout)
#                if sd_ref in ready[0]:
#                    pybonjour.DNSServiceProcessResult(sd_ref)
#        finally:
#            sd_ref.close()

#    def stop(self):
#        self.running = False
        
#    def _service_registered_callback(self, *args, **kwds):
#        if self.callback is not None:
#            self.callback(*args, **kwds)

    pass
    