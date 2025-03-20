// load a bird data upon page loading
document.addEventListener('DOMContentLoaded', function () {
    fetch('/game/select_random_bird')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error when fetching bird data');
            }
            console.log('Bird selected successfully', response.status);
            return response.status;
        })
        .catch(error => {
            console.error('Failed to select bird:', error);
        })
    })

// play sound from current bird
function playBirdSound() {
    fetch('/game/get_bird_sound_url')
        .then(response => response.json())
        .then(data => {
            console.log(data.url);
            const audioPlayer = document.getElementById("audioPlayer");
            audioPlayer.src = data.url;
            audioPlayer.play();
        })
        .catch(error => {
            console.error("Error fetching bird sound URL:", error);
        });
}
  
// play sound on click on the audio
document.getElementById("audioPlayer").addEventListener("click", function() {
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.play();
  });