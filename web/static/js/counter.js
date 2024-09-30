let totalCount = 0;
let carNum = 0;
let busNum = 0;
let truckNum = 0;
let scooterNum = 0;

function updateCountDisplay() {
    document.getElementById('total_count').value = totalCount;
    document.getElementById('car_count_input').value = carNum;
    //document.getElementById('bus_count_input').value = busNum;
    //document.getElementById('truck_count_input').value = truckNum;
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
});