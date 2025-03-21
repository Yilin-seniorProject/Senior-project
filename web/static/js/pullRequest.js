import { put_icon } from './putIcon.js';
import { map } from './osm.js'
export let id = 0;

// 自動發送請求設定
export function autoFetchData() {
    let url = `/update_data?`;
    fetch(url)
        .then(response => response.json()) // 將回應 body(type:json) 解析為 promise object
        .then(data => {
            while (id < data.length) {
                const element = data[id];
                put_icon(map, element['Latitude'], element['Longitude'], element['target_type'], element['message']);
                id++;
            }
        })
        .catch((error) => {
            console.error('Error:', error); // 如果有錯誤，打印錯誤信息
        });
}

// 請求照片設定
export function imgRequest(markerId) {
    // 構建查詢參數的 URL，傳遞 Marker ID
    let url = `/submit_data?marker_id=${encodeURIComponent(markerId)}`;

    // 使用 fetch 發送 GET 請求
    fetch(url)
        .then(response => response.json()) // 將回應解析為 JSON 格式
        .then(data => {
            console.log('Success:', data); // 成功後打印回應數據
            if (data.image_path) {
                document.getElementById("target_img").src = data.image_path;
                document.getElementById("popup_img").src = data.image_path;
                document.getElementById("drone_alt").innerHTML = "無人機拍攝高度： " + data.drone_info[2] + " 公尺";
                // TODO 違規判斷式與記數
                if (data.message[0]) {
                    document.getElementById("violation").innerHTML = "車輛是否違規： 是 Yes";
                } else {
                    document.getElementById("violation").innerHTML = "車輛是否違規： 否 No";
                }
                console.log('Image changed.');
            }
        })
        .catch((error) => {
            console.error('Error:', error); // 如果有錯誤，打印錯誤信息
        });
}
