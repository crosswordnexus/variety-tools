const canvas = document.getElementById("spiralCanvas");
const ctx = canvas.getContext("2d");

const centerX = canvas.width / 2;
const centerY = canvas.height / 2;

// Spiral configuration
const spacing = 13; // Space between spiral arms
const angleOffset = 4 * Math.PI / 3; // Start at 240 degrees
const NUM_LETTERS = 43; // letters in each of gray and white bands
const numSubdivisions = 5e4; // for plotting
const fillColor = "#CCCCCC";

// constants for thick spiral
const thickLineWidth = 3;
const thickStrokeStyle = "#000000";
const thickInitialRadius = 60;
const thickNumTurns = 3; // number of full turns of the spiral

// constants for thinner spiral
const thinLineWidth = 1;
const thinStrokeStyle = "#666666";
const thinInitialRadius = thickInitialRadius + spacing * Math.PI;
const thinNumTurns = thickNumTurns - 1;

// helper function to find the point closest to the given value
function findClosestPoint(points, target, value='radius') {
    return points.reduce((closest, point) => {
        return Math.abs(point[value] - target) < Math.abs(closest[value] - target) ? point : closest;
    });
}

// helper function similar to numpy linspace
function* linspace(start, end, num) {
    if (num === 1) {
        yield start; // Only yield the start if we want one value
        return;
    }

    const step = (end - start) / (num - 1);
    for (let i = 0; i < num; i++) {
        yield start + i * step;
    }
}

// Draw reverse spiral with offset
function drawSpiral(initialRadius, lineWidth, strokeStyle, numTurns,
          thick=false, savePoints=false, reverse=true, beginPath=true, returnLastPoint=false) {
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = strokeStyle;
    if (beginPath) ctx.beginPath();

    var myLinspace;
    if (reverse) {
      myLinspace = linspace(angleOffset, -numTurns * Math.PI * 2 + angleOffset, numSubdivisions);
    } else {
      myLinspace = linspace(angleOffset, numTurns * Math.PI * 2 + angleOffset, numSubdivisions);
    }

    var x, y, radius, angle, dist = 0;
    const spiralPoints = [];
    for (angle of myLinspace) {
        radius = initialRadius + spacing * Math.abs(angle - angleOffset);
        if (!reverse) radius = initialRadius - spacing * Math.abs(angle - angleOffset);
        x = centerX + radius * Math.cos(angle);
        y = centerY + radius * Math.sin(angle);

        if (angle === angleOffset) {
            // Move to the starting point of the spiral
            ctx.moveTo(x, y);
            if (savePoints) spiralPoints.push({ x, y, radius, angle, dist });
        } else {
            ctx.lineTo(x, y);
            if (savePoints) {
              let lastPoint = spiralPoints.at(-1);
              dist = lastPoint.dist + Math.hypot(x - lastPoint.x, y - lastPoint.y);
              spiralPoints.push({ x, y, radius, angle, dist });
            }
        }
    }
    ctx.stroke();
    // return
    if (returnLastPoint) return { x, y, radius, angle, dist };
    else return spiralPoints;
}

function drawSegment(radius, angle, lineWidth, strokeStyle, relativeLength = 1, beginPath = true) {
  // Get x and Y from this
  const startX = centerX + radius * Math.cos(angle);
  const startY = centerY + radius * Math.sin(angle);

  // the length of the line is 2 * PI * relativeLength * spacing
  let endRadius = radius + spacing * 2 * Math.PI * relativeLength;
  const endX = centerX + endRadius * Math.cos(angle);
  const endY = centerY + endRadius * Math.sin(angle);
  // draw the line
  if (beginPath) ctx.beginPath();
  ctx.moveTo(startX, startY);
  ctx.lineTo(endX, endY);
  ctx.strokeStyle = strokeStyle;
  ctx.lineWidth = lineWidth;
  ctx.stroke();
  return endRadius;
}

