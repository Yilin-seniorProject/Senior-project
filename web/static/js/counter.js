document.addEventListener("DOMContentLoaded", function() {
    // 初始化計數器
    let totalCount = 0;
    let carNum = 0;
    let busNum = 0;
    let truckNum = 0;
    let scooterNum = 0;

    const updateCountDisplay = () => {
        document.querySelector('#car_count input:nth-child(2)').value = totalCount;
        document.querySelector('#car_count input:nth-child(5)').value = carNum;
        document.querySelector('#car_count input:nth-child(8)').value = busNum;
        document.querySelector('#car_count input:nth-child(11)').value = truckNum;
        document.querySelector('#car_count input:nth-child(14)').value = scooterNum;
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
});
