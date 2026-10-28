"""Load Delhi road segments from OpenStreetMap into PostGIS with H3 indexes."""
import osmnx as ox
import h3

G = ox.graph_from_place("New Delhi, India", network_type="drive")
edges = ox.graph_to_gdfs(G, nodes=False)
edges["h3_index"] = edges.geometry.centroid.apply(lambda p: h3.latlng_to_cell(p.y, p.x, 9))
print(len(edges), "segments")   # then bulk insert with geoalchemy2
