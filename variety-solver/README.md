# Crossword Nexus Variety Puzzle Solver
#### Make any variety puzzle available for online solving

## Installation
Simply download the files in this repo and add them to your web site.

## Usage

### vPuz file
You'll need to create a `vPuz` file to render your puzzle. You can look at the example in this repo for a guide. It is essentially the same as an iPuz file, with many fields removed, and two new ones added. The new fields are
* `puzzle-image`: a base64 representation of your puzzle grid. We recommend using https://www.base64encoder.io/image-to-base64-converter/ and choosing the "Base64 Image source" option
* `solution-string` (optional): the (uppercase) letters in the solution of your puzzle, in any order. If present, confetti will appear when the user puts these letters in the grid.

To allow users to solve your puzzle, create a URL like https://your.site/variety-solver?file=/link/to/your/file.vpuz

## Solving
Solving using the variety solver is relatively intuitive. Click in the puzzle image to add a letter. Click on a letter and hit "delete" (or "backspace") to remove.

## License
This software is released under the MIT License.
