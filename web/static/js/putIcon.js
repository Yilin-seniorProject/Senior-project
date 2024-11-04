import { imgRequest } from './pullRequest.js';
import { counter } from './osm.js';
export let markerList = [];


function updateCountDisplay() {
    document.getElementById('total_count').value = counter.totalCount;
    document.getElementById('car_count_input').value = counter.carNum;
    document.getElementById('taxi_count_input').value = counter.taxiNum;    
    document.getElementById('scooter_count_input').value = counter.scooterNum;
};

export function put_icon(map, latitude, longitude, vehicleType) {
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

    // 更新計數器
    counter.totalCount++;
    // 根據訊號類型選擇圖標
    let selectedIcon;
    switch (vehicleType) {
        case 'car':
            selectedIcon = CarIcon;
            counter.carNum++;
            break;
        case 'taxi':
            selectedIcon = TaxiIcon;
            counter.taxiNum++
            break;
        case 'scooter':
            selectedIcon = ScooterIcon;
            counter.scooterNum++;
            break;
        default:
            selectedIcon = CarIcon; // 默認圖標
            counter.carNum++;
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
    // 更新顯示的計數結果
    updateCountDisplay();
}