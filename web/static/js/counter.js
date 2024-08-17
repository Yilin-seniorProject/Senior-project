// 自動發送請求設定
function autoFetchData() {
    let targetType = document.getElementById("target_type").value;
    let targetLat = document.getElementById("target_lat").value;
    let targetLng = document.getElementById("target_lng").value;

    // 構建查詢參數的 URL
    let url = `/submit_data?target_type=${encodeURIComponent(targetType)}&target_lat=${encodeURIComponent(targetLat)}&target_lng=${encodeURIComponent(targetLng)}`;

    // 使用 fetch 發送 GET 請求
    fetch(url)
    .then(response => response.json()) // 將回應解析為 JSON 格式
    .then(data => {
        console.log('Success:', data); // 成功後打印回應數據
        // 你可以在這裡添加代碼來更新網頁的顯示
    })
    .catch((error) => {
        console.error('Error:', error); // 如果有錯誤，打印錯誤信息
    });
}

document.addEventListener("DOMContentLoaded", function() {
    // 初始化計數器
    let totalCount = 0;
    let carNum = 0;
    let busNum = 0;
    let truckNum = 0;
    let scooterNum = 0;

    const updateCountDisplay = () => {
        document.getElementById('total_count').value = totalCount;
        document.getElementById('car_count_input').value = carNum;
        document.getElementById('bus_count_input').value = busNum;
        document.getElementById('truck_count_input').value = truckNum;
        document.getElementById('scooter_count_input').value = scooterNum;
    };

    const btnPutMarkers = document.getElementById('put-markers');
    btnPutMarkers.addEventListener('click', () => {
        const vehicleType = document.querySelector('input[name="vehicle-type"]:checked').value;

        // 更新計數器
        totalCount++;
        switch(vehicleType) {
            case 'car':
                carNum++;
                break;
            case 'bus':
                busNum++;
                break;
            case 'truck':
                truckNum++;
                break;
            case 'scooter':
                scooterNum++;
                break;
        }

        // 更新顯示的計數結果
        updateCountDisplay();
    });

    // 設置每5秒自動執行一次請求
    setInterval(autoFetchData, 5000);
});

