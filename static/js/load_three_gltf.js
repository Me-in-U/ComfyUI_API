// 페이지가 로드되면 실행될 함수

import * as THREE from "three";
import { GLTFLoader } from "GLTFLoader";

console.log(THREE);
console.log(GLTFLoader);

window.addEventListener("load", init);

function init() {
	// canvas 엘리먼트 생성
	const canvas = document.createElement("canvas");
	const container = document.getElementById("three-container"); // div 요소 선택

	// WebGLRenderer 생성 및 설정
	const renderer = new THREE.WebGLRenderer({ canvas });
	renderer.setSize(container.clientWidth, container.clientHeight);
	container.appendChild(renderer.domElement); // div에 렌더러의 캔버스 추가

	// 씬(Scene) 생성
	const scene = new THREE.Scene();
	scene.background = new THREE.Color(0xaaaaaa);
	// 카메라(Camera) 생성 (원근 투영 카메라)
	const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

	//조명
	const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
	scene.add(ambientLight);

	let loadedMesh;
	const gltfLoader = new GLTFLoader();
	gltfLoader.load(
		"/static/models/1.gltf",
		(gltf) => {
			const meshFile = gltf.scene.children[0];
			scene.add(meshFile);
			loadedMesh = meshFile;
			// 모델의 바운딩 박스 계산
			const box = new THREE.Box3().setFromObject(meshFile);
			const center = box.getCenter(new THREE.Vector3());
			const size = box.getSize(new THREE.Vector3());

			// 카메라 위치 조정
			const maxDim = Math.max(size.x, size.y, size.z);
			const fov = camera.fov * (Math.PI / 180);
			let cameraZ = Math.abs((maxDim / 2) * Math.tan(fov / 2)); // 카메라 위치 조정 로직 변경

			// 카메라 종횡비 업데이트
			camera.aspect = container.clientWidth / container.clientHeight;
			camera.updateProjectionMatrix();
			cameraZ *= 3; // 카메라 거리를 모델 크기의 3배로 설정
			camera.position.z = cameraZ;

			const cameraY = center.y;
			camera.position.y = cameraY;

			// 카메라가 모델 중심을 바라보도록 설정
			camera.lookAt(center);

			//조명
			const directionalLight1 = new THREE.DirectionalLight(0x11ffff, 0.75);
			directionalLight1.position.set(10, 10, 10); // 좀 더 넓은 각도에서 조명을 제공
			scene.add(directionalLight1);

			const directionalLight2 = new THREE.DirectionalLight(0xff11ff, 0.75);
			directionalLight2.position.set(-10, 10, -10); // 반대 방향에서도 조명 추가
			scene.add(directionalLight2);

			const pointLight = new THREE.PointLight(0x11ff11, 1, 100);
			pointLight.position.set(25, 10, 25); // 객체 측면에 포인트 라이트 추가
			scene.add(pointLight);
		},
		(xhr) => {
			// 진행 상태 콜백
			console.log(`Model load progress: ${((xhr.loaded / xhr.total) * 100).toFixed(2)}% loaded`);
		},
		(error) => {
			// 오류 콜백
			console.error("An error happened during loading the model:", error);
		}
	);
	function animate() {
		requestAnimationFrame(animate);
		if (loadedMesh) {
			// 모델이 로드된 경우에만 회전
			loadedMesh.rotation.x += 0.01;
			loadedMesh.rotation.y += 0.01; // 모델을 y축 주변으로 회전
		}

		renderer.render(scene, camera);
	}

	animate();
}

//! 3d 모델 크기 관련
function adjustAspectRatio() {
	const container = document.querySelector(".container"); // 상위 컨테이너 선택
	if (container) {
		const containerWidth = container.clientWidth; // 컨테이너의 현재 너비 가져오기
		const aspectHeight = (containerWidth * 9) / 16; // 16:9 비율로 높이 계산
		const threeContainer = document.getElementById("three-container");
		threeContainer.style.height = `${aspectHeight}px`; // 계산된 높이를 적용
	}
}

// 페이지 로드 시 및 창 크기 변경 시에 함수 실행
window.addEventListener("load", adjustAspectRatio);
window.addEventListener("resize", adjustAspectRatio);
