import logging
import sys

LOG = logging.getLogger(__name__)


def import_class(import_str):
    '''Returns a class from a string including module and class.'''
    mod_str, _sep, class_str = import_str.rpartition('.')
    try:
        __import__(mod_str)
        return getattr(sys.modules[mod_str], class_str)
    except (ImportError, ValueError, AttributeError), exc:
        LOG.debug('Inner Exception: %s', exc)
        raise


def import_object(import_str, *args, **kw):
    '''Returns an object including a module or module and class.'''
    try:
        __import__(import_str)
        return sys.modules[import_str]
    except ImportError:
        cls = import_class(import_str)
        return cls(*args, **kw)


def import_static_method(import_str):
    '''Returns a method ref'''
    try:
        mod_name, cls_name, func_name = import_str.rsplit('.', 2)
        __import__(mod_name)
        cls = getattr(sys.modules[mod_name], cls_name)
        return getattr(cls, func_name)
    except ImportError:
        return import_class(import_str)
