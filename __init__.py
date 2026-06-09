# -*- coding: utf-8 -*-
"""
BasemapTiles – Add predefined basemap tile layers (OSM, Esri, Google, Bing) to QGIS 4.0
"""

from qgis.core import QgsApplication
from .plugin import BasemapTiles


def classFactory(iface):
    """Required plugin entry point."""
    return BasemapTiles(iface)