// Function to draw the jelly roll puzzle
function drawJellyRoll(numLetters=NUM_LETTERS) {
  /** Draw the main spiral to get spiralPoints **/
  const spiralPoints = drawSpiral(thickInitialRadius, 0, thickStrokeStyle, thickNumTurns, true, true);

  /** Draw a closed spiral to fill **/
  ctx.beginPath();
  // first, the spiral from the inside out
  let testColor = null;
  let testWidth = 0;
  let lastPt = drawSpiral(thickInitialRadius, testWidth, testColor, thickNumTurns - 1, true, false, true, false, true);
  // now the connecting line segment
  let segmentEndpointRadius = drawSegment(lastPt.radius, lastPt.angle, testWidth, testColor, 0.5, false);
  // draw a spiral back to the "beginning"
  drawSpiral(segmentEndpointRadius, testWidth, testColor, thickNumTurns - 1, false, false, false, false);
  ctx.closePath();
  ctx.fillStyle = fillColor;
  ctx.fill();


  /** Draw segments for each letter **/
  // find the closest point to where we want to end
  const endPoint = findClosestPoint(spiralPoints, thickInitialRadius + spacing * 2 * Math.PI);
  // find the length of each segment
  const distDelta = (spiralPoints.at(-1).dist - endPoint.dist) / numLetters;
  // starting angle and radius
  let myAngle = angleOffset;
  let myRadius = spiralPoints[0].radius;
  for (let i=0; i < numLetters; i++) {
    // don't draw anything if i == 0
    if (i > 0) {
      drawSegment(myRadius, myAngle, thinLineWidth, thinStrokeStyle);
      // draw the half-segment
      if (i % 2 == numLetters % 2) {
        drawSegment(myRadius, myAngle, thickLineWidth, thickStrokeStyle, relativeLength = 0.5);
      } else {
        drawSegment(myRadius + spacing * Math.PI, myAngle, thickLineWidth, thickStrokeStyle, relativeLength = 0.5);
      }
    }
    // find the endpoint of the segment we just drew
    let thisEndPoint = findClosestPoint(spiralPoints, myAngle - (2 * Math.PI), 'angle');
    // add deltaDist and find closest point
    let newPoint1 = findClosestPoint(spiralPoints, thisEndPoint.dist + distDelta, 'dist');
    // now go back 2pi
    let newPoint = findClosestPoint(spiralPoints, newPoint1.angle + 2 * Math.PI, 'angle');
    myAngle = newPoint.angle;
    myRadius = newPoint.radius;
  }

  // Thin spiral, then thick spiral
  drawSpiral(thinInitialRadius, thinLineWidth, thinStrokeStyle, thinNumTurns);
  drawSpiral(thickInitialRadius, thickLineWidth, thickStrokeStyle, thickNumTurns, true);

  // Close up the spiral on both ends
  drawSegment(spiralPoints[0].radius, spiralPoints[0].angle, thickLineWidth, thickStrokeStyle);
  const endRadius = thickInitialRadius + spacing * (thickNumTurns - 1) * (2 * Math.PI);
  drawSegment(endRadius, angleOffset, thickLineWidth, thickStrokeStyle);
}

// Export trimmed canvas
function getTrimmedCanvas() {
     const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
     const data = imageData.data;

     let top = canvas.height, bottom = 0, left = canvas.width, right = 0;

     for (let y = 0; y < canvas.height; y++) {
         for (let x = 0; x < canvas.width; x++) {
             const alpha = data[(y * canvas.width + x) * 4 + 3]; // Alpha channel

             if (alpha > 0) { // If pixel is not transparent
                 top = Math.min(top, y - 1);
                 bottom = Math.max(bottom, y + 1);
                 left = Math.min(left, x - 1);
                 right = Math.max(right, x + 1);
             }
         }
     }

     // Define new dimensions and create a new canvas
     const trimmedWidth = right - left;
     const trimmedHeight = bottom - top;
     const trimmedCanvas = document.createElement("canvas");
     trimmedCanvas.width = trimmedWidth;
     trimmedCanvas.height = trimmedHeight;
     const trimmedCtx = trimmedCanvas.getContext("2d");

     // Draw the trimmed area onto the new canvas
     trimmedCtx.putImageData(imageData, -left, -top);
     return trimmedCanvas;
 }
