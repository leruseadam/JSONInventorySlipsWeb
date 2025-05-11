// Load JSON data from a URL and process it
function loadFromUrl() {
    const url = document.getElementById('json_url').value;
    if (!url) {
        alert('Please enter a URL');
        return;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            document.getElementById('json_data').value = JSON.stringify(data, null, 2);
            processJsonData();
        })
        .catch(error => {
            alert('Error loading data: ' + error.message);
        });
}

// Process pasted JSON data
function processJsonData() {
    const jsonData = document.getElementById('json_data').value;
    if (!jsonData) {
        alert('Please enter JSON data');
        return;
    }

    fetch('/paste_json', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'json_text=' + encodeURIComponent(jsonData)
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && !data.success) {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error processing data: ' + error.message);
    });
}