// Custom alert 정의
(function() {
    function initBox() {
        const alertBoxTmplId = "warnBox";
        const alertBoxTmpl   = `<div class="toast-container top-0 end-0 p-3" id="${alertBoxTmplId}"></div>`;

        let $warnBox = document.querySelector(`#${alertBoxTmplId}`);
        if( ! $warnBox ) {
            document.body.insertAdjacentHTML("beforeend", alertBoxTmpl);
            $warnBox = document.querySelector(`#${alertBoxTmplId}`);
        }
        return $warnBox;
    }
    function initAlert() {
        const alertTmplId = "warnPop";
        const alertTmpl   = `<template id="${alertTmplId}">
                                <div class="toast fade show blink-shadow" role="alert" aria-live="assertive" aria-atomic="true">
                                    <div class="toast-header text-bg-danger">
                                        <strong class="me-auto">{TITLE}</strong>
                                        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                                    </div>
                                    <div class="toast-body">{BODY}</div>
                                </div>
                            </template>`;

        let $alert = document.getElementById(`${alertTmplId}`);
        if( ! $alert ) {
            document.body.insertAdjacentHTML("beforeend", alertTmpl);
            $alert = document.getElementById(`${alertTmplId}`);
        }
        return document.importNode($alert.content,true);
    }

    const $warnBox = initBox();
    const $alert   = initAlert();

    const newAlert = function(title, body) {
        let $warn = $alert.cloneNode(true);
        $warn.querySelector(".me-auto").innerText    = title;
        $warn.querySelector(".toast-body").innerText = body;

        $warnBox.prepend($warn);
    }

    Object.defineProperty(window, 'newAlert', {
        value       : newAlert,
        writable    : false,
        configurable: false
    });
})();

// chatting box
const ChatBox = function(boxId) {
    const $chatLog = document.getElementById(boxId);
    const tmpl     = `<div class="d-flex">
                        <div class="p-3 rounded-4 chatMsg"></div>
                     </div>`;

    function getChatBlock(type, obj) {
        let $tmpl = document.createElement("div");
        $tmpl.innerHTML = tmpl;
        $tmpl = $tmpl.firstChild;

        switch(type) {
            case "bot":
                $tmpl.querySelector("div").classList.add("bg-light", "text-dark");
                break;
            case "me":
                $tmpl.classList.add("justify-content-end");
                $tmpl.querySelector("div").classList.add("bg-success", "text-white");
                break;
        }

        if( typeof obj === "string")  $tmpl.querySelector("div").innerHTML = obj;
        if( typeof obj === "object")  $tmpl.querySelector("div").appendChild(obj);

        return $tmpl;
    }
    function addNewChat(type, obj) {
        const $chatBlock = getChatBlock(type, obj);
        $chatLog.appendChild($chatBlock);
    }
    function add(obj) {
        $chatLog.appendChild(obj);
    }

    return {
        getChatBlock: getChatBlock,
        addNewChat  : addNewChat,
        add         : add,
    };
};

const setFilePreview = function($input, $preview) {
    $input.addEventListener("change", e1 => {
        $preview.innerHTML = "";
        for( let i in $input.files ) {
            let file = $input.files[i];
            if( file instanceof File ) {
                let $img = document.createElement("img");
                $img.classList.add("img-thumbnail");

                let reader = new FileReader();
                reader.onload = e => $img.src = e.target.result;
                reader.readAsDataURL(file);

                $preview.appendChild($img);
            }
        }
    });
};

(function() {
    // 채팅 로그 관리
    const chatBox = new ChatBox("chatLog");

    // 이미지 미리보기
    const $inputFile = document.getElementById("formFile")
    const $preview   = document.getElementById("preview");
    setFilePreview($inputFile, $preview);

    // 사용자 질문
    const f = document.askForm;
    const ask = function() {
        let fileCnt = f.images.files.length;
        let textLen = f.user_text.value.length;
        if( fileCnt === 0 && textLen === 0 ) {
            newAlert("필수 입력값 확인", "파일이나 텍스트 둘 중 하나는 입력해야 합니다.");
            return stopLoading();
        }


        let $msgTmpl = chatBox.getChatBlock("me", f.user_text.value);
        if( fileCnt > 0 ) {
            const $chatMsg = $msgTmpl.querySelector(".chatMsg");
            const $imgBox  = document.createElement("div");
            $chatMsg.prepend($imgBox);
            [...$preview.childNodes].forEach((e,i) => $imgBox.appendChild(e));
        }
        chatBox.add($msgTmpl);


        let params = {
            method:"POST",
            cache:"no-cache",
            headers:{
                "X-CSRFToken" :f.csrfmiddlewaretoken.value
            },
            body: new FormData(f)
        };
        fetch("/chat/", params)
            .then(resp => resp.json())
            .then(function(json) {
                try {
                    let html = marked.parse(json.answer);
                    chatBox.addNewChat("bot", html);
                } catch(err) {
                    console.error("appendChat got caught an error.", err)
                } finally {
                    stopLoading();
                    f.reset();
                }
            });
    }

    const $askBtn = document.getElementById("askBtn");
    $askBtn.addEventListener("click", e => {
        try {
            startLoading();
            ask();
        } catch(err) {
            console.error("ask got caught an error.", err);
            stopLoading();
        }
    });
    document.getElementById("floatingTextarea2").addEventListener("keydown", e => {
        let isEnter = e.key === "Enter";
        e.ctrlKey && isEnter && $askBtn.click();
    })
})();