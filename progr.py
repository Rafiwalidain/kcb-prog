import osmnx as ox
import networkx as nx
import folium
import requests
import matplotlib.pyplot as plt
from geopy.distance import geodesic

# Fungsi geocoding dari alamat ke koordinat
def geocode_alamat(alamat):
    url = f"https://nominatim.openstreetmap.org/search?q={alamat}&format=json"
    headers = {"User-Agent": "Astar-Routing-Script"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        raise ValueError(f"Alamat tidak ditemukan: {alamat}")

# User input alamat
alamat_awal = input("Masukkan alamat asal (contoh: Jl. Raya Kenjeran No.300, Surabaya): ")
alamat_tujuan = input("Masukkan alamat tujuan (contoh: Jl. Kalijudan No.98, Surabaya): ")

# Ubah alamat ke koordinat
start_coords = geocode_alamat(alamat_awal)
end_coords = geocode_alamat(alamat_tujuan)

# Hitung jarak antar dua titik dalam meter
jarak_meter = geodesic(start_coords, end_coords).meters

# Tentukan titik tengah antara koordinat start dan end
mid_lat = (start_coords[0] + end_coords[0]) / 2
mid_lon = (start_coords[1] + end_coords[1]) / 2

# Tentukan radius ambil graf dengan buffer 1 km
radius = jarak_meter + 1000  # meter

# Ambil graf berdasarkan titik tengah dan radius tersebut
G = ox.graph_from_point((mid_lat, mid_lon), dist=radius, network_type='drive')

# Cari simpul terdekat di graf
start_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
end_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])

# Cari rute menggunakan A*
route = nx.astar_path(G, start_node, end_node, weight='length')

# Visualisasi rute dengan folium
m = folium.Map(location=start_coords, zoom_start=14)
route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
folium.PolyLine(route_coords, color='blue', weight=5).add_to(m)
folium.Marker(start_coords, popup="Gudang", icon=folium.Icon(color='green')).add_to(m)
folium.Marker(end_coords, popup="Pelanggan", icon=folium.Icon(color='red')).add_to(m)

# Simpan hasil ke file HTML
m.save("rute_user_input.html")

# --- Menambahkan visualisasi graf jalan ---
# Buat visualisasi graf jaringan menggunakan matplotlib
fig, ax = plt.subplots(figsize=(10, 10))

# Gambar graf jalan yang dilalui rute
ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='w', ax=ax)

# Simpan grafik ke file
plt.savefig("graf_jalan.png")
plt.close()

# Tampilkan informasi lebih detail tentang jalan yang dilalui
jalan_dilewati = []
for i in range(len(route) - 1):
    u, v = route[i], route[i + 1]
    street = G[u][v].get('name', 'Unnamed road')  # Nama jalan
    jalan_dilewati.append(street)

print("\n✅ Peta rute berhasil dibuat!")
print("📁 Silakan lihat file 'rute_user_input.html' di browser.")
print("\n📁 Grafik jalan yang dilalui:")
print("Silakan buka file 'graf_jalan.png' untuk melihat graf jalan yang dilewati rute.")

# Menampilkan daftar jalan yang dilalui
print("\n--- Jalan yang Dilewati ---")
for i, jalan in enumerate(jalan_dilewati, 1):
    print(f"{i}. {jalan}")
