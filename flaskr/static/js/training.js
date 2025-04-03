// autocomplete function



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



// let userBirdLst = [];
const trainingBirdSelectorField = document.getElementById("trainingBirdSelector").addEventListener('input', autocompleteBirdName());
trainingBirdSelectorField.addEventListener('submit', function() {
    
    console.log("training bird made");
    const query = wantedBirdField.value.toLowerCase();
    autocompleteDiv.innerHTML = ''; // Clear any previous autocomplete to avoid issues
});


// Bird user display
let userBirdLst = [];

const listContainer = document.getElementById('birdNameList');

        // Populate the list
        elements.forEach(element => {
            const listItem = document.createElement('div');
            listItem.classList.add('list-item');
            listItem.textContent = element;
            listContainer.appendChild(listItem);
        });


// Load set data
const elementSets = loadSetNames();
let currentSet = null;
let currentBirds = []

// DOM elements
const setNameInput = document.getElementById('setNameInput');
const elementInput = document.getElementById('elementInput');
const birdNameList = document.getElementById('birdNameList');
const currentSetNameDisplay = document.getElementById('currentSetName');
const emptyMessage = document.getElementById('emptyMessage');

// Add event listeners
document.getElementById('loadSetBtn').addEventListener('click', loadSet);
document.getElementById('createSetBtn').addEventListener('click', createSet);
document.getElementById('addElementBtn').addEventListener('click', addElement);

// Load existing sets from database
async function loadSetNames() {
    let userSetLst = [];
    try {
        const response =  await fetch("/training/get_user_sets");
        
        if (!response.ok) {
            throw new Error(`HTTP error fetching bird user data. Status ${response.status}`)
        }
        userSetLst = await response.json();
        return userSetLst
    } catch (error) {
        console.error("Error fetching user set names", error);
        throw error;  // break code as this is not supposed to happen
    };
}


// Load an existing set or indicate if it doesn't exist
function loadSet() {
    const setName = setNameInput.value.trim();
    if (!setName) {
        alert('Please enter a set name');
        return;
    }
    
    if (elementSets[setName]) {
        currentSet = setName;
        currentSetNameDisplay.textContent = setName;
        birdNameList = loadBirdsInSet(currentSet)
        refreshBirdNameList();
        setNameInput.value = '';
    } else {
        alert(`Set "${setName}" does not exist. Create it first.`);
    }
}

// Create a new set
async function createSet() {
    const setName = setNameInput.value.trim();
    if (!setName) {
        alert('Please enter a set name');
        return;
    }
    
    // check if a set with this name already exists
    // delete previous set upon confirmation if already exists
    if (elementSets[setName]) {
        if (!confirm(`Set "${setName}" already exists. Do you want to replace it?`)) {
            return;
        } else {
            deleteUserSet(set_name)
        }
    }
    
    // update and clear elements
    currentSet = setName;
    currentSetNameDisplay.textContent = setName;
    refreshBirdNameList();
    setNameInput.value = '';
}


async function deleteUserSet(set_name) {
    try {
        const url = `/training/delete_set/${set_name}`
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': 'json'
            },
            body: JSON.stringify(setName)
        }
        response = await fetch(url, data);

        if (!response.ok) {
            throw new Error(`HTTP error when deleting user set ${set_name}. status: ${response.status}`);
        }
    } catch {
        console.error('Error posting data:', error);
        throw error;
    } 
}


async function createSetInDatabase(set_name) {
    try {
        const url = `/training/create_set/${set_name}`
        const data = {
            method: 'POST',
            headers: {
                'Content-Type': 'json'
            },
            body: JSON.stringify(setName)
        }
        response = await fetch(url, data);

        if (!response.ok) {
            throw new Error(`HTTP error when deleting user set ${set_name}. status: ${response.status}`);
        }
    } catch {
        console.error('Error posting data:', error);
        throw error;
    } 
}


// load bird names from set
async function loadBirdsInSet(set_name) {
    let birdNameLst = [];
    try {
        const response =  await fetch(`/training/get_birds_in_set/${set_name}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error fetching bird names from set ${set_name}. Status ${response.status}`)
        }
        birdNameLst = await response.json();
        return birdNameLst
    } catch (error) {
        console.error(`Error fetching birds in user_set ${set_name}`, error);
        throw error;  // break code as this is not supposed to happen
    };
}


// Add an element to the current set
function addElement() {
    if (!currentSet) {
        alert('Please load or create a set first');
        return;
    }
    
    const element = elementInput.value.trim();
    if (!element) {
        alert('Please enter an element');
        return;
    }
    
    elementSets[currentSet].push(element);
    refreshBirdNameList();
    elementInput.value = '';
}

// Remove an element from the current set
function removeElement(index) {
    elementSets[currentSet].splice(index, 1);
    refreshBirdNameList();
}

// Update the displayed list of elements
function refreshBirdNameList() {
    // Clear the list first
    while (birdNameList.firstChild) {
        birdNameList.removeChild(birdNameList.firstChild);
    }
    
    // Check if we have a current set and if it has any elements
    if (!currentSet || elementSets[currentSet].length === 0) {
        birdNameList.appendChild(emptyMessage);
        return;
    }
    
    // Add all elements to the list
    elementSets[currentSet].forEach((element, index) => {
        const listItem = document.createElement('div');
        listItem.className = 'list-item';
        
        const text = document.createElement('span');
        text.textContent = element;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-btn';
        removeBtn.textContent = 'Remove';
        removeBtn.onclick = () => removeElement(index);
        
        listItem.appendChild(text);
        listItem.appendChild(removeBtn);
        birdNameList.appendChild(listItem);
    });
}