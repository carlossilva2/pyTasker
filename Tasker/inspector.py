import inspect


def implements(interface_cls):
    def _decorator(cls):
        verify_methods(interface_cls, cls)
        verify_properties(interface_cls, cls)
        verify_attributes(interface_cls, cls)
        return cls

    return _decorator


def verify_methods(interface_cls, cls):
    methods_predicate = lambda m: inspect.isfunction(m) or inspect.ismethod(m)
    for name, method in inspect.getmembers(interface_cls, methods_predicate):
        signature = inspect.signature(method)
        cls_method = getattr(cls, name, None)
        cls_signature = inspect.signature(cls_method) if cls_method else None
        if cls_signature != signature:
            raise NotImplementedError(
                f"'{cls.__name__}' must implement method '{name}({signature})' defined in interface '{interface_cls.__name__}'"
            )


def verify_properties(interface_cls, cls) -> None:
    prop_attrs = dict(
        fget='getter', 
        fset='setter', 
        fdel='deleter'
    )
    for name, prop in inspect.getmembers(interface_cls, inspect.isdatadescriptor):
        cls_prop = getattr(cls, name, None)
        for attr in prop_attrs:
            # instanceof doesn't work for class function comparison
            if type(getattr(prop, attr, None)) != type(getattr(cls_prop, attr, None)):
                raise NotImplementedError(
                    f"'{cls.__name__}' must implement a {prop_attrs[attr]} for property '{name}' defined in interface '{interface_cls.__name__}'"  # flake8: noqa
                )

def verify_attributes(interface_cls, cls) -> None:
    interface_attributes = get_attributes(interface_cls)
    cls_attributes = get_attributes(cls)
    for missing_attr in (interface_attributes - cls_attributes):
        raise NotImplementedError(
            f"'{cls.__name__}' must have class attribute '{missing_attr}' defined in interface '{interface_cls.__name__}'"
        )


def get_attributes(cls) -> set[str]:
    boring = dir(type('dummy', (object,), {}))
    return set(item[0] for item in inspect.getmembers(cls) if item[0] not in boring and not callable(item[1]))