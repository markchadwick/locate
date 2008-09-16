from threading import Thread

class PresenceDaemon(Thread):
    def __init__(self, timeout=1):
        """
        :Parameters:
            timeout : int
                number of seconds to wait to select a socket.
        """
        Thread.__init__(self)
        
        self._socket_timeout = timeout
        self._running = True

        self._registered_services = []

    def register_service(self, instance, port, version, params={}):
        service_type = self._get_service_type(instance)
        service_repr = self._get_service_repr(service_type, port)

        self._register_service(service_type, instance, port, version, params)
        self._registered_services.append(instance)
        
    def unregister_service(self, instance):
        instances = [i for i in self._registered_services if i == instance]
        
        for instance in instances:
            self._unregister_service(instance)
            self._registered_services.remove(instance)

    def run(self):
        pass
        
    def stop(self):
        """
        Cleanly shuts down the Presence Daemon.
        """
        self._running = False
        
    def _get_service_type(self, instance):
        if isinstance(instance, type):
            service_type = instance.__name__
        elif isinstance(instance, str):
            service_type = instance
        else:
            service_type = instance.__class__.__name__

        return service_type

    def _get_service_repr(self, service_type, port):
        return "%s:%s" % (service_type, port)

    def _register_service(self, repr):
        raise "Presence subclass must implement _register_service"
        
    def _unregister_service(self, repr):
        raise "Presence subclass must implement _unregister_service"
        