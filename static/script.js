document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();  // Prevent form submission

    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];  // Get the selected file
    if (!file) return;  // If no file is selected, exit

    var formData = new FormData();
    formData.append('file', file);  // Append the file to FormData object

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/index', true);

    // Show the progress bar
    document.getElementById('progressContainer').style.display = 'block';

    // Update progress bar as the file is uploaded
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            var percent = (e.loaded / e.total) * 100;
            document.getElementById('progressBar').style.width = percent + '%';
            document.getElementById('progressBar').innerText = Math.round(percent) + '%';
        }
    };

    // When the upload is complete
    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log('File uploaded successfully!');
            window.location.reload();  // Reload page to show uploaded files
        } else {
            console.error('Error uploading file!');
        }
    };

    // Send the request
    xhr.send(formData);
});
