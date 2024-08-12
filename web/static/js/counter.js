document.addEventListener("DOMContentLoaded", function() {
    // 初始化計數器
    let totalCount = 0;
    let carCount = 0;
    let busCount = 0;
    let truckCount = 0;
    let scooterCount = 0;

    const updateCountDisplay = () => {
        document.querySelector('#car_count input:nth-child(2)').value = totalCount;
        document.querySelector('#car_count input:nth-child(5)').value = carCount;
        document.querySelector('#car_count input:nth-child(8)').value = busCount;
        document.querySelector('#car_count input:nth-child(11)').value = truckCount;
        document.querySelector('#car_count input:nth-child(14)').value = scooterCount;
    };

    const btnPutMarkers = document.getElementById('put-markers');
    btnPutMarkers.addEventListener('click', () => {
        const vehicleType = document.querySelector('input[name="vehicle-type"]:checked').value;

        // 更新計數器
        totalCount++;
        switch(vehicleType) {
            case 'car':
                carCount++;
                break;
            case 'bus':
                busCount++;
                break;
            case 'truck':
                truckCount++;
                break;
            case 'scooter':
                scooterCount++;
                break;
        }

        // 更新顯示的計數結果
        updateCountDisplay();
    });
});
