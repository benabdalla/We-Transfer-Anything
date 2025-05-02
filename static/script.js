const uploadForm = document.getElementById('uploadForm');
    const progressBar = document.getElementById('progressBar');
    const progressContainer = document.querySelector('.progress');

    uploadForm.addEventListener('submit', function(e) {
      e.preventDefault(); // prevent default form submit

      const formData = new FormData(uploadForm);
      const xhr = new XMLHttpRequest();

      xhr.open('POST', uploadForm.action);

      xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
          const percent = Math.round((e.loaded / e.total) * 100);
          progressBar.style.width = percent + '%';
          progressBar.setAttribute('aria-valuenow', percent);
          progressBar.textContent = percent + '%';
          progressContainer.style.display = 'block';
        }
      });

      xhr.onload = function() {
        if (xhr.status == 200) {
          progressBar.classList.remove('progress-bar-animated');
          progressBar.classList.add('bg-success');
          progressBar.textContent = 'Upload complete!';
          setTimeout(() => { location.reload(); }, 1000);
        } else {
          progressBar.classList.remove('progress-bar-animated');
          progressBar.classList.add('bg-danger');
          progressBar.textContent = 'Upload failed!';
        }
      };

      xhr.send(formData);
    });