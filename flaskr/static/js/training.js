// autocomplete function
function autocompleteBirdName(options) {
    // A function which create divs to show suggestions from a list when user is typing in a field
    // suggestions are clickable to autofill the text field
    const {
        inputFieldId,           // Text element to show suggestion for
        autocompleteDivId,      // Div where autocomplete suggestions will be displayed
        dataSource,             // Source of autocomplete data (array or api address)
        maxResults = 5,         // Maximum number of results to show
    } = options;

    // set up the list of possible names for autocomplete
    let autocompleteData = []
    if (Array.isArray(dataSource)) {
        autocompleteData = dataSource
    } else {
        fetch(dataSource)
            .then(response => response.json())
            .then(data => {
                autocompleteData = data;
            })
            .catch(error => {
                console.error("Error fetching data from " + dataSource, error);
            });
    }
    
    const inputField = document.getElementById(inputFieldId);
    const autocompleteDiv = document.getElementById(autocompleteDivId)
    
    inputField.addEventListener('input', function() {
        const currentText = inputField.value.toLowerCase();
        autocompleteDiv.innerHTML = ''; // Clear any previous autocomplete

        if (currentText) {
            const autocompleteDataFiltered = autocompleteData.filter(elem => elem.toLowerCase().includes(currentText));
            const autocompleteDataFilteredLimited = autocompleteDataFiltered.slice(0, maxResults);  // Limit results

            autocompleteDataFilteredLimited.forEach(elem => {
                const autocompleteElement = document.createElement('div');
                autocompleteElement.textContent = elem;
                autocompleteElement.classList.add('autocomplete-item');
                
                // Allow clicking on autocomplete to fill wantedBird field
                autocompleteElement.addEventListener('click', function() {
                    inputField.value = elem;
                    autocompleteDiv.innerHTML = ''; // Clear autocompletes afterwards
                });
                autocompleteDiv.appendChild(autocompleteElement);
            });
        };
    });
};


document.getElementById('wantedBird').addEventListener('input', function() {
    autocompleteBirdName({
        inputFieldId = this.getAttribute('id'),
        autocompleteDivId = this.getAttribute('autocompleteDivId'),   // Div where autocomplete suggestions will be displayed
        dataSource,           // Source of autocomplete data (array or api address)
        maxResults = 5,    
    })
});

// autocomplete
let globalBirdNameSet = Set()

document.addEventListener('DOMContentLoaded', function() {
    console.log("Autocomplete loaded");
    const wantedBirdField = document.getElementById('wantedBird');
    const autocompleteDiv = document.getElementById('autocomplete');

    fetch('/training/get_bird_name_list')
        .then(response => response.json())
        .then(data => {
            globalBirdNameSet = Set(data);
        })
        .catch(error => {
            console.error("Error fetching bird names", error);
        });
});

// autocomplete
document.getElementById('wantedBird').addEventListener('input', function() {
    console.log("training bird made");
    const query = wantedBirdField.value.toLowerCase();
    autocompleteDiv.innerHTML = ''; // Clear any previous autocomplete to avoid issues

    if (query) {
        const filteredBirdNames = globalBirdNameSet.filter(birdName => birdName.toLowerCase().includes(query));
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


// let userBirdLst = [];
const trainingBirdSelectorField = document.getElementById("trainingBirdSelector").addEventListener('input', autocompleteBirdName());
trainingBirdSelectorField.addEventListener('submit', function() {
    
    console.log("training bird made");
    const query = wantedBirdField.value.toLowerCase();
    autocompleteDiv.innerHTML = ''; // Clear any previous autocomplete to avoid issues
});


// Bird user display
let userBirdLst = [];

const listContainer = document.getElementById('elementList');

        // Populate the list
        elements.forEach(element => {
            const listItem = document.createElement('div');
            listItem.classList.add('list-item');
            listItem.textContent = element;
            listContainer.appendChild(listItem);
        });