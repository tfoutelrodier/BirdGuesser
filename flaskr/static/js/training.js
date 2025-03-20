// autocomplete
document.addEventListener('DOMContentLoaded', function() {
    console.log("Autocomplete loaded");
    const wantedBirdField = document.getElementById('wantedBird');
    const autocompleteDiv = document.getElementById('autocomplete');
    let birdNameList = [];
    fetch('/training/get_bird_name_list')
        .then(response => response.json())
        .then(data => {
            birdNameList = data;
        })
        .catch(error => {
            console.error("Error fetching bird names", error);
        });
    
    wantedBirdField.addEventListener('input', function() {
        console.log("Input event triggered");
        const query = wantedBirdField.value.toLowerCase();
        autocompleteDiv.innerHTML = ''; // Clear any previous autocomplete to avoid issues
    
        if (query) {
            const filteredBirdNames = birdNameList.filter(birdName => birdName.toLowerCase().includes(query));
            const limitedFilteredBirdNames = filteredBirdNames.slice(0, 5);  // Limit to 5 results at most
    
            limitedFilteredBirdNames.forEach(birdName => {
                const autocompleteElement = document.createElement('div');
                autocompleteElement.textContent = birdName;
                autocompleteElement.classList.add('autocomplete-item');
                
                // Allow clicking on autocomplete to fill wantedBird field
                autocompleteElement.addEventListener('click', function() {
                    wantedBirdField.value = birdName;
                    autocompleteDiv.innerHTML = ''; // Clear autocompletes afterwards
                });
                
                autocompleteDiv.appendChild(autocompleteElement);
            });
        }
    });
});



// // sound loading after user select a bird to listen to
// document.addEventListener('DOMContentLoaded', function () {
//     const audioPlayer = document.getElementById("audioPlayer")
//     fetch('/game/select_random_bird')
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Error when fetching bird data');
//             }
//             console.log('Bird selected successfully', response.status);
            
//             // Now load sound url
//             fetch('/game/get_bird_sound_url')
//                 .then(response => response.json())
//                 .then(data => {
//                     audioPlayer.src = data.url;
//                 })
//                 .catch(error => {
//                     console.error("Error fetching bird sound URL:", error);
//                 });
//             return response.status;
//         })
//         .catch(error => {
//             // Display error message
//             console.error('Failed to select bird:', error);
//         });
//     })