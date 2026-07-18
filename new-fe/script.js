const dropArea = document.getElementById("dropArea");
const input = document.getElementById("fileInput");
const filename = document.getElementById("filename");

dropArea.addEventListener("click", () => {
    input.click();
});

input.addEventListener("change", function(){

    if(this.files.length){

        filename.innerHTML=this.files[0].name;
    }

});

dropArea.addEventListener("dragover",(e)=>{

    e.preventDefault();

    dropArea.style.background="#252b38";

});

dropArea.addEventListener("dragleave",()=>{

    dropArea.style.background="#1a1d24";

});

dropArea.addEventListener("drop",(e)=>{

    e.preventDefault();

    dropArea.style.background="#1a1d24";

    const files=e.dataTransfer.files;

    input.files=files;

    if(files.length){

        filename.innerHTML=files[0].name;
    }

});
