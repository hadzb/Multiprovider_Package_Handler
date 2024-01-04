document.addEventListener("DOMContentLoaded", function() {
    var timerRows = document.querySelectorAll("#timerTable .timer");

    timerRows.forEach(function(timerCell) {
        var seconds = parseInt(timerCell.parentElement.querySelector("td").textContent);
        startCountdown(seconds, timerCell);
    });

    function startCountdown(seconds, displayElement) {
        var timerInterval = setInterval(function() {
            var hours = Math.floor(seconds / 3600);
            var minutes = Math.floor((seconds % 3600) / 60);
            var secondsLeft = seconds % 60;

            // Format the time string
            var formattedTime = 
                hours.toString().padStart(2, '0') + ":" + 
                minutes.toString().padStart(2, '0') + ":" + 
                secondsLeft.toString().padStart(2, '0');

            // Display the formatted time
            displayElement.textContent = formattedTime;

            // Decrease seconds
            seconds--;

            // Stop the timer when it reaches 0
            if (seconds < 0) {
                clearInterval(timerInterval);
                displayElement.textContent = "Time's up!";
            }
        }, 1000);
    }
});
