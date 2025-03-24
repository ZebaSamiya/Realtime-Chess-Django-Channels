// Function to move a chess piece from source to destination
function movePiece() {
  // Get the source and destination input values
  let src = document.getElementById('src').value;
  let dst = document.getElementById('dst').value;

  // Validate that both source and destination are provided
  if (!src || !dst) {
    alert("Please enter both source and destination.");
    return;
  }

  // Get the source and destination elements (td) on the chessboard
  let srcElement = document.getElementById(src);
  let dstElement = document.getElementById(dst);

  // Check if both elements exist on the board
  if (!srcElement || !dstElement) {
    alert("Invalid source or destination square.");
    return;
  }

  // Move the piece from source to destination
  dstElement.innerHTML = srcElement.innerHTML; // Move the piece
  srcElement.innerHTML = ""; // Clear the source square
}

// Function to reset the chessboard to its initial state
function resetBoard() {
  window.location.reload(); // Reload the page to reset the board
}
