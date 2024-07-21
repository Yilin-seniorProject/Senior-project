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
        iconUrl: '../static/Drone_icon.png',
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
        permanent: false, // 是滑鼠移過才出現，還是一直出現
        opacity: 1.0
    }).openTooltip();


    // 汽車標籤
    const CarCenter = [25.02020409808486, 121.2150120596153];
    const CarIcon = L.icon({
        iconUrl: '../static/car_icon.png',
        iconSize: [40, 40],
    });

    const CarMarker = L.marker(CarCenter, {
        icon: CarIcon,
        opacity: 1.0
    }).addTo(map);
    CarMarker.bindPopup(`緯度：${CarCenter[0]}<br>經度：${CarCenter[1]}`).openPopup();
    

    // 公車標籤
    const BusCenter = [25.02236270417824, 121.21548413994972];
    const BusIcon = L.icon({
        iconUrl: '../static/bus_icon.png',
        iconSize: [40, 40],
    });

    const BusMarker = L.marker(BusCenter, {
        icon: BusIcon,
        opacity: 1.0
    }).addTo(map);
    BusMarker.bindPopup(`緯度：${BusCenter[0]}<br>經度：${BusCenter[1]}`).openPopup();
    

    // 卡車標籤
    const TruckCenter = [25.018566260253085, 121.21632635354695];
    const TruckIcon = L.icon({
        iconUrl: '../static/Truck_icon.png',
        iconSize: [40, 40],
    });
    
    const TruckMarker = L.marker(TruckCenter, {
        icon: TruckIcon,
        opacity: 1.0
    }).addTo(map);
    TruckMarker.bindPopup(`緯度：${TruckCenter[0]}<br>經度：${TruckCenter[1]}`).openPopup();
    
    
    // 機車標籤
    const ScooterCenter = [25.022083808101044, 121.21886640547179];
    const ScooterIcon = L.icon({
        iconUrl: '../static/scooter_icon.png',
        iconSize: [40, 40],
    });
    
    const ScooterMarker = L.marker(ScooterCenter, {
        icon: ScooterIcon,
        opacity: 1.0
    }).addTo(map);
    ScooterMarker.bindPopup(`緯度：${ScooterCenter[0]}<br>經度：${ScooterCenter[1]}`).openPopup();
});