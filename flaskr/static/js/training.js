document.addEventListener('DOMContentLoaded', () => {
    // Load set data
    let userSetList = [];
    let currentBirdsInSet = [];
    let defaultSetList = [];
    let allBirdsList = []

    loadSetNames()
        .then(userSetArray => {
            if (Array.isArray(userSetArray)) {
                console.log(userSetArray);
                userSetList = userSetArray;
            } else {
                console.error("User set loading did not return an Array:", userSetArray);
            }
        })
        .catch(error => {
            console.error("Failed to load user sets from database:", error);
        })
    
    // load base prefilled sets that cannot be modified
    loadSetNames(baseSets=true)
        .then(userSetArray => {
            if (Array.isArray(userSetArray)) {
                console.log(userSetArray);
                defaultSetList = userSetArray;
            } else {
                console.error("User set loading did not return an Array:", userSetArray);
            }
        })
        .catch(error => {
            console.error("Failed to load user sets from database:", error);
        })
    
    // load all bird names in an array
    loadBirdNames()
        .then(birdArray => {
            if (Array.isArray(birdArray)) {
                console.log(birdArray);
                allBirdsList = birdArray;
            } else {
                console.error("User set loading did not return an Array:", birdArray);
            }
        })
        .catch(error => {
            console.error("Failed to load user sets from database:", error);
        })


    // DOM elements
        // user set manipulation
    const setNameInput = document.getElementById('setNameInput');
    const birdInput = document.getElementById('birdInput');
    const userSetContent = document.getElementById('userSetContent');
    const currentSetNameDisplay = document.getElementById('currentSetName');
    const emptyMessage = document.getElementById('emptyMessage');

        // bird song player
    const songLoadInput = document.getElementById('songLoadInput');
    const audioPlayer = document.getElementById('audioPlayer');  // audio player
    const currentBirdSongDisplay = document.getElementById('currentBirdSongDisplay')

    // Buttons
    const loadSetButton = document.getElementById('loadSetButton');
    const createSetButton = document.getElementById('createSetButton');
    const deleteSetButton = document.getElementById('deleteSetButton');
    const addBirdButton = document.getElementById('addBirdButton');
    const loadSongButton = document.getElementById('loadSongButton')

    // Add event listeners for buttons
    if (loadSetButton) {
        loadSetButton.addEventListener('click', loadSet);
    } else {
        console.info("Element with id 'loadSetButton' was not loaded")
    }
    if (createSetButton) {
        createSetButton.addEventListener('click', createSet);
    } else {
        console.info("Element with id 'createSetButton' was not loaded")
    }
    if (deleteSetButton) {
        deleteSetButton.addEventListener('click', deleteSet);
    } else {
        console.info("Element with id 'deleteSetButton' was not loaded")
    }
    if (addBirdButton) {
        addBirdButton.addEventListener('click', addBird);
    } else {
        console.info("Element with id 'addBirdButton' was not loaded")
    }
    if (loadSongButton) {
        loadSongButton.addEventListener('click', loadSongUrl);
    } else {
        console.info("Element with id 'loadSongButton' was not loaded")
    }
    
    
    // Add event listeners for autocomplete
    document.getElementById('songLoadInput').addEventListener('input', function() {
        autocompleteBirdName({
            inputFieldId: this.getAttribute('id'),  // Div where autocomplete suggestions will be displayed
            dataSource:allBirdsList, // Source of autocomplete data (array or api address)
            maxResults:5,  
        })
    });

    document.getElementById('setNameInput').addEventListener('input', function() {
        autocompleteBirdName({
            inputFieldId: this.getAttribute('id'),  // Div where autocomplete suggestions will be displayed
            dataSource:userSetList, // Source of autocomplete data (array or api address)
            maxResults:5,  
        })
    });

    document.getElementById('birdInput').addEventListener('input', function() {
        autocompleteBirdName({
            inputFieldId: this.getAttribute('id'),  // Div where autocomplete suggestions will be displayed
            dataSource:allBirdsList, // Source of autocomplete data (array or api address)
            maxResults:5,  
        })
    });


    // On click event functions
    function loadSet() {
        /* 
        Recover user set data from database
        Display the result by updating the html code
        */
        const setName = setNameInput.value.trim();
        if (!setName) {
            alert('Please enter a set name');
            return;
        }
        
        if (userSetList.includes(setName)) {
            // load birds
            loadBirdsInSet(setName)
                .then(birdArray => {
                    if (Array.isArray(birdArray)) {
                        console.log(birdArray);
                        currentBirdsInSet = birdArray;
                        currentSetNameDisplay.textContent = setName;
                        refreshBirdNameList();
                        setNameInput.value = '';
                    } else {
                        console.error("User set loading did not return an Array:", userSetArray)
                    }
                })
            .catch(error => {
                console.error("Failed to load birds from user_set from database:", error);
            })
        } else {
            alert(`Set "${setName}" does not exist. Create it first.`);
        }
    }
    
    function createSet() {
        // Create a user set with input name
        console.log("current set value", setNameInput.value, setNameInput)
        const setName = setNameInput.value.trim();
        if (!setName) {
            alert('Please enter a set name');
            return;
        }
        
        // check if a set with this name already exists
        // delete previous set upon confirmation if already exists
        if (defaultSetList.includes(setName)) {
            alert(`${setName} is a default set and can't be modified`);
            return;
        } else if (userSetList.includes(setName)) {
            if (!confirm(`Set "${setName}" already exists. Do you want to replace it?`)) {
                return;
            } else {
                deleteSetFromDatabase(setName)
                    .then(response => {
                        if (response.ok) {
                            console.log(`Deleted ${setName} to overwrite it`)
                        } else {
                            console.error("HTTP error when overwriting set:", response);
                        }
                    })
                    .catch(error => {
                        console.error("Failed to overwrite set in database:", error);
                    })
            }
        } 
        
        createSetInDatabase(setName)
            .then(response => {
                if (response.ok) {
                    // update and clear elements
                    currentSet = setName;
                    currentSetNameDisplay.textContent = setName;
                    userSetList.push(setName);
                    refreshBirdNameList();
                    setNameInput.value = '';
                } else {
                    console.error("HTTP error when creating set with response:", response);
                }
            })
            .catch(error => {
                console.error("Failed to create user set in database:", error);
            })
    }

    function addBird() {
        // add a bird to the current set
        // Create a user set with input name
        const setName = currentSetNameDisplay.textContent.trim();
        const birdName = birdInput.value.trim()
        if (!setName) {
           console.error('No set loaded when trying to add a bird');
            return;
        } else if (defaultSetList.includes(setName)) {
            warn("Can't modify a default set");
            return;
        } else if (currentBirdsInSet.includes(birdName)) {
            alert('This bird is already in the current set')
            return;
        }
        
        addBirdToSetInDatabase(birdName, setName)
            .then(response => {
                if (response.ok) {
                    currentBirdsInSet.push(birdName)
                    // update and clear elements
                    refreshBirdNameList();
                    birdInput.value = '';
                } else {
                    console.log(`Couldn't add ${birdName} in current set. HTTP error : ${response}`);
                    return;
                }
            })
            .catch(error => {
                console.error("Failed to add bird to set in database:", error);
            })
    }

    function deleteSet() {
        // Delete user set
        const setName = setNameInput.value.trim();
        if (!setName) {
            console.error('No set selected');
             return;
        } else if (defaultSetList.includes(setName)) {
            warn("Can't delete a default set");
            return;
        }

        deleteSetFromDatabase(setName)
            .then(response => {
                if (response.ok) {
                    console.log(`Successfully deleted set ${setName} from database`)
                    // update and clear elements
                    birdInput.value = '';
                    setNameInput.value = '';
                    currentBirdsInSet.value = '';
                    currentSetNameDisplay.textContent = '';
                    refreshBirdNameList();
                } else {
                    console.log(`Couldn't delete ${setName} from database. HTTP error : ${response}`);
                    return;
                }
            })
            .catch(error => {
                console.error("Failed to delete set from database:", error);
            });
    }

    function loadSongUrl() {
        // Get a song url from a bird
        const birdName = songLoadInput.value.trim();
        let songUrl = ""

        if (!birdName) {
            alert('Please enter a bird name');
            return;
        }
        console.log(`Loading bird song for ${birdName}`);
        loadBirdSongFomDatabase(birdName)
            .then(songUrlStr => {
                songUrl = songUrlStr;
                // update display
                if (songUrl === "") {
                    console.log("Empty song url");
                }
                audioPlayer.src = songUrl;
                audioPlayer.load();
                currentBirdSongDisplay.textContent = birdName;
                songLoadInput.value = '';
            })
        .catch(error => {
            console.error("Failed to load bird song from database:", error);
        })
    }

    // helper functions

    // Load existing sets from database
    async function loadSetNames(baseSets=false) {
        let setLst = [];
        let url;
        try {
            if (baseSets === true) {
                url = "/training/get_user_sets/default"
            } else {
                url = "/training/get_user_sets/all"
            }
            const data = {
                method: 'GET',
                headers: {
                    'Content-Type': 'json'
                }
            }
            const response = await fetch(url, data);
            
            if (!response.ok) {
                throw new Error(`HTTP error fetching bird user data. Status ${response.status}`)
            }
            setLst = await response.json();
            console.log(setLst)
            return setLst;
        } catch (error) {
            console.error("Error fetching user set names", error);
            throw error;  // break code as this is not supposed to happen
        };
    };

    // create an empty user set in database
    async function createSetInDatabase(setName) {
        try {
            const url = `/training/create_set/${setName}`
            const data = {
                method: 'POST',
                headers: {
                    'Content-Type': 'json'
                },
                body: JSON.stringify(setName)
            }
            response = await fetch(url, data);
    
            if (!response.ok) {
                throw new Error(`HTTP error when deleting user set ${setName}. status: ${response.status}`);
            } else {
                return response
            }
        } catch {
            console.error('Error posting data:', error);
            throw error;
        } 
    };

    // Update display elements to reflect changes in set selected or set composition
    function refreshBirdNameList() {
        // Clear the list first
        while (userSetContent.firstChild) {
            userSetContent.removeChild(userSetContent.firstChild);
        }
        console.log("refreshing bird displayed")

        // Display message if the set is empty or no set loaded 
        if (!currentBirdsInSet || currentBirdsInSet.length === 0) {
            userSetContent.appendChild(emptyMessage);
            return;
        }
        
        // Display all bird in set
        const currentSetName = currentSetNameDisplay.textContent.trim()
        currentBirdsInSet.forEach((element, index) => {
            console.log("Birds in current set, updating display")
            const listItem = document.createElement('div');
            listItem.className = 'list-item';
            
            const text = document.createElement('span');
            text.textContent = element;
            
            // create a button to easily remove birds from set
            const removeButton = document.createElement('button');
            removeButton.className = 'remove-button';
            removeButton.textContent = 'Remove';
            removeButton.onclick = () => removeBird(index);
            
            listItem.appendChild(text);
            // Only add a remove button if it's a user set and not a default set
            if (!defaultSetList.includes(currentSetName)) {
                listItem.appendChild(removeButton);
            }
            userSetContent.appendChild(listItem);
        });
    };

    // remove a bird from a set
    function removeBird(index) {
        const removedBird = currentBirdsInSet[index]
        const currentSet = currentSetNameDisplay.textContent.trim()
        // remove from database
        deleteBirdFromSetInDatabase(currentSet, removedBird) 
            .then(response => {
                if (response.ok) {
                    console.log(`Successfully deleted bird ${removedBird} from set ${currentSet} in database`)
                    // update display
                    currentBirdsInSet.splice(index, 1);
                    refreshBirdNameList();
                } else {
                    console.log(`Couldn't delete ${removeBird} from set ${currentSet} in database. HTTP error : ${response}`);
                    return;
                }
            })
            .catch(error => {
                console.error("Failed to remove bird from set in database:", error);
            })
    }

    async function deleteBirdFromSetInDatabase(setName, birdName) {
        try {
            const url = `/training/remove_bird_from_set/${setName}/${birdName}`
            const data = {
                method: 'POST',
                headers: {
                    'Content-Type': 'json'
                }
            }
            const response = await fetch(url, data);
            
            if (!response.ok) {
                throw new Error(`HTTP error deleting ${birdName} in set ${setName}. Status ${response.status}`)
            }
            return response;
        } catch (error) {
            console.error("Error deleting bird in set", error);
            throw error;  // break code as this is not supposed to happen
        };
    }

    async function loadBirdsInSet(setName) {
        let birdNameLst = [];
        try {
            const url = `/training/get_birds_in_set/${setName}`
            const data = {
                method: 'GET',
                headers: {
                    'Content-Type': 'json'
                }
            }
            const response = await fetch(url, data);
            
            if (!response.ok) {
                throw new Error(`HTTP error fetching bird names from set ${setName}. Status ${response.status}`);
            }
            birdNameLst = await response.json();
            return birdNameLst;
        } catch (error) {
            console.error(`Error fetching birds in user_set ${setName}`, error);
            throw error;  // break code as this is not supposed to happen
        };
    };

    async function addBirdToSetInDatabase(birdName, setName) {
        try {
            const url = `/training/add_to_user_set/${setName}/${birdName}`
            const data = {
                method: 'POST',
                headers: {
                    'Content-Type': 'json'
                }
            }
            const response = await fetch(url, data);
            if (!response.ok) {
                throw new Error(`HTTP error adding ${birdName} into set ${setName}. Status ${response.status}`);
            } 
            return response;
        } catch (error) {
            console.error(`Error adding ${birdName} to ${setName} in database`, error);
            throw error;  // break code as this is not supposed to happen
        }
    };

    async function deleteSetFromDatabase(setName) {
        try {
            const url = `/training/delete_set/${setName}`
            const data = {
                method: 'POST',
                headers: {
                    'Content-Type': 'json'
                }
            }
            const response = await fetch(url, data);
            
            if (!response.ok) {
                throw new Error(`HTTP error deleting user set ${setName}. Status ${response.status}`)
            }
            return response;
        } catch (error) {
            console.error(`Error deleting user set ${setName}`, error);
            throw error;  // break code as this is not supposed to happen
        };
    };

    // Audio song loading
    async function loadBirdSongFomDatabase(birdName) {
        let songUrl = "";
        try {
            const url = `/training/get_bird_song/${birdName}`
            const data = {
                method: 'GET',
                headers: {
                    'Content-Type': 'json'
                }
            }
            const response = await fetch(url, data);
            
            if (!response.ok) {
                throw new Error(`HTTP error fetching bird song from ${birdName}. Status ${response.status}`);
            }
            songUrl = await response.text(); // use .text() to recover an html string here
            return songUrl;
        } catch (error) {
            console.error(`Error fetching song url from bird ${birdName}`, error);
            throw error;  // break code as this is not supposed to happen
        };
    };

    // load all burd names in an array for autocomplete
    async function loadBirdNames() {
        try {
            const url = `/training/get_bird_name_list`
            const data = {
                method: 'GET',
            }
            const response = await fetch(url, data);
            
            if (!response.ok) {
                throw new Error(`HTTP error fetching all bird names. Status ${response.status}`);
            }
            const birdArray = await response.json(); // use .text() to recover an html string here
            return birdArray;
        } catch (error) {
            console.error(`Error fetching song url from bird ${birdName}`, error);
            throw error;  // break code as this is not supposed to happen
        };
    }

    // Autocomplete function
    function autocompleteBirdName(options) {
        // A function which create divs to show suggestions from a list when user is typing in a field
        // suggestions are clickable to autofill the text field
        const {
            inputFieldId,           // id of html Text element to show suggestion for
            dataSource,             // Source of autocomplete data (array)
            maxResults = 5,         // Maximum number of results to show
        } = options;
    
        // set up the list of possible names for autocomplete
        const autocompleteData = dataSource
        
        const inputField = document.getElementById(inputFieldId);
        const autocompleteDivId = inputFieldId + "Autocomplete" // id of html div where autocomplete suggestions will be displayed
        const autocompleteDiv = document.getElementById(autocompleteDivId)
        
        inputField.addEventListener('input', function() {
            const currentText = inputField.value.trim().toLowerCase();
            autocompleteDiv.textContent = ''; // Clear any previous autocomplete
    
            if(currentText) {
                const autocompleteDataFiltered = autocompleteData.filter(elem => elem.toLowerCase().includes(currentText));
                const autocompleteDataFilteredLimited = autocompleteDataFiltered.slice(0, maxResults);  // Limit results
                
                // crezate the div elements for showing autocomplete suggestions
                autocompleteDataFilteredLimited.forEach(elem => {
                    const autocompleteElement = document.createElement('div');
                    autocompleteElement.textContent = elem;
                    autocompleteElement.classList.add('autocomplete-item');
                    
                    // Allow clicking on autocomplete to fill the text box
                    autocompleteElement.addEventListener('click', function() {
                        inputField.value = elem;
                        autocompleteDiv.textContent = ''; // Clear autocompletes afterwards
                    });
                    autocompleteDiv.appendChild(autocompleteElement);
                });
            };
        });
    };
});