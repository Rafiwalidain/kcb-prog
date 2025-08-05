from flask import Flask, render_template, request, send_file
import osmnx as ox
import networkx as nx
import folium
import requests
import matplotlib.pyplot as plt
from geopy.distance import geodesic

app = Flask(__name__)

def geocode_alamat(alamat):
    url = f"https://nominatim.openstreetmap.org/search?q={alamat}&format=json"
    headers = {"User-Agent": "Astar-Routing-Script"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        raise ValueError(f"Alamat tidak ditemukan: {alamat}")

@app.route('/', methods=['GET', 'POST'])
def index():
    rute_html_path = "rute_user_input.html"
    graf_image_path = "static/graf_jalan.png"
    jalan_dilewati = []

    if request.method == 'POST':
        alamat_awal = "JNE Surabaya"
        alamat_tujuan = request.form['alamat_tujuan']

        try:
            start_coords = geocode_alamat(alamat_awal)
            end_coords = geocode_alamat(alamat_tujuan)

            jarak_meter = geodesic(start_coords, end_coords).meters
            mid_lat = (start_coords[0] + end_coords[0]) / 2
            mid_lon = (start_coords[1] + end_coords[1]) / 2
            radius = jarak_meter + 1000

            G = ox.graph_from_point((mid_lat, mid_lon), dist=radius, network_type='drive')
            start_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
            end_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])

            route = nx.astar_path(G, start_node, end_node, weight='length')

            # Folium map
            m = folium.Map(location=start_coords, zoom_start=14)
            route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
            folium.PolyLine(route_coords, color='blue', weight=5).add_to(m)
            folium.Marker(start_coords, popup="Gudang", icon=folium.Icon(color='green')).add_to(m)
            folium.Marker(end_coords, popup="Pelanggan", icon=folium.Icon(color='red')).add_to(m)
            m.save(rute_html_path)

            # Matplotlib graph
            fig, ax = plt.subplots(figsize=(10, 10))
            ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='w', ax=ax)
            plt.savefig(graf_image_path)
            plt.close()

            # Nama jalan
            for i in range(len(route) - 1):
                u, v = route[i], route[i + 1]
                edge_data = G.get_edge_data(u, v)
                if edge_data:
                    nama_jalan = edge_data[0].get('name', 'Unnamed road')
                else:
                    nama_jalan = 'Unnamed road'
    
                if nama_jalan not in jalan_dilewati:
                    jalan_dilewati.append(nama_jalan)


            return render_template('index.html',
                                   alamat_tujuan=alamat_tujuan,
                                   jalan_dilewati=jalan_dilewati,
                                   show_result=True)
        except Exception as e:
            return render_template('index.html', error=str(e), show_result=False)

    return render_template('index.html', show_result=False)

@app.route('/peta')
def peta():
    return send_file('rute_user_input.html')

if __name__ == '__main__':
    app.run(debug=True)
