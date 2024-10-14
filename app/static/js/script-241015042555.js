document.getElementById("uploadForm").addEventListener("submit", function (e) {
  e.preventDefault();

  let formData = new FormData();
  formData.append("image", document.getElementById("imageInput").files[0]);
  formData.append("positive_prompt", document.getElementById("positivePrompt").value);
  formData.append("negative_prompt", document.getElementById("negativePrompt").value);

  if (document.getElementById("imageInput").files.length > 0) {
    const reader = new FileReader();
    reader.onload = function (e) {
      document.getElementById("originalImageContainer").innerHTML = `<img src="${e.target.result}" alt="Original Image"/>`;
    };
    reader.readAsDataURL(document.getElementById("imageInput").files[0]);
  }

  document.getElementById("result").innerHTML = "이미지가 곧 표시됩니다. 새로운 이미지의 경우 최대 2분";

  //! 로딩 텍스트
  let dots = 0;
  let loadingText = "로딩중";
  document.getElementById("loading").style.display = "flex";
  const loadingInterval = setInterval(() => {
    document.getElementById("loadingText").textContent = loadingText + ".".repeat(dots);
    dots = (dots + 1) % 5;
  }, 500);

  //! Flask Post 요청- "http://real.pinkbean.co.kr:5000/ComfyUI_API/mainFlask.py"
  fetch("http://real.pinkbean.co.kr:1557/human_plus_dress", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json(); // 응답을 JSON으로 파싱
    })
    .then((data) => {
      console.log("Data received:");
      clearInterval(loadingInterval);
      document.getElementById("loading").style.display = "none";
      console.log(data);
      if (data.error) {
        document.getElementById("result").innerHTML = "오류가 발생했습니다: " + data.error;
      } else {
        const base64Image = `data:image/jpeg;base64,${data.results[0]}`;
        document.getElementById("result").innerHTML = `<img src="${base64Image}" alt="Processed Image"/>`;
      }
    })
    .catch((error) => {
      clearInterval(loadingInterval);
      console.error("Error:", error);
      document.getElementById("loading").style.display = "none";
      document.getElementById("result").innerHTML = "오류가 발생했습니다.";
    });
});

//! 파일 선택
document.getElementById("customFileBtn").addEventListener("touchstart", function () {
  document.getElementById("imageInput").click();
});

document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("imageInput");
  const fileBtn = document.getElementById("customFileBtn");
  const fileNameDisplay = document.getElementById("fileName");

  fileBtn.addEventListener("click", function () {
    fileInput.click(); // 실제 파일 입력 필드를 트리거합니다.
  });

  fileInput.addEventListener("change", function () {
    fileNameDisplay.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : "선택된 파일 없음";
  });
});

document.addEventListener("DOMContentLoaded", function () {
  //!Positive Prompt 기본 설정
  document.getElementById("useDefaultPositive").addEventListener("change", function () {
    const checkbox = this;
    const input = document.getElementById("positivePrompt");
    input.classList.remove("opacity-one");
    input.classList.add("opacity-zero");
    if (checkbox.checked) {
      setTimeout(() => {
        input.value =
          "full body of a woman, elegant floor-length skirt, bride, full body portrait, wedding dress, white clothes, (1 girl:1.5), beautiful and pretty girl, smile, (beautiful wedding dress:1.2), (luxury wedding dress:1.2), (standing:1.2),(empty background: 1.2), (Slim body: 1.2), (Narrow waist: 1.2), (Slim calf: 1.2), (Tall: 1.2), best quality, best shadow, masterpiece, realistic, photo-realistic, realism, finely detail, Super Resolution, super detail, ultra-detailed, ultra high res, RAW photo, detailed cafe, perfect fingers";
        input.classList.remove("opacity-zero");
        input.classList.add("opacity-one");
      }, 300);
      input.disabled = true;
    } else {
      setTimeout(() => {
        input.value = "";
        input.disabled = false;
        input.classList.remove("opacity-zero");
        input.classList.add("opacity-one");
      }, 300);
    }
  });

  //!Negative Prompt 기본 설정
  document.getElementById("useDefaultNegative").addEventListener("change", function () {
    const checkbox = this;
    const input = document.getElementById("negativePrompt");
    input.classList.remove("opacity-one");
    input.classList.add("opacity-zero");
    if (checkbox.checked) {
      setTimeout(() => {
        input.value =
          "2d art, 3d art, ((illustration)), anime, cartoon, bad pictures, bad artist, EasyNegative,(worst quality:1.6), (low quality:1.6), (normal quality:1.6), lowres, bad anatomy, bad hands, vaginas in breasts, ((monochrome)), ((grayscale)), collapsed eyeshadow, multiple eyebrow, (cropped), oversaturated, extra limb, missing limbs, deformed hands, long neck, long body, imperfect, (bad hands), signature, watermark, username, artist name, conjoined fingers, deformed fingers, ugly eyes, imperfect eyes, skewed eyes, unnatural face, unnatural body, error, bad image, bad photo";
        input.classList.remove("opacity-zero");
        input.classList.add("opacity-one");
      }, 300);
      input.disabled = true;
    } else {
      setTimeout(() => {
        input.value = "";
        input.disabled = false;
        input.classList.remove("opacity-zero");
        input.classList.add("opacity-one");
      }, 300);
    }
  });
});
