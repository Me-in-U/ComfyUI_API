//! 이미지 생성
document.getElementById("uploadForm").addEventListener("submit", function (e) {
  e.preventDefault();

  //! 폼 확인
  let formData = new FormData();
  formData.append("positive_prompt", document.getElementById("positivePrompt").value);
  formData.append("negative_prompt", document.getElementById("negativePrompt").value);

  // 옵션에 따른 formData 설정 및 API URL 변경
  let apiUrl = "http://real.pinkbean.co.kr:1557/human_plus_dress"; // 기본 URL
  if (document.getElementById("optionSelect").value === "prompt_new_dress") {
    apiUrl = "http://real.pinkbean.co.kr:1557/new_dress"; // 변경된 URL
    document.getElementById("original_image").innerHTML = "프롬프트로 이미지가 생성됩니다.";
  } else if (document.getElementById("optionSelect").value === "human_new_dress") {
    formData.append("image", document.getElementById("imageInput").files[0]); // 이미지 데이터 추가
    if (document.getElementById("imageInput").files.length > 0) {
      const reader = new FileReader();
      reader.onload = function (e) {
        document.getElementById("original_image").innerHTML = `<img src="${e.target.result}" alt="Original Image"/>`;
      };
      reader.readAsDataURL(document.getElementById("imageInput").files[0]);
    }
  }

  document.getElementById("result_image").innerHTML = "이미지가 곧 표시됩니다. 새로운 이미지의 경우 최대 2분";

  //! 로딩 텍스트
  let dots = 0;
  let loadingText = "이미지 생성중";
  document.getElementById("loading").style.display = "flex";
  const loadingInterval = setInterval(() => {
    document.getElementById("loadingText").textContent = loadingText + ".".repeat(dots);
    dots = (dots + 1) % 5;
  }, 500);

  //! Flask Post 요청
  fetch(apiUrl, {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Data received:");
      clearInterval(loadingInterval);
      document.getElementById("loading").style.display = "none";
      console.log(data);
      if (data.error) {
        document.getElementById("result_image").innerHTML = "오류가 발생했습니다: " + data.error;
      } else {
        const base64Image = `data:image/jpeg;base64,${data.results[0]}`;
        document.getElementById("result_image").innerHTML = `<img src="${base64Image}" alt="Processed Image"/>`;
      }
    })
    .catch((error) => {
      clearInterval(loadingInterval);
      console.error("Error:", error);
      document.getElementById("loading").style.display = "none";
      document.getElementById("result").innerHTML = "오류가 발생했습니다.";
    });
});

//* function으로 등록 *//
document.addEventListener("DOMContentLoaded", function () {
  setupOptionSelection();
  setupFileSelection();
  setupPromptDefaults();
});

//! optionSelect
function setupOptionSelection() {
  const optionSelect = document.getElementById("optionSelect");
  const imageInputContainer = document.querySelector(".select-image-container");
  optionSelect.addEventListener("change", function () {
    if (this.value === "prompt_new_dress") {
      imageInputContainer.classList.add("hidden"); // 숨김 클래스 추가
      imageInput.required = false; // 필수 입력 필드 해제
    } else {
      imageInputContainer.classList.remove("hidden"); // 숨김 클래스 제거
      imageInput.required = true; // 필수 입력 필드 설정
    }
  });
}

//! 파일 선택
function setupFileSelection() {
  const fileInput = document.getElementById("imageInput");
  const fileBtn = document.getElementById("customFileBtn");
  const fileNameDisplay = document.getElementById("fileName");

  fileBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => {
    fileNameDisplay.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : "선택된 파일 없음";
  });
}

//! 프롬프트 관련
function setupPromptDefaults() {
  configurePrompt("positivePrompt", "useDefaultPositive");
  configurePrompt("negativePrompt", "useDefaultNegative");
}

function configurePrompt(promptId, checkboxId) {
  document.getElementById(checkboxId).addEventListener("change", function () {
    const checkbox = document.getElementById(checkboxId);
    const input = document.getElementById(promptId);
    input.classList.remove("opacity-one");
    input.classList.add("opacity-zero");
    if (checkbox.checked) {
      setTimeout(() => {
        input.value = getDefaultPromptValue(promptId);
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
}

function getDefaultPromptValue(promptId) {
  const prompts = {
    positivePrompt:
      "full body of a woman, elegant floor-length skirt, bride, full body portrait, wedding dress, white clothes, (1 girl:1.5), beautiful and pretty girl, smile, (beautiful wedding dress:1.2), (luxury wedding dress:1.2), (standing:1.2),(empty background: 1.2), (Slim body: 1.2), (Narrow waist: 1.2), (Slim calf: 1.2), (Tall: 1.2), best quality, best shadow, masterpiece, realistic, photo-realistic, realism, finely detail, Super Resolution, super detail, ultra-detailed, ultra high res, RAW photo, detailed cafe, perfect fingers",
    negativePrompt:
      "2d art, 3d art, ((illustration)), anime, cartoon, bad pictures, bad artist, EasyNegative,(worst quality:1.6), (low quality:1.6), (normal quality:1.6), lowres, bad anatomy, bad hands, vaginas in breasts, ((monochrome)), ((grayscale)), collapsed eyeshadow, multiple eyebrow, (cropped), oversaturated, extra limb, missing limbs, deformed hands, long neck, long body, imperfect, (bad hands), signature, watermark, username, artist name, conjoined fingers, deformed fingers, ugly eyes, imperfect eyes, skewed eyes, unnatural face, unnatural body, error, bad image, bad photo",
  };
  return prompts[promptId];
}
