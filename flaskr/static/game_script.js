
// load a bird upon page loading
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

document.addEventListener('DOMContentLoaded', function () {
    fetch('/game/get_session_attributes')
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

function playBirdSound() {
    fetch('/get_bird_sound_url')
        .then(response => response.json())
        .then(data => {
            console.log(data.url);
            const audioPlayer = document.getElementById("audioPlayer");
            audioPlayer.src = data.url;
            audioPlayer.play();
        });
}
  
// play sound on click on the audio
document.getElementById("audioPlayer").addEventListener("click", function() {
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.play();
  });