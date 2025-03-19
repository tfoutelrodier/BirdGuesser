
// Setup actions
/*var focusBirdLst = "{{ g.focus_bird_lst | tojson}}";
var rareBirdLst = "{{ g.rare_bird_lst | tojson}}";

console.log(focusBirdLst)
console.log(rareBirdLst)
// Add birds to setup if not empty
focusBirdLst.forEach(function(birdName) {addItemToList("focus-list", birdName)});
rareBirdLst.forEach(function(birdName) {addItemToList("rare-list", birdName)});*/

document.getElementById('birdForm').addEventListener('submit', newFocusBird)
document.addEventListener("focusBirdForm", function() {
    "focusBirdFormText"
});



class BirdSet {
  constructor(name) {
    this.name = name // set name as stored in database

    // request the data to the server 
    // default request is 'get'
    fetch('/bird_set/get_bird_in_set?set_name=' + encodeURIComponent(this.name))
    .then(response => response.json())
    .then(data => {
        // Process the retrieved data
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
  }



}



// Function to handle form submission
function newFocusBird(event) {
    // event is passed implicitely
    event.preventDefault(); // Prevent the default form submission behavior

    // Retrieve the value from the input element
    var birdName = document.getElementById("focusBirdFormText").value;
    // Call the addBirdToSet function with appropriate parameters
    addBirdToSet('focusBirdForm', 'focus-list', focusBirdLst);
}


// Other functions
function addItemToList(listId, itemText) {
   // Add the element to the visible list
    var ul = document.getElementById(listId);

    // Create a new <li> element
    var li = document.createElement("li");

    // Set the text content of the <li> element
    li.textContent = itemText;

    // Append the <li> element to the <ul> element
    ul.appendChild(li);
}


function addBirdToSet(formId, listId, birdList) {
  /* formId --> id of the text box with the bird to add
    listId --> Id of the list element where the bird name is displayed
    birdList --> js array where all the current birds of the set are stored
  */
  // When adding a bird to focus group
  birdName = document.getElementById(formId).value;
  console.log("Adding" + birdName);
  if (birdList.includes(birdName)){
    birdList.push(birdName);
    // update visible list
    addItemToList(listId, birdName);
  }
  else {
    console.log("ERROR: " + birdName + " already present in set:" + formId)
  }
}








/*document.addEventListener('DOMContentLoaded', function() {
    const leftList = document.getElementById('left-list');
    const rightList = document.getElementById('right-list');
    const moveButton = document.getElementById('move-button');
    const validateButton = document.getElementById('validate-button');
    const newItemInput = document.getElementById('new-item');
    
    // Add event listener to move button
    moveButton.addEventListener('click', function() {
        // Get selected item from the left list
        const selectedItem = leftList.querySelector('.selected');
        if (selectedItem) {
            // Remove selected class from the item
            selectedItem.classList.remove('selected');
            // Clone the item and append it to the right list
            const newItem = selectedItem.cloneNode(true);
            rightList.appendChild(newItem);
        }
    });

    // Add event listener to validate button
    validateButton.addEventListener('click', function() {
        const newItemText = newItemInput.value.trim();
        if (newItemText) {
            // Create a new list item with the entered text
            const newItem = document.createElement('li');
            newItem.textContent = newItemText;
            // Append the new item to the left list
            leftList.appendChild(newItem);
            // Clear the input field
            newItemInput.value = '';
        }
    });

    // Add event listener to left list items
    leftList.addEventListener('click', function(event) {
        const listItem = event.target;
        if (listItem.tagName === 'LI') {
            // Remove selected class from all items
            const items = leftList.querySelectorAll('li');
            items.forEach(item => item.classList.remove('selected'));
            // Add selected class to the clicked item
            listItem.classList.add('selected');
        }
    });
});
*/

/*  AUTOCOMPLETE SCRIPT */
function autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < arr.length; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
          /*execute a function when someone clicks on the item value (DIV element):*/
              b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
      x[i].parentNode.removeChild(x[i]);
    }
  }
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}