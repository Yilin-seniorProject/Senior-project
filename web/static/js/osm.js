const markerList = [];
let id = 0;
let map;

// 自動發送請求設定
function autoFetchData() {
    let url = `/update_data?`;
    fetch(url)
        .then(response => response.json()) // 將回應 body(type:json) 解析為 promise object
        .then(data => {
            while (id < data.length) {
                const element = data[id];
                console.log(element['ImageName']);
                console.log(element['ImageType']);
                console.log(element['Latitude']);
                console.log(element['Longitude']);
                logo(map, element['Latitude'], element['Longitude'], element['ImageType'])
                id++;
            }
        })
        .catch((error) => {
            console.error('Error:', error); // 如果有錯誤，打印錯誤信息
        });

}

// 請求照片設定
function imgRequest(markerId) {
    // 構建查詢參數的 URL，傳遞 Marker ID
    let url = `/submit_data?marker_id=${encodeURIComponent(markerId)}`;

    // 使用 fetch 發送 GET 請求
    fetch(url)
        .then(response => response.json()) // 將回應解析為 JSON 格式
        .then(data => {
            console.log('Success:', data); // 成功後打印回應數據
            // console.log(`Marker ID: ${markerId}\nType: ${vehicleType}\nLocation: ${latitude}, ${longitude}`)
            // 假設後端返回的 data 中包含圖片的 URL
            if (data.img_url) {
                document.getElementById("target_img").src = data.img_url;
            }
        })
        .catch((error) => {
            console.error('Error:', error); // 如果有錯誤，打印錯誤信息
        });
}

function logo(map, latitude, longitude, vehicleType) {
    // 自定義圖標：汽車、公車、卡車、機車
    const CarIcon = L.icon({
        iconUrl: '../static/img/car_icon.png',
        iconSize: [40, 40],
    });
    const TaxiIcon = L.icon({
        iconUrl: '../static/img/taxi_icon.png',
        iconSize: [40, 40],
    });
    const ScooterIcon = L.icon({
        iconUrl: '../static/img/scooter_icon.png',
        iconSize: [40, 40],
    });

    // 根據訊號類型選擇圖標
    let selectedIcon;
    switch (vehicleType) {
        case 'car':
            selectedIcon = CarIcon;
            break;
        case 'taxi':
            selectedIcon = TaxiIcon;
            break;
        case 'scooter':
            selectedIcon = ScooterIcon;
            break;
        default:
            selectedIcon = CarIcon; // 默認圖標
    }

    // 放置標記
    if (!isNaN(latitude) && !isNaN(longitude)) {
        const markerId = markerList.length + 1;
        const marker = L.marker([latitude, longitude], { icon: selectedIcon }).addTo(map);
        markerList.push({ marker, markerId });
        // 當標記被點擊時，顯示車輛的資訊
        marker.on('click', () => {
            document.getElementById('target_type').value = vehicleType;
            document.getElementById('target_lng').value = longitude;
            document.getElementById('target_lat').value = latitude;
            imgRequest(markerId);
        });
    } else {
        alert('Please enter valid latitude and longitude.');
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // *** 放置地圖
    let zoom = 17; // 縮放程度，間距為 0 - 18
    let center = [25.019448151190158, 121.21634240643077]; // 中心點座標：橫山書法藝術公園
    map = L.map('map').setView(center, zoom); // 使用新添加的map元素

    // 設定地圖的圖層
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap', // 商用時必須要有版權出處
        zoomControl: true, // 是否秀出 - + 按鈕
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

    interval = setInterval(autoFetchData, 5000);

    const btnPutMarkers = document.getElementById('put-markers');
    btnPutMarkers.addEventListener('click', e => {
        const latitude = parseFloat(document.getElementById('input_lat').value);
        const longitude = parseFloat(document.getElementById('input_lng').value);
        const vehicleType = document.querySelector('input[name="vehicle-type"]:checked').value;
        e.preventDefault();
        logo(map, latitude, longitude, vehicleType);
    });

    // 獲取相關元素
    const thumbnailImg = document.getElementById("target_img");
    const popup = document.getElementById("popup");
    const popupImg = document.getElementById("popup_img");
    const closePopup = document.getElementById("close_popup");

    // 当点击缩略图时，顯示懸浮視窗
    thumbnailImg.addEventListener("click", function () {
        popup.style.display = "block"; // 顯示懸浮視窗
    });

    // 当点击关闭按钮时，隐藏懸浮視窗
    closePopup.addEventListener("click", function () {
        popup.style.display = "none"; // 隱藏懸浮視窗
    });

    // 当点击懸浮視窗外部區域时，隱藏窗口
    window.addEventListener("click", function (event) {
        if (event.target === popup) {
            popup.style.display = "none";
        }
    });
});