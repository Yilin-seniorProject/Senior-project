// 自動發送請求設定
function autoFetchData() {
    let inputLat = document.getElementById("input_lat").value;
    let inputLng = document.getElementById("input_lng").value;
    
    // 構建查詢參數的 URL
    let url = `/submit_data?input_lat=${encodeURIComponent(inputLat)}&input_lng=${encodeURIComponent(inputLng)}`;
    
    // 使用 fetch 發送 GET 請求
    fetch(url)
    .then(response => response.json()) // 將回應解析為 JSON 格式
    .then(data => {
        console.log('Success:', data); // 成功後打印回應數據
        
        // 自动选择与 imagetype 匹配的 radio 按钮
        const inputType = data.imagetype; // 假設後端回傳的資料格式中包含 input_type 屬性
        if (inputType) {
            const radioButton = document.querySelector(`input[name="vehicle-type"][value="${inputType}"]`);
            if (radioButton) {
                radioButton.checked = true;
            }
        }
    })
    .catch((error) => {
        console.error('Error:', error); // 如果有錯誤，打印錯誤信息
    });
}
let totalCount = 0;
let carNum = 0;
let busNum = 0;
let truckNum = 0;
let scooterNum = 0;

function updateCountDisplay() {
    document.getElementById('total_count').value = totalCount;
    document.getElementById('car_count_input').value = carNum;
    document.getElementById('bus_count_input').value = busNum;
    document.getElementById('truck_count_input').value = truckNum;
    document.getElementById('scooter_count_input').value = scooterNum;
};

document.addEventListener("DOMContentLoaded", function() {
    // 初始化計數器

    
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