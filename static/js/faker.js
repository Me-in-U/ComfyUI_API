function glitch(element) {
	let count = 0;
	let interval1 = 15;
	let interval2 = 30;
	setInterval(() => {
		// element
		const skew = Math.random() * 20 - 10;
		// element::before
		const top1 = Math.random() * 100;
		const btm1 = Math.random() * 100;
		// element::after
		const top2 = Math.random() * 100;
		const btm2 = Math.random() * 100;

		element.style.setProperty("--skew", `${skew}deg`);
		element.style.setProperty("--t1", `${top1}%`);
		element.style.setProperty("--b1", `${btm1}%`);
		element.style.setProperty("--t2", `${top2}%`);
		element.style.setProperty("--b2", `${btm2}%`);
		element.style.setProperty("--scale", `1`);

		count++;

		if (count % interval1 === 0) {
			interval1 = 10 + Math.floor(Math.random() * 11);
			const bigSkew = Math.random() * 180 - 90;
			element.style.setProperty("--skew", `${bigSkew}deg`);
		}

		if (count % interval2 === 0) {
			interval2 = 20 + Math.floor(Math.random() * 11);
			const bigScale = 1 + Math.random() / 2;
			element.style.setProperty("--scale", `${bigScale}`);
		}
	}, 100);
}

const h1 = document.querySelector("h1");
glitch(h1);
let mouseDownTime;

document.body.addEventListener("mousedown", function (event) {
	mouseDownTime = new Date(); // 마우스를 누르기 시작한 시간 기록
});
document.body.addEventListener("mouseup", function (event) {
	const mouseUpTime = new Date(); // 마우스를 떼는 시간 기록
	const clickDuration = (mouseUpTime - mouseDownTime) / 1000; // 클릭 지속 시간 계산

	let fontSize;
	if (clickDuration < 2) {
		fontSize = 5 + (clickDuration / 2) * 5; // 2초 미만 지속 시, 비례하여 크기 계산
	} else {
		fontSize = 10; // 2초 이상 지속 시, 최대 크기 10vw
	}
	fontSize = `${fontSize}vw`;

	const newH1 = document.createElement("h1");
	newH1.setAttribute("data-text", "증명하세요");
	newH1.textContent = "증명하세요";
	newH1.style.position = "absolute";
	newH1.style.left = `${event.clientX}px`;
	newH1.style.top = `${event.clientY}px`;
	newH1.style.transform = "translate(-12.3vw, -6vw)";
	newH1.style.fontSize = fontSize;
	newH1.style.color = "#f1f1f1";
	newH1.style.zIndex = "1000";

	document.body.appendChild(newH1);

	glitch(newH1); // glitch 효과 적용

	setTimeout(() => {
		newH1.remove();
	}, 1000); // 1초 후에 텍스트 제거
});
