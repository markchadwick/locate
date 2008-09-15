import logging

_LOCAL_REGISTERED_INSTACES = {}

class PresenseFactory(object):
    @classmethod
    def get_presense_daemon(self, instance, port, timeout):
        from locate.presence import BonjourPresenseDaemon
        return BonjourPresenseDaemon(instance, port, timeout=timeout)

    @classmethod
    def get_register_daemon(self, instance_type, callback):
        from locate.presence import BonjourMonitorDaemon
        return BonjourMonitorDaemon(instance_type, callback)

def register(reg_instance, port, timeout=1):
    presence = PresenseFactory.get_presense_daemon(reg_instance, port, timeout=timeout)
    presence.start()
    _LOCAL_REGISTERED_INSTACES[reg_instance] = presence
    return presence

def unregister(reg_instance):
    if reg_instance in _LOCAL_REGISTERED_INSTACES:
        _LOCAL_REGISTERED_INSTACES[reg_instance].stop()
        del _LOCAL_REGISTERED_INSTACES[reg_instance]

def listen_for_register(class_name, callback):
    presence = PresenseFactory.get_register_daemon(class_name, callback)
    presence.start()
    return presence
    
def listen_for_unregister(class_name, callback):
    pass
    