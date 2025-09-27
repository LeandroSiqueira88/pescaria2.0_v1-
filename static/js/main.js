document.addEventListener('DOMContentLoaded', function() {
    console.log("main.js carregado.");

    // Lógica para o campo de upload de arquivo
    const fileInput = document.getElementById('foto');
    const fileNameSpan = document.getElementById('file-name');
    
    if (fileInput && fileNameSpan) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameSpan.textContent = this.files[0].name;
            } else {
                fileNameSpan.textContent = 'Nenhum arquivo selecionado';
            }
        });
    }

    // Lógica para o mapa interativo
    const mapContainer = document.getElementById('map-container');
    const localInput = document.getElementById('local');
    const latitudeInput = document.getElementById('latitude');
    const longitudeInput = document.getElementById('longitude');

    if (mapContainer && localInput && latitudeInput && longitudeInput) {
        // Inicializa o mapa em uma localização padrão (Ribeirão Preto, SP)
        const defaultLat = -21.1764;
        const defaultLon = -47.8188;
        let map = L.map(mapContainer).setView([defaultLat, defaultLon], 13);
        let marker = null;

        L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19,
        }).addTo(map);

        function updateLocation(lat, lng) {
            localInput.value = `Lat: ${lat.toFixed(6)}, Lon: ${lng.toFixed(6)}`;
            latitudeInput.value = lat;
            longitudeInput.value = lng;
        }

        // Tenta obter a localização do usuário
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    map.setView([lat, lon], 13);
                    
                    if (marker) map.removeLayer(marker);
                    marker = L.marker([lat, lon], { draggable: true }).addTo(map).bindPopup("Local da Pescaria").openPopup();
                    updateLocation(lat, lon);
                    
                    marker.on('dragend', function(e) {
                        const newLatLng = e.target.getLatLng();
                        updateInputs(newLatLng.lat, newLatLng.lng);
                    });
                },
                function(error) {
                    console.error("Erro na geolocalização: ", error);
                    // Deixa a localização padrão no mapa
                }
            );
        } else {
            console.error("Geolocalização não é suportada por este navegador.");
        }
        
        // Adiciona a funcionalidade de clique no mapa
        map.on('click', function(e) {
            if (marker) {
                map.removeLayer(marker);
            }
            marker = L.marker(e.latlng, { draggable: true }).addTo(map).bindPopup("Local da Pescaria").openPopup();
            updateLocation(e.latlng.lat, e.latlng.lng);
            
            marker.on('dragend', function(ev) {
                const newLatLng = ev.target.getLatLng();
                updateInputs(newLatLng.lat, newLatLng.lng);
            });
        });
    } else {
        console.error("Elementos do mapa não encontrados. Verifique o HTML.");
    }
});