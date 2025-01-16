import { put_icon } from './putIcon.js';
import { autoFetchData } from './pullRequest.js';
export let map;
export var counter = {
    totalCount: 0,
    carNum: 0,
    taxiNum: 0,
    scooterNum: 0
};

document.addEventListener("DOMContentLoaded", function () {
    // *** 放置地圖
    let zoom = 18; // 縮放程度，間距為 0 - 18
    let center = [25.019448151190158, 121.21634240643077]; // 中心點座標：橫山書法藝術公園
    map = L.map('map').setView(center, zoom); // 使用新添加的map元素

    // 設定地圖的圖層
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap', // 商用時必須要有版權出處
        zoomControl: true, // 是否秀出 - + 按鈕
    }).addTo(map);

    let interval = setInterval(autoFetchData, 5000);

    // 手動新增圖標
    const btnPutMarkers = document.getElementById('put-markers');
    btnPutMarkers.addEventListener('click', e => {
        const latitude = parseFloat(document.getElementById('input_lat').value);
        const longitude = parseFloat(document.getElementById('input_lng').value);
        const vehicleType = document.querySelector('input[name="vehicle-type"]:checked').value;
        e.preventDefault();
        put_icon(map, latitude, longitude, vehicleType);
    });

    // 獲取相關元素
    const thumbnailImg = document.getElementById("target_img");
    const popup = document.getElementById("popup");
    const popupImg = document.getElementById("popup_img");
    const closePopup = document.getElementById("close_popup");

    // 當點擊缩圖時，顯示懸浮視窗
    thumbnailImg.addEventListener("click", function () {
        popup.style.display = "block"; // 顯示懸浮視窗
    });

    // 當點擊關閉按钮时，隐藏懸浮視窗
    closePopup.addEventListener("click", function () {
        popup.style.display = "none"; // 隱藏懸浮視窗
    });

    // 當點擊懸浮視窗外部區域时，隱藏窗口
    window.addEventListener("click", function (event) {
        if (event.target === popup) {
            popup.style.display = "none";
        }
    });
});