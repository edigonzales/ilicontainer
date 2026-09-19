def classFactory(iface):
    from .plugin import IbxPlugin

    return IbxPlugin(iface)
