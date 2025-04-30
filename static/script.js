  const form = document.getElementById('uploadForm');
  const input = document.getElementById('fileInput');
  const progressBar = document.getElementById('progressBar');
  const progressContainer = document.getElementById('progressContainer');

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    const file = input.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/', true);

    progressContainer.style.display = 'block';

    xhr.upload.onprogress = function (e) {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
      }
    };

    xhr.onload = function () {
      if (xhr.status === 200) {
        location.reload();
      } else {
        alert('Upload failed.');
      }
    };

    xhr.send(formData);
  });
