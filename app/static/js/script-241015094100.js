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

    //프롬프트 초기화
    const input1 = document.getElementById("positivePrompt");
    const input2 = document.getElementById("negativePrompt");
    input1.value = "";
    input2.value = "";

    const checkbox1 = document.getElementById("useDefaultPositive");
    const checkbox2 = document.getElementById("useDefaultNegative");
    checkbox1.checked = false;
    checkbox2.checked = false;
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
    const optionValue = document.getElementById("optionSelect").value;
    input.classList.remove("opacity-one");
    input.classList.add("opacity-zero");
    if (checkbox.checked) {
      setTimeout(() => {
        input.value = optionValue === "human_new_dress" ? getDefaultPromptValue1(promptId) : getDefaultPromptValue2(promptId);
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

function getDefaultPromptValue1(promptId) {
  const prompts = {
    positivePrompt:
      "(white dress:1.2), (luxury wedding dress:1.3), bride,long dress,elegant floor-length skirt,(korean1.2), Best Quality, (Masterpiece:1.4), (Realism:1.2), (Realisitc:1.2), 4K,(photorealistic:1.3), Detailed, 1 girl, beautiful and pretty girl, (black background: 1.3), photo-realistic, realism, finely detail, Super Resolution, super detail, ultra-detailed, ultra high res, RAW photo, detailed cafe, perfect fingers, beautiful face, beautiful detailed eyes, symmetric eyes",
    negativePrompt:
      "(black clothes:1.5), (black dress:1.5), (black accessories), text, paintings,sketches,worst quality,low quality,easynegative,lowres,bad hands,bad anatomy,poorly drawn hands,poorly drawn face, extra digit,fewer digits,signature,blurry, bad feet, fused girls, username,duplicate,morbid,mutilated, mutated hands,mutation, deformed, bad proportions, malformed limbs, extra limbs, disfigured, gross proportions,disfigured, bad art, deformed,plump, bad anatomy, error, watermark,long neck, long torso, bad feet, pubic hair, extra digit bad legs,missing legs,missing arms, bad anatomy, wrong finger,missing fingers,big breasts,huge breasts,large breasts,bad hands, extra arms,extra hands,ugly face,cloned face, deformed face,malformed face, extra head,badhandv4,multiple view, multiple views,bad_pictures,logo,",
  };
  return prompts[promptId];
}

function getDefaultPromptValue2(promptId) {
  const prompts = {
    positivePrompt:
      "Best Quality, (Masterpiece:1.4), (Realism:1.2), (Realisitc:1.2), 4K,(photorealistic:1.3), Detailed,elegant floor-length skirt,long dress, bride, (white dress:1.4), korean, 1 girl, beautiful and pretty girl, (luxury wedding dress:1.3), (black background: 1.4), photo-realistic, realism, finely detail, Super Resolution, super detail, ultra-detailed, ultra high res, RAW photo, detailed cafe, perfect fingers, beautiful face, beautiful detailed eyes, symmetric eyes",
    negativePrompt:
      "(black color dress:1.5),black color accessories,Paintings,sketches, (worst quality, low quality, normal quality:1.7),lowres, blurry, text, logo, ((monochrome)), ((grayscale)), easynegative, badhandv, , wrong finger, lowres, bad anatomy, bad handsmissing fingers,extra digit ,fewer digits,signature,watermark, username, blurry, bad feet, fused girls, fushion, signature, watermark, username, blurry, (bad feet:1.1),, monochrome, duplicate, morbid, mutilated, long neck, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, bad proportions, malformed limbs, extra limbs, cloned face, disfigured, gross proportions, (missing arms:1.331), (missing legs:1.331), (extra arms:1.331), (extra legs:1.331), plump, bad legs, bad anatomy, bad hands, text, error, missing fingers,watermark, username, blurry, long body, bad anatomy, bad hands, missing fingers, pubic hair,extra digit, fewer digits, bad anatomy, bad hands, missing fingers, signature, watermark, username, blurry,huge breasts,Large Breasts,kid,children,extra hands,extra arms((disfigured)), ((bad art)), ((deformed)),ugly face,umbrella,deformed face,malformed face,extra head, easynegative, badhandv4,Big Breasts,multiple girls, multiple view,Big Breasts,multiple girls, multiple views,Long Necks,Long Torso,  bad_pictures",
  };
  return prompts[promptId];
}
