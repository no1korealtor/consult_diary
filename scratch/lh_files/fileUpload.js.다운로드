// FormData[0] 형식자동변환 지원여부 확인
function fn_FormDataSupport(formId){
	if (document.createElement('canvas').getContext) {
		try {
			formData = new FormData($("#"+formId)[0]);
			return true;
		} catch (e) {
			return false;
		}
	}
	return false;
}

// html5 지원여부 확인
function fn_html5Support() {
	if (document.createElement('canvas').getContext) {
		try {
			FileReader;
			return true;
		} catch (e) {
			return false;
		}
	}

	return false;
}

// 파일 확장자
function fn_getFileExtClass(fileExt) {
	
	if(fileExt != null){
		fileExt = fileExt.toLowerCase();	
	}
	
	if (fileExt == "gul" || fileExt == "hwp") {
		return "file_hw";
	} else if (fileExt == "doc" || fileExt == "docx") {
		return "file_word";
	} else if (fileExt == "pptx" || fileExt == "pptx") {
		return "file_ppt";
	} else if (fileExt == "pdf") {
		return "file_pdf";
	} else if (fileExt == "xls" || fileExt == "xlsx") {
		return "file_excel";
	} else if (fileExt == "jpg" || fileExt == "jpeg") {
		return "file_jpg";
	} else if (fileExt == "gif") {
		return "file_gif";
	} else if (fileExt == "bmp") {
		return "file_bmp";
	} else if (fileExt == "png") {
		return "file_png";
	} else if (fileExt == "txt") {
		return "file_note";
	} else if (fileExt == "dwg" || fileExt == "dxf" || fileExt == "dwt" || fileExt == "dwf" || fileExt == "iges" || fileExt == "step" || fileExt == "kosdic" || fileExt == "stl" || fileExt == "cals") {
		return "file_dwg";
	} else if (fileExt == "zip") {
		return "file_zip";
	} else {
		return "file_blank";
	}
}