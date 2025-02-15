import { imgRequest } from './pullRequest.js';
import { counter } from './osm.js';
export let pinList = [];


function updateCountDisplay() {
    const fields = [
        { key: 'totalCount', id: 'total_amount' },
        { key: 'legal_carNum', id: 'legal_car_amount' },
        { key: 'legal_scooterNum', id: 'legal_scooter_amount' },
        { key: 'illegal_carNum', id: 'illegal_car_amount' },
        { key: 'illegal_scooterNum', id: 'illegal_scooter_amount' },
    ];

    fields.forEach(field => {
        document.getElementById(field.id).innerHTML = counter[field.key];
    });
};

export function put_icon(map, latitude, longitude, targetType) {
    // 自定義圖標：汽車、機車、其他(以計程車表示)
    const CarIcon = L.icon({
        iconUrl: '../static/img/car_icon.png',
        iconSize: [40, 40],
    });
    const ScooterIcon = L.icon({
        iconUrl: '../static/img/scooter_icon.png',
        iconSize: [40, 40],
    });
    const TaxiIcon = L.icon({
        iconUrl: '../static/img/taxi_icon.png',
        iconSize: [40, 40],
    });
    
    // 根據訊號類型選擇圖標
    let selectedIcon;
    switch (targetType) {
        case 'car': // car
        selectedIcon = CarIcon;
        counter.legal_carNum++;
        break;
        case 'motorcycle': // scooter
        selectedIcon = ScooterIcon;
        counter.legal_scooterNum++;
        break;
        default:
            selectedIcon = TaxiIcon; // 默認圖標
        }
        
        // 更新計數器
        counter.totalCount = counter.legal_carNum + counter.legal_scooterNum + 
        counter.illegal_carNum + counter.illegal_scooterNum;
        
        // 放置標記
        if (!isNaN(latitude) && !isNaN(longitude)) {
            const markerId = pinList.length + 1;
            const marker = L.marker([latitude, longitude], { icon: selectedIcon }).addTo(map);
            pinList.push({ marker, markerId });
            // TODO 違規判斷式與記數
            // if  (data.violation) {
            //     counter.illegal_carNum++;
            // 當標記被點擊時，顯示車輛的資訊
            marker.on('click', () => {
                if(targetType == 'car') {
                    document.getElementById('target_type').innerHTML = "車輛類別： 車子 Car";
                } else if(targetType == 'motorcycle') {
                    document.getElementById('target_type').innerHTML = "車輛類別： 機車 Motorcycle";
            }
            document.getElementById('target_position').innerHTML = "目標車輛位置：<br>(" + latitude + ", " + longitude + ")";
            imgRequest(markerId);
        });
    } else {
        alert('Please enter valid latitude and longitude.');
    }
    // 更新顯示的計數結果
    updateCountDisplay();
}