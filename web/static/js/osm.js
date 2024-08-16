document.addEventListener("DOMContentLoaded", function() {
    // *** 放置地圖
    let zoom = 17; // 縮放程度，間距為 0 - 18
    let center = [25.019448151190158, 121.21634240643077]; // 中心點座標：橫山書法藝術公園
    let map = L.map('map').setView(center, zoom); // 使用新添加的map元素

    // 設定地圖的圖層
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap', // 商用時必須要有版權出處
        zoomControl: true , // 是否秀出 - + 按鈕
    }).addTo(map);
    
    const DroneIcon = L.icon({
        iconUrl: '../static/img/Drone_icon.png',
        iconSize: [40, 40],
    });

    // 無人機標籤
    const DroneCenter = [25.021431498025557, 121.21861694845937]; //marker center
    const DroneMarker = L.marker(DroneCenter, {
        icon: DroneIcon,
        opacity: 1.0
    }).addTo(map);

    // Marker 加上 Tooltip
    DroneMarker.bindTooltip("Drone position", {
        direction: 'bottom', // right、left、top、bottom、center。default: auto
        permanent: false, // true是滑鼠移過才出現，false是一直出現
        opacity: 1.0
    }).openTooltip();

    // 自定義圖標：汽車、公車、卡車、機車
    const CarIcon = L.icon({
        iconUrl: '../static/img/car_icon.png',
        iconSize: [40, 40],
    });
    const BusIcon = L.icon({
        iconUrl: '../static/img/bus_icon.png',
        iconSize: [40, 40],
    });
    const TruckIcon = L.icon({
        iconUrl: '../static/img/truck_icon.png',
        iconSize: [40, 40],
    });
    const ScooterIcon = L.icon({
        iconUrl: '../static/img/scooter_icon.png',
        iconSize: [40, 40],
    });

    const btnPutMarkers = document.getElementById('put-markers');
    btnPutMarkers.addEventListener('click', e => {
        e.preventDefault();
        
        // 獲取經緯度和訊號類型
        const latitude = parseFloat(document.getElementById('lat_input').value);
        const longitude = parseFloat(document.getElementById('lng_input').value);
        const vehicleType = document.querySelector('input[name="vehicle-type"]:checked').value;

        // 根據訊號類型選擇圖標
        let selectedIcon;
        switch(vehicleType) {
            case 'car':
                selectedIcon = CarIcon;
                break;
            case 'bus':
                selectedIcon = BusIcon;
                break;
            case 'truck':
                selectedIcon = TruckIcon;
                break;
            case 'scooter':
                selectedIcon = ScooterIcon;
                break;
            default:
                selectedIcon = CarIcon; // 默認圖標
        }

        // 放置標記
        if (!isNaN(latitude) && !isNaN(longitude)) {
            L.marker([latitude, longitude], { icon: selectedIcon }).addTo(map);
        } else {
            alert('Please enter valid latitude and longitude.');
        }
    });

});