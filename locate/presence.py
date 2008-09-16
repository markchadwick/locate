import pybonjour
import select
import logging
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
        


class BonjourMonitorDaemon(Thread):
    def __init__(self, monitor_class, callback):
        Thread.__init__(self)
        
        self._presence_type = BonjourPresenseDaemon.instance_to_ref(monitor_class)
        self._callback = callback
        self.running = True

    def run(self):
        browse_sd_ref = pybonjour.DNSServiceBrowse(
                            regtype=self._presence_type,
                            callBack=self._browse_event_callback)

        try:
            while self.running:
                ready = select.select([browse_sd_ref], [], [], 1)
                if browse_sd_ref in ready[0]:
                    pybonjour.DNSServiceProcessResult(browse_sd_ref)
        finally:
            browse_sd_ref.close()
            
    def stop(self):
        self.running = False
        

    def _browse_event_callback(self, sd_ref, flags, interface_index, error_code,
                                service_name, reg_type, reply_domain):
                                
        if error_code != pybonjour.kDNSServiceErr_NoError:
            return

        if not (flags & pybonjour.kDNSServiceFlagsAdd):
            print '*' * 60
            print 'Service removed'
            print service_name
            print reg_type
            print reply_domain
            print '*' * 60
            return

        resolve_sd_ref = pybonjour.DNSServiceResolve(
                            0,
                            interface_index,
                            service_name,
                            reg_type,
                            reply_domain,
                            self._service_registered_callback)

        self.target_resolved = False
        try:
            while not self.target_resolved:
                ready = select.select([resolve_sd_ref], [], [], 1)
                if resolve_sd_ref in ready[0]:
                    pybonjour.DNSServiceProcessResult(resolve_sd_ref)
        finally:
            self.target_resolved = False
            resolve_sd_ref.close()
    def _service_registered_callback(self, sd_ref, flags, interface_index,
                                    error_code, fullname, hosttarget, port,
                                    txt_record):
                                    
        if error_code == pybonjour.kDNSServiceErr_NoError:
            self.target_resolved = True
            self._callback(hosttarget, port)
        