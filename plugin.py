# -*- coding: utf-8 -*-
"""
BasemapTiles – Main plugin logic for QGIS 4.0 (Qt6)
"""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QToolBar, QToolButton, QMenu
from qgis.core import (
    QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem,
    QgsMessageLog, Qgis
)


class BasemapTiles:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar = None
        self.btn = None

        # Define basemaps: (display_name, xyz_url_template)
        self.basemaps = [
            # OpenStreetMap
            ("OpenStreetMap",
             "http://tile.openstreetmap.org/{z}/{x}/{y}.png"),

            # ESRI Base Imagery
            ("ESRI World Imagery",
             "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Street Map",
             "https://services.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Topographic Map",
             "https://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Physical Map",
             "https://services.arcgisonline.com/arcgis/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Terrain Base",
             "https://services.arcgisonline.com/arcgis/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Shaded Relief",
             "https://services.arcgisonline.com/arcgis/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI National Geographic World Map",
             "https://services.arcgisonline.com/arcgis/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI USA Topographic Maps",
             "https://services.arcgisonline.com/arcgis/rest/services/USA_Topo_Maps/MapServer/tile/{z}/{y}/{x}"),

            # ESRI Reference Overlays (transparent layers for overlaying)
            ("ESRI World Reference Overlay",
             "https://services.arcgisonline.com/arcgis/rest/services/Reference/World_Reference_Overlay/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Boundaries and Places",
             "https://services.arcgisonline.com/arcgis/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Transportation",
             "https://services.arcgisonline.com/arcgis/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}"),

            # ESRI Ocean Services
            ("ESRI World Ocean Base",
             "https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Ocean Reference",
             "https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}"),

            # ESRI Hillshade Layers
            ("ESRI World Hillshade",
             "https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}"),
            ("ESRI World Hillshade (Dark)",
             "https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade_Dark/MapServer/tile/{z}/{y}/{x}"),
            
            # Virtual Earth Services
            ("Virtual Earth Street Map",
             "http://ecn.t0.tiles.virtualearth.net/tiles/r{q}.png?g=1"),
            ("Virtual Earth Satellite",
             "http://ecn.t0.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1"),
            ("Virtual Earth Hybrid",
             "http://ecn.t0.tiles.virtualearth.net/tiles/h{q}.jpeg?g=1")
        ]

    def initGui(self):
        # Remove any existing BasemapTiles toolbar to avoid duplicates
        existing = self.iface.mainWindow().findChild(QToolBar, "BasemapTilesToolbar")
        if existing:
            existing.deleteLater()

        self.toolbar = QToolBar("Basemap Tiles")
        self.toolbar.setObjectName("BasemapTilesToolbar")
        self.toolbar.setWindowTitle("Basemap Tiles")

        # Create a tool button with a drop-down menu
        self.btn = QToolButton()
        self.btn.setText("➕ BasemapTiles")
        self.btn.setToolTip("Choose a basemap tile layer to add")
        self.btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        # Build the menu – connect using lambda to capture name and URL
        menu = QMenu()
        for name, url in self.basemaps:
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, n=name, u=url: self.add_tile_layer(n, u))
        self.btn.setMenu(menu)

        self.toolbar.addWidget(self.btn)
        self.iface.mainWindow().addToolBar(self.toolbar)
        self.toolbar.setVisible(True)

    def unload(self):
        if self.toolbar:
            self.toolbar.deleteLater()
            self.toolbar = None

    def add_tile_layer(self, layer_name, url_template):
        """
        Add an XYZ tile layer to the current project.
        :param layer_name: Display name in the layer tree.
        :param url_template: Tile URL with {z}, {x}, {y} placeholders.
        """
        # Build the datasource URI for QGIS XYZ tiles
        datasource = f"type=xyz&url={url_template}"

        # Create the raster layer (provider 'wms' handles XYZ tiles)
        layer = QgsRasterLayer(datasource, layer_name, "wms")

        if not layer.isValid():
            error_msg = f"Failed to create tile layer: {layer.error().message()}"
            QgsMessageLog.logMessage(error_msg, "BasemapTiles", Qgis.Critical)
            self.iface.messageBar().pushMessage(
                "BasemapTiles", error_msg, level=Qgis.Critical, duration=5
            )
            return

        # Set the layer CRS to Web Mercator (EPSG:3857) – standard for these tiles
        layer.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))

        # Add the layer to the project
        QgsProject.instance().addMapLayer(layer)

        # Optional: zoom to the new layer's extent
        self.iface.mapCanvas().setExtent(layer.extent())
        self.iface.mapCanvas().refresh()

        self.iface.messageBar().pushMessage(
            "BasemapTiles",
            f"Added '{layer_name}' to the map.",
            level=Qgis.Success,
            duration=3
        )
        QgsMessageLog.logMessage(f"Added basemap: {layer_name}", "BasemapTiles", Qgis.Info)
