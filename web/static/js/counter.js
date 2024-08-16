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
    postRequest();
    
});

function postRequest(){
    let targetType = document.getElementById("target_type").value;
    let targetLat = document.getElementById("target_lat").value;
    let targetImg = document.getElementById("target_img").value;
    let targetLng = document.getElementById("target_lng").value;
    
    // 構建要發送的數據
    const data = {
        target_type: targetType,
        target_lat: targetLat,
        target_lng: targetLng,
        target_img: targetImg
    };

    // 使用 fetch 發送 POST 請求
    fetch('/submit_data', {
        method: 'POST', // 使用 POST 方法
        headers: {
            'Content-Type': 'application/json' // 告訴伺服器發送的是 JSON 格式的數據
        },
        body: JSON.stringify(data) // 將數據轉換為 JSON 字符串並發送
    })
    .then(response => response.json()) // 將回應解析為 JSON 格式
    .then(data => {
        console.log('Success:', data); // 成功後打印回應數據
    })
    .catch((error) => {
        console.error('Error:', error); // 如果有錯誤，打印錯誤信息
    });
}