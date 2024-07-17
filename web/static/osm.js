document.addEventListener("DOMContentLoaded", function() {
    // *** 放置地圖
    let zoom = 17; // 0 - 18
    let center = [25.019448151190158, 121.21634240643077]; // 中心點座標：橫山書法藝術公園
    let map = L.map('map').setView(center, zoom); // 使用新添加的map元素
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap', // 商用時必須要有版權出處
        zoomControl: true , // 是否秀出 - + 按鈕
    }).addTo(map);
});
