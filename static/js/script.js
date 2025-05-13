// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded successfully');

    // Safe paragraph handling
    function handleParagraphs() {
        try {
            const paragraphs = document.querySelectorAll('[data-content]');
            if (!paragraphs.length) return;

            paragraphs.forEach((element) => {
                const content = element.getAttribute('data-content');
                if (content) {
                    element.textContent = content;
                }
            });
        } catch (error) {
            console.error('Error handling paragraphs:', error);
        }
    }

    // Initialize paragraph handling
    handleParagraphs();

    // Handle dynamic content updates
    const observer = new MutationObserver(handleParagraphs);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

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