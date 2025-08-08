document.addEventListener("DOMContentLoaded", () => {
  const input   = document.getElementById("id_images");   // 다중 이미지 업로드 input
  const preview = document.getElementById("preview-box"); // 썸네일 영역
  const btn     = document.getElementById("analyzeBtn");  // “분석 요청하기” 버튼
  const spinner = document.getElementById("spinner");     // 버튼 안 스피너

  // 필수 요소가 하나라도 없으면 실행 중단 (다른 페이지 안전)
  if (!input || !preview || !btn || !spinner) return;

  /* -------- 1) 이미지 미리보기 -------- */
  input.addEventListener("change", (e) => {
    preview.innerHTML = "";                              // 기존 썸네일 초기화

    [...e.target.files].forEach((file) => {
      if (!file.type.startsWith("image/")) return;       // 이미지만 처리

      const reader = new FileReader();
      reader.onload = (evt) => {
        const img = document.createElement("img");
        img.src = evt.target.result;                     // base64 데이터 URL
        img.className = "img-thumbnail me-2 mb-2";
        img.style.maxWidth  = "120px";
        img.style.maxHeight = "120px";
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);                        // 파일 → base64
    });
  });

  /* -------- 2) 버튼 클릭 → 스피너 표시 -------- */
  btn.addEventListener("click", (e) => {
    spinner.classList.remove("d-none");                  // 스피너 보이기
  });
});