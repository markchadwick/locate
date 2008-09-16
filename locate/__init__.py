import logging

class PresenseFactory(object):
    _presence_daemon = None
    
    @classmethod
    def get_presence_daemon(self):
        if self._presence_daemon is not None:
            return self._presence_daemon
        else:
            from locate.impl.bonjour import BonjourPresenceDaemon as PresenceDaemon
            self._presence_daemon = PresenceDaemon()
            self._presence_daemon.start()
            return self._presence_daemon

    @classmethod
    def get_register_daemon(self, instance_type, callback):
        from locate.impl.bonjour import BonjourMonitorDaemon
        return BonjourMonitorDaemon(instance_type, callback)

def register(instance, port, version='1.0', params={}):
    presence = PresenseFactory.get_presence_daemon()
    
    presence.register_service(instance, port, version, params)
    return presence

def unregister(instance):
    presence = PresenseFactory.get_presence_daemon()
    
    presence.unregister_service(instance)
    return presence

def listen_for_register(class_name, callback):
    presence = PresenseFactory.get_register_daemon(class_name, callback)
    presence.start()
    return presence
    
def listen_for_unregister(class_name, callback):
    pass
    