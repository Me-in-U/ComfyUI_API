let loadingInterval = null;

//* uploadForm submit*//
document.getElementById("uploadForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const optionValue = document.getElementById("optionSelect").value;
  const formData = new FormData();
  configureFormData(optionValue, formData);

  const apiUrl = determineApiUrl(optionValue);
  const originalImage = document.getElementById("original_image");
  const clothesImage = document.getElementById("clothes_image");
  const resultImage = document.getElementById("result_image");
  handleImagePreview(optionValue, originalImage, clothesImage, resultImage);
  loadingInterval = startLoadingAnimation();
  postFormData(apiUrl, formData);
});

//! URL 처리
function determineApiUrl(optionValue) {
  const apiPaths = {
    human_new_dress: "http://real.pinkbean.co.kr:1557/human_plus_dress",
    prompt_new_dress: "http://real.pinkbean.co.kr:1557/new_dress",
    vton_dress: "http://real.pinkbean.co.kr:1557/vton_dress",
  };
  return apiPaths[optionValue];
}

//! 폼 생성
function configureFormData(optionValue, formData) {
  if (optionValue !== "vton_dress") {
    formData.append("positive_prompt", document.getElementById("positivePrompt").value);
    formData.append("negative_prompt", document.getElementById("negativePrompt").value);
  }
  if (["human_new_dress", "vton_dress"].includes(optionValue)) {
    appendImageToFormData(formData, "imageInput1", "image1");
  }
  if (optionValue === "vton_dress") {
    appendImageToFormData(formData, "imageInput1", "image1");
    appendImageToFormData(formData, "imageInput2", "image2");
  }
}

//! 이미지 처리
function appendImageToFormData(formData, inputId, formKey) {
  const fileInput = document.getElementById(inputId);
  if (fileInput.files.length > 0) {
    formData.append(formKey, fileInput.files[0]);
  }
}
function handleImagePreview(optionValue, originalImage, clothesImage, resultImage) {
  if (optionValue === "human_new_dress") {
    loadImagePreview("imageInput1", originalImage);
  } else if (optionValue === "prompt_new_dress") {
    originalImage.innerHTML = "프롬프트로 이미지가 생성됩니다.";
  } else if (optionValue === "vton_dress") {
    loadImagePreview("imageInput1", originalImage);
    loadImagePreview("imageInput2", clothesImage);
  }
  resultImage.innerHTML = "이미지가 곧 표시됩니다. 새로운 이미지의 경우 최대 2분";
}
function loadImagePreview(inputId, container, alt) {
  const fileInput = document.getElementById(inputId);
  if (fileInput.files.length > 0) {
    const reader = new FileReader();
    reader.onload = function (e) {
      container.innerHTML = `<img src="${e.target.result}" alt="Original Image"/>`;
    };
    reader.readAsDataURL(fileInput.files[0]);
  }
}

//! 로딩 애니메이션
function startLoadingAnimation() {
  let dots = 0;
  const loadingText = "이미지 생성중";
  document.getElementById("loading").style.display = "flex";
  const loadingInterval = setInterval(() => {
    document.getElementById("loadingText").textContent = loadingText + ".".repeat(dots);
    dots = (dots + 1) % 5;
  }, 500);
  return loadingInterval;
}

//! fetch Post
function postFormData(apiUrl, formData) {
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
      handleResponse(data);
    })
    .catch((error) => {
      handleError(error);
    });
}

//! then(data => handle)
function handleResponse(data) {
  clearInterval(loadingInterval);
  document.getElementById("loading").style.display = "none";
  if (data.error) {
    document.getElementById("result_image").innerHTML = "오류가 발생했습니다: " + data.error;
  } else {
    const base64Image = `data:image/jpeg;base64,${data.results[0]}`;
    document.getElementById("result_image").innerHTML = `<img src="${base64Image}" alt="Processed Image"/>`;
  }
}

//! then(error => handle)
function handleError(error) {
  clearInterval(loadingInterval);
  console.error("Error:", error);
  document.getElementById("loading").style.display = "none";
  document.getElementById("result").innerHTML = "오류가 발생했습니다.";
}

//* DOMContentLoaded *//
document.addEventListener("DOMContentLoaded", function () {
  setupOptionSelection();
  setupFileSelection();
  setupPromptDefaults();
});

//! optionSelect
function setupOptionSelection() {
  const optionSelect = document.getElementById("optionSelect");
  const imageInputContainer1 = document.getElementById("select-image-container1");
  const imageInputContainer2 = document.getElementById("select-image-container2");
  const promptContainer1 = document.getElementById("positivePrompt-container");
  const promptContainer2 = document.getElementById("negativePrompt-container");
  const clothesImagePreview = document.getElementById("clothes_image");
  const imageInput1 = document.getElementById("imageInput1");
  const imageInput2 = document.getElementById("imageInput2");
  const positivePromptText = document.getElementById("positivePrompt");
  const negativePromptText = document.getElementById("negativePrompt");

  optionSelect.addEventListener("change", function () {
    const isHumanNewDress = this.value === "human_new_dress";
    const isPromptNewDress = this.value === "prompt_new_dress";
    const isVtonDress = this.value === "vton_dress";

    // 이미지 입력 컨테이너
    imageInputContainer1.classList.toggle("hidden", !isHumanNewDress && !isVtonDress);
    imageInputContainer2.classList.toggle("hidden", !isVtonDress);
    clothesImagePreview.style.display = isVtonDress ? "block" : "none";

    // 프롬프트 컨테이너
    promptContainer1.classList.toggle("hidden", isVtonDress);
    promptContainer2.classList.toggle("hidden", isVtonDress);

    // 입력 필드의 필수 설정
    imageInput1.required = isHumanNewDress || isVtonDress;
    imageInput2.required = isVtonDress;
    positivePromptText.required = isHumanNewDress || isPromptNewDress;
    negativePromptText.required = isHumanNewDress || isPromptNewDress;
  });
}

//! 파일 선택
function setupFileSelection() {
  setupFileInput("imageInput1", "customFileBtn1", "fileName1");
  setupFileInput("imageInput2", "customFileBtn2", "fileName2");
}

function setupFileInput(inputId, buttonId, displayId) {
  const fileInput = document.getElementById(inputId);
  const fileButton = document.getElementById(buttonId);
  const fileNameDisplay = document.getElementById(displayId);

  fileButton.addEventListener("click", () => fileInput.click());
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
