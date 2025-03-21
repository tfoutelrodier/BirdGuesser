// load a bird data and song upon page loading
document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById("audioPlayer")
    fetch('/game/select_random_bird')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error when fetching bird data');
            }
            console.log('Bird selected successfully', response.status);
            
            // Now load sound url
            fetch('/game/get_bird_sound_url')
                .then(response => response.json())
                .then(data => {
                    audioPlayer.src = data.url;
                })
                .catch(error => {
                    console.error("Error fetching bird sound URL:", error);
                });
            return response.status;
        })
        .catch(error => {
            // Display error message
            console.error('Failed to select bird:', error);
        });
    })

// Add autocomplete to user answer box
const answerField = document.getElementById('answer');
const autocompleteDiv = document.getElementById('autocomplete');
let birdNameList = [];
fetch('/game/get_bird_name_list')
    .then(response => response.json())
    .then(data => {
        birdNameList = data;
    })
    .catch(error => {
        console.error("Error fetching bird names", error);
    });

answerField.addEventListener('input', function() {
    const query = answerField.value.toLowerCase();
    autocompleteDiv.innerHTML = ''; // Clear any previous autocomplete to avoid issues

    if (query) {
        const filteredBirdNames = birdNameList.filter(birdName => birdName.toLowerCase().includes(query));
        const limitedFilteredBirdNames = filteredBirdNames.slice(0, 5);  // Limit to 5 results at most
        // Create a suggestion list
        limitedFilteredBirdNames.forEach(birdName => {
            const autocompleteElement = document.createElement('div');
            autocompleteElement.textContent = birdName;
            autocompleteElement.classList.add('autocomplete-item');
            
            // Allow clicking on autocomplete to fill answer field
            autocompleteElement.addEventListener('click', function() {
                answerField.value = birdName;
                autocompleteDiv.innerHTML = ''; // Clear autocompletes afterwards
            });
            
            autocompleteDiv.appendChild(autocompleteElement);
        });
    }
});
