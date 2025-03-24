// static/js/ajax_polling.js

document.addEventListener("DOMContentLoaded", function() {
    setInterval(function(){
        fetch("/poll/")
        .then(response => response.json())
        .then(data => {
            if(data.game){
                // Update the chessboard
                data.game.board.forEach(function(row){
                    for(let pos in row){
                        document.getElementById(pos).innerHTML = row[pos];
                    }
                });
                // Update current turn
                document.getElementById('current-turn').innerText = 'Current Turn: ' + data.game.current_turn;
            }
            if(data.available_users){
                // Update the opponent dropdown in challenge form
                let opponentSelect = document.getElementById('id_opponent');
                opponentSelect.innerHTML = '<option value="" disabled selected>Choose an opponent</option>';
                data.available_users.forEach(function(user){
                    let option = document.createElement('option');
                    option.value = user.id;
                    option.text = user.username;
                    opponentSelect.appendChild(option);
                });
            }
        });
    }, 1000); // Poll every second
});
