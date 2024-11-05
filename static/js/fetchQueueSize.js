// 1초마다 대기열 정보를 가져와 업데이트
function fetchQueueSize() {
	fetch("http://real.pinkbean.co.kr:1557/queue_size")
		.then((response) => {
			if (!response.ok) {
				throw new Error("Failed to fetch queue size");
			}
			return response.json();
		})
		.then((data) => {
			const queueSize = data.exec_info.queue_remaining;
			// console.log(data.exec_info);
			document.getElementById("queueSize").textContent = queueSize;
		})
		.catch((error) => {
			console.error("Error fetching queue size:", error);
		});
}

// 페이지가 로드되면 fetchQueueSize를 1초마다 실행
document.addEventListener("DOMContentLoaded", function () {
	setInterval(fetchQueueSize, 1000);
});
