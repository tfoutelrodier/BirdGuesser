// load a bird data and song upon page loading
document.addEventListener('DOMContentLoaded', function () {
    
    let nbGoodGuess = 0;  // keep track of user score
    let nbTotalGuess = 0;
    const nbGuessLimit = 10;
    let startingSetName = null; // placeholder to be able to preload a custom set on page load
    let currentBirdDict = {};  // this disc is expected to have 'name' and 'file' as key at minimum 
    let userSetList = [];
    let userSetBirdList = [];  
    
    // DOM Eleemnts
    const audioPlayer = document.getElementById("audioPlayer");
    const userAnswerInput = document.getElementById("userAnswer");
    const setNameInput = document.getElementById("setNameInput");
    const endGameWindow = document.getElementById("endGameWindow");

    // display elements
    const setNameDisplay = document.getElementById("setNameDisplay");
    const endGameMessageDisplay = document.getElementById("endGameMessage");

    // buttons
    const userAnswerButton = document.getElementById("userAnswerButton");  
    const loadSetButton = document.getElementById("loadSetButton");
    const newGuessButton = document.getElementById("newGuessButton");  
    const newGameButton = document.getElementById("newGameButton");    
        // end game window buttons
    const endGameReplayButton = document.getElementById("endGameReplayButton")
    const endGameCloseButton = document.getElementById("endGameCloseWindowButton")

    // Add on click events
    if (userAnswerButton) {
        userAnswerButton.addEventListener('click', checkAnswer);
    } else {
        console.info("Element with id 'userAnswerButton' was not loaded");
    };
    if (loadSetButton) {
        loadSetButton.addEventListener('click', loadSet);
    } else {
        console.info("Element with id 'loadSetButton' was not loaded");
    };
    if (newGuessButton) {
        newGuessButton.addEventListener('click', newGuessSetup);
    } else {
        console.info("Element with id 'newGuessButton' was not loaded");
    };
    if (newGameButton) {
        newGameButton.addEventListener('click', newGameSetup);
    } else {
        console.info("Element with id 'newGameButton' was not loaded");
    };
    if (endGameReplayButton) {
        endGameReplayButton.addEventListener('click', newGameSetup);
    } else {
        console.info("Element with id 'endGameReplayButton' was not loaded");
    };
    if (endGameCloseButton) {
        endGameCloseButton.addEventListener('click', hideEndGameWindow);
    } else {
        console.info("Element with id 'endGameCloseButton' was not loaded");
    };


    // input autocomplete events
    userAnswerInput.addEventListener('input', function() {
        autocompleteBirdName({
            inputFieldId: this.getAttribute('id'),  // Div where autocomplete suggestions will be displayed
            dataSource:userSetBirdList, // Source of autocomplete data (array or api address)
            maxResults:2,  
        })
    });
    setNameInput.addEventListener('input', function() {
        autocompleteBirdName({
            inputFieldId: this.getAttribute('id'),  // Div where autocomplete suggestions will be displayed
            dataSource:userSetList, // Source of autocomplete data (array or api address)
            maxResults:2,  
        })
    });


    // init dispaly elements and populate variables
    initPage(startingSetName);

    //////
    // on click functions
    //////

    // change display based on user answer
    function checkAnswer() {
        const userAnswer = document.getElementById('userAnswer').value.trim();
        const resultTextElem = document.getElementById('resultMessage');
        const correctBirdName = currentBirdDict['name'];
        
        // Do nothing if the answer was already checked
        if (resultTextElem.textContent != "") {
            return;
        };
        
        if (userAnswer == correctBirdName) {
            // right answer
            resultTextElem.textContent = `Correct! It's indeed a ${correctBirdName}.`;
            nbGoodGuess = nbGoodGuess + 1;
        } else {
            // wrong answer
            resultTextElem.textContent = `Wrong! It was a ${correctBirdName}.`;
        };
        nbTotalGuess = nbTotalGuess + 1;

        // check for game ending
        if (nbTotalGuess >= nbGuessLimit) {
            console.log("End game reached")
            setName = getSetName();
            const endGameMessage = `Game End.\nYou correctly identified ${nbGoodGuess} / ${nbTotalGuess} birds by sound from the set ${setName}.`
            // show the window
            showEndGameWindow(endGameMessage)
        } else {
            console.log("End game not reached")
        };
    };

    // Setup for next user guess when clicking on next guess button
    function newGuessSetup() {
        console.log("New guess setup");
        // only has an effect if the game has not ended.
        if (nbTotalGuess >= nbGuessLimit) {
            return;
        }

        // reset display elements
            // user input field
        document.getElementById('userAnswer').value = "";
            // result message field
        document.getElementById('resultMessage').textContent = "";
        
        // update score display
        document.getElementById('goodScore').textContent = nbGoodGuess;
        document.getElementById('totalGuesses').textContent = nbTotalGuess;

        // fetch new bird data
        updateCurrentBird();
    };

    // Setup for next game
    function newGameSetup() {
        console.log("New game setup");
        // This function is called either upon loading a new set or at the end of a game
        hideEndGameWindow(); 

        // reset score
        nbGoodGuess = 0;
        nbTotalGuess = 0;
        
        // additionnal display and select random bird
        newGuessSetup();  
    }

    // load user set
    function loadSet() {
        /* 
        Recover user set data from database
        Replace current bird name array with updated array 
        Display the result by updating the html code
        */
        const setName = getSetName();
        if (!setName) {
            alert('Please enter a set name');
            return;
        };
        
        if (userSetList.includes(setName)) {
            // load birds
            loadBirdsInSet(setName)
                .then(birdArray => {
                    if (Array.isArray(birdArray)) {
                        console.log(birdArray);
                        userSetBirdList = birdArray;
                        // Check that display the correct set
                        setNameDisplay.textContent = setName;
                        setNameInput.value = '';
                    } else {
                        console.error("User set loading did not return an Array:", userSetArray);
                    };
                })
            .catch(error => {
                console.error("Failed to load birds from user_set from database:", error);
            });
            // set the game with the new set
            newGameSetup();
        } else {
            alert(`Set "${setName}" does not exist. Create it first.`);
        };
    };

    
    /////
    // General functions
    /////
    
    // init page with default parameters
    function initPage(setName=null) {
        // Use default bird set if needed 
        if (setName == null) {
            setName = 'common_birds'
        }

        setNameDisplay.textContent = setName;
        userAnswerInput.value = '';
        setNameInput.vale = '';
        
        // populate some variable
        // load the names for all bird sets in database
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

        // load all birds in user set
        loadBirdsInSet(setName)
            .then(birdArray => {
                if (Array.isArray(birdArray)) {
                    console.log(birdArray);
                    userSetBirdList = birdArray;
                } else {
                    console.error("User set loading did not return an Array:", birdArray);
                }
            })
            .catch(error => {
                console.error("Failed to load user sets from database:", error);
            })
        
        // Set a new game
        newGameSetup();
    };

    // load a random bird data from currently loaded set
    function updateCurrentBird() {
        // load bird data then load audio if successfull  
        setName = getSetName()
        if (!setName) {
            console.error('No set selected');
            return;
        }

        fetchRandomBirdData(setName)
            .then(response => {
                console.log(`Successfully selected a new random bird from ${setName}`);
                // update bird data
                currentBirdDict = response;
                console.log(`selected bird ${currentBirdDict.name}`);
                // load song url
                loadSongUrl();
            })
            .catch(error => {
                console.error("Failed select random bird data:", error);
            });
    };

    // load the audio file
    function loadSongUrl() {     
        // check for url existence
        console.log(`bird dict: ${currentBirdDict['name']}`)

        if (!currentBirdDict) {
            console.log("bird dict not loaded")
        }

        if (!currentBirdDict["sound_url"]) {
            console.log("no song url for current bird")
            return;
        };

        const songUrl = currentBirdDict["sound_url"];
        console.log(`Loading bird song for ${currentBirdDict["name"]}: ${songUrl}`);
        
        if (songUrl === "") {
            console.log("Empty song url");
        };
        audioPlayer.src = songUrl;
        audioPlayer.load();
    };

    // Load existing set names from database
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

    // retrieve a random bird name and song url from given set
    async function fetchRandomBirdData(setName) {
        try {
            const url = `/game/get_random_bird_data/${setName}`
            const data = {
                method: 'GET',
                headers: {
                    'Content-Type': 'json'
                }
            }
            response = await fetch(url, data);
    
            if (!response.ok) {
                throw new Error(`HTTP error when retrieving random bird data from ${setName}. status: ${response.status}`);
            } else {
                return response.json()
            }
        } catch {
            console.error('Error fetchning random bird data:', error);
            throw error;
        } 
    }

    // returns a promise for an array of birds names
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

    ///////
    // Helper functions
    ///////

    // return current set name
    function getSetName() {
        const setName = document.getElementById("setNameDisplay").textContent.trim();
        return setName;
    }

    function showEndGameWindow(message="") {
        if (endGameMessageDisplay) {
            console.log("changing endgame window message");
            endGameMessageDisplay.textContent = message;
        } else {
            console.log("end game window message element not found");
        }
        
        endGameWindow.classList.remove("hidden");  
    }

    function hideEndGameWindow() {
        console.log("Hiding end game window")
        endGameWindow.classList.add("hidden");
    }
});
