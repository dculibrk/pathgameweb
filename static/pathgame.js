// number of levels that we have until restart the grid dimensions to 10x10
var numberOfLevels = 41;

var increaseStep = (level%41 === 0) ? 0 : level === 1 ? 0 : level%41;
//dimensions of grid (e.g. a 5x10 grid)
//the dimensions of the table increase as the level increases
var rows = 10 + increaseStep;
var cols = 10 + increaseStep;

//center coordinates of any circle being drawn
var x;
var y;

//center coordinates of first circle being drawn
var xstart = 10;
var ystart = 23;

// distance between center coordinates
var xspacing = 25;//100;
var yspacing = 25;//100;

// text shown at the end of the level
var fontSize = 60;

// text shown at the end of the level
var fontSizeOther = 10;

// size of the blue path that is created when moving mouse
var strokeWidth = 7;

// change of the color at the end of each level
var textOverColorHue = 1;

// number of cicles
var numberOfCircles = Math.floor(level/numberOfLevels);

// ratio of number of destinations that we should collect to total destinations
var probabilityDestination = 0.65;

if(level > 40 && level <= 81){
    probabilityDestination = 0.75;
} else if(level > 81 && level <= 122){
    probabilityDestination = 0.8
} else if(level > 122 && level <= 163){
    probabilityDestination = 0.85
} else if(level > 163){
    probabilityDestination = Math.floor(86 +  numberOfCircles - 4)/100;
    if(probabilityDestination > 0.9){
        probabilityDestination = 0.9;
    }
}

// dimensions of the circles in grid
var radius = 6;

// depo rotation speed
var depoRotationSpeed = 3;
if(level < 19 + numberOfCircles*41) {
    fontSize = (level%41)*1.5 + 20;
    textOverColorHue = 4;
    xspacing = 25;
    yspacing = 25;
    strokeWidth = 7;
} else if(level >= 19 + numberOfCircles*41 && level <= 29 + numberOfCircles*41) {
    xspacing = 18;
    yspacing = 18;
    fontSize = level%41 + 15;
    strokeWidth = 6.5;
    textOverColorHue = 2;
    radius = 4.7;
    depoRotationSpeed = 4.5;
} else if(level > 29 + numberOfCircles*41 && level <= 41 + numberOfCircles*41) {
    xspacing = 14;
    yspacing = 14;
    fontSize = level%41 + 30;
    strokeWidth = 6;
    textOverColorHue = 3;
    radius = 4;
    depoRotationSpeed = 6;
}

var xend = xstart + xspacing*(cols-1);
var yend = ystart + yspacing*(rows-1);

//changed css style so grid can be centered while the dimensions increase
document.getElementById("dubasCanvas").height = yend + 20;
document.getElementById("dubasCanvas").width = xend + 20;
document.getElementById("dubasCanvas").style.height = (yend + 20) + "px";
document.getElementById("dubasCanvas").style.width = (xend + 20) + "px";

document.getElementById("main_div").style.height = (yend + 110) + "px";
document.getElementById("main_div").style.width = (xend + 150) + "px";

document.getElementById("canvas_div").style.height = (yend + 150) + "px";
document.getElementById("canvas_div").style.width = (xend + 150) + "px";

var fillColor = 'orange';

var points = [];
var gameStarted = 0;

//var canvas = document.getElementById('dubasCanvas');
//paper.setup(canvas);

/*var layer = new Layer();
//layer.position = new Point(150,150);
var allgroup = new Group();
layer.addChild(allgroup);

var group = new Group();
allgroup.addChild(group);
var rectangle = new Rectangle(new Point(0, 0), new Point(300, 300));

var path = new Path.Rectangle(rectangle);
path.fillColor = 'green';
group.addChild(path);

var group2 = new Group();
allgroup.addChild(group2);
var rectangle = new Rectangle(new Point(0, 0), new Point(100, 200));

var path = new Path.Rectangle(rectangle);
path.fillColor = 'red';
group2.addChild(path);

//paper.view.draw();*/
//create a super group to hold the lines and points in the path sthat will be suggested to the user until he reaches one of the nodes for visit
//var suggestedPath = new Group();
var suggestedPathLines = new Group();
suggestedPathLines.name = 'lines';
var suggestedPathPoints = [];

var pointsDestination = [];
var pathPoints = [];
//suggestedPathPoints.name = 'points';

var gameOver = 0;

//suggestedPath.addChild(suggestedPathLines);
//suggestedPath.addChild(suggestedPathPoints);

gridGroup = new Group(); //this holds the grid
pointGroup = new Group(); //this holds the circles

var pointsGrid = []; //this holds the grid locations

var pathGroup = new Group(); //this holds the lines of the path
var numDestinations = 0; //this will be used to

var text = new PointText({ point: view.top, justification: 'left', fontSize: fontSizeOther, fillColor: 'green'});
text.content = 'POINTS LEFT:';
var text1 = new PointText({ point: view.top, justification: 'right', fontSize: fontSizeOther, fillColor: 'black'});
//var destination = Point.random() * view.size;
//var vector = destination - text1.position;
//text1.position += vector/3;

text1.position.x = xend;
text1.position.y += (ystart - 10);

text.position.x = xstart + 40;
text.position.y += (ystart - 10);

text1.content =  'TIME: ' + 0;

var timeElapsed = 0; //this is the timer

function findClosestInSuggestedPath(x,y){
    var closest = 0;

    var mdist = 2000;

    var dist_x = 0;
    var dist_y = 0;

    for (var i = 0; i < suggestedPathPoints.length; i++) {
        dist_x = Math.abs(suggestedPathPoints[i].x - x);
        dist_y = Math.abs(suggestedPathPoints[i].y - y);

        if(dist_x + dist_y < mdist){
            mdist= dist_x + dist_y;
            closest = i;
        }
    }

    return closest;
}

function findClosestInGrid(x,y){
    var closest = 0;

    var mdist = 2000;

    var dist_x = 0;
    var dist_y = 0;

    for (var i = 0; i < pointsGrid.length; i++) {
        dist_x = Math.abs(pointsGrid[i].x - x);
        dist_y = Math.abs(pointsGrid[i].y - y);

        if(dist_x + dist_y < mdist){
            mdist= dist_x + dist_y;
            closest = i;

        }
    }

    return closest;
}

//call to display the gameover message and send data to python
function endGame(){
    //var textover = new PointText({ point: view.center, justification: 'center', fontSize: 200, fillColor: 'cyan'});
    //textover.content = 'GAME OVER';
    //text1.content = 'GAME OVER';
    //textover.content = 'LEVEL '+str(level)+' DONE!'
    gameOver = 1;
    //textover.opacity = 0;

    //create a json array to send
    var result = {};

    var pathPointsJSON= [];

    for(var i in pathPoints) {

        var item = pathPoints[i];

        pathPointsJSON.push({
            "x" : item.x,
            "y"  : item.y
        });
    }

    result.pathpoints = pathPointsJSON;

    var pathlength = 0;

    //calculate the length of the path
    for (var j = 1; j < pathPoints.length; j++) {
        var first = pathPoints[j-1];
        var second = pathPoints[j];

        pathlength = pathlength + Math.sqrt((second.x - first.x)*(second.x - first.x) + (second.y - first.y)*(second.y - first.y));
    }

    var pointsDestinationJSON= [];

    var numdestpoints = 0;

    for(var i in pointsDestination) {

        var item = pointsDestination[i];

        pointsDestinationJSON.push({
            "x" : item.x,
            "y"  : item.y
        });
        numdestpoints++;
    }

    result.pointsdestination = pointsDestinationJSON;
    result.time = timeElapsed;
    result.pathlength = pathlength;
    result.numdestpoints = numdestpoints;

    //$.post("receiver", { 'pointsdestination' : 'nja' , 'pathpoints': 'nja2' }, function(){
        //console.log(result);
    //});
    $.post( "/postmethod", {
        //javascript_data: result
        javascript_data: JSON.stringify(result)
    });

    //event.preventDefault();
}

//this just gets an index of the point in the pointGroup which needs to be added to the suggested pat
function addPointToSuggestedPath(point){
    // add a line segment for visualization
    var point_loc = new Point(pointsGrid[point].x, pointsGrid[point].y);
    var segm = new Path.Line(suggestedPathPoints[suggestedPathPoints.length-1], point_loc);
    segm.strokeColor = 'blue';
    segm.strokeWidth = strokeWidth;
    segm.opacity = 0.5;
    suggestedPathLines.addChild(segm);

    // add the point
    suggestedPathPoints.push(point_loc);
}

// update the suggested path based on the location of the mouse (x,y)
function updateSuggestedPath(x,y){
    var closest = findClosestInSuggestedPath(x,y);
    //text1.content = closest;

    //check if the last point in the path is the closest to the pointer, or the path should be pruned
    if( closest != suggestedPathPoints.length - 1){
        //prune the path to the closest
        for(var i = suggestedPathPoints.length - 1; i > closest; i--){
            suggestedPathPoints.pop();
        }

        for(var i = suggestedPathLines.children.length - 1; i >= closest; i--){
            var tmp  = suggestedPathLines.children[i];
            suggestedPathLines.children[i].remove();
            tmp.removeSegment(0);
        }
    }

    closest = findClosestInGrid(x,y);

    //text.content = suggestedPathPoints.length;
    text.content = numDestinations;
    text1.content = closest;
    //text.remove();

    addPointToSuggestedPath(closest);

    if(pointGroup.children[closest].fillColor == 'blue'){
        //text1.content = 'iiiiha';
        //this is a destination point so make the suggested path part of the full part
        for(i = suggestedPathLines.children.length - 1; i >= 0; i--){
            pathGroup.addChild(suggestedPathLines.children[i]);
        }

        //text1.content = 'iiiiha';

        for(var i = suggestedPathLines.children.length - 1; i >= 0; i--){
            var tmp  = suggestedPathLines.children[i];
            suggestedPathLines.children[i].remove();
            tmp.removeSegment(0);
        }
        suggestedPathLines.remove();

        suggestedPathLines = new Group();

        for(var i = 0; i < suggestedPathPoints.length; i++){

            pathPoints.push(suggestedPathPoints[i]);
        }

        for(var i = suggestedPathPoints.length - 1; i >= 0; i--){
            suggestedPathPoints.pop();
        }

        suggestedPathPoints.push(new Point(pointsGrid[closest].x, pointsGrid[closest].y));

        pointGroup.children[closest].fillColor = 'black'; //change the color so it is not counted any more

        if (numDestinations <= 0){
            //we got all the the the destinations, close the game
            endGame();

        }

        numDestinations--; //decrease the num of destinations that need to be visited


    }

}

//clear the suggested path and add the depo
function clearSuggestedPath(depo_x, depo_y){
    for (var i = suggestedPathLines.children.length - 1; i >= 0 ; i--) {
        suggestedPathLines.children[i].remove();
    }

    for (var i = suggestedPathPoints.length -1; i >= 0 ; i--) {
        //suggestedPathPoints[i].remove();
        suggestedPathPoints.pop(); // suggestedPathPoints.splice(i, 1);
    }

    suggestedPathPoints.push(new Point(depo_x,depo_y));
}

var cellSize = 100;
var gridColor = '#D0D0D0';

var boundingRect = view.bounds;
var rectanglesX = view.size.width / cellSize;
var rectanglesY = view.size.height / cellSize;

var xposs = [];
var yposs = [];

//Vertical Lines
for(var col = 0; col < cols; col++) {
    var correctedLeftBounds = xstart; //Math.ceil(boundingRect.left / self.cellSize) * self.cellSize;
    var xPos = correctedLeftBounds + col * xspacing;
    var topPoint = new Point(xPos, ystart);
    var bottomPoint = new Point(xPos, yend);
    var gridLine = new Path.Line(topPoint, bottomPoint);

    xposs[col] = xPos;

    gridLine.strokeColor = gridColor;
    gridLine.strokeWidth = 1;

    gridGroup.addChild(gridLine);

}

//Horizontal Lines
for(var row = 0; row < rows; row++) {
    var correctedTopBounds = ystart; //Math.ceil(boundingRect.left / self.cellSize) * self.cellSize;
    var yPos = correctedTopBounds + row * yspacing;
    var topPoint = new Point(xstart, yPos);
    var bottomPoint = new Point(xend, yPos);
    var gridLine = new Path.Line(topPoint, bottomPoint);

    yposs[row] = xPos;

    gridLine.strokeColor = gridColor;
    gridLine.strokeWidth = 1;

    gridGroup.addChild(gridLine);

}

//Removes the children of the gridGroup and discards the gridGroup itself
function removeGrid() {
    for (var i = 0; i<= gridGroup.children.length-1; i++) {
        gridGroup.children[i].remove();
    }
    gridGroup.remove();
}

gridGroup.sendToBack();

//drawGrid(100);

// draw circles
for(var row = 0, i = 0; row < rows; row++) {
    y = ystart + row * yspacing;

    for(var col = 0; col < cols; col++, i++) {
        x = xstart + col * xspacing;
        var point = new Point(x, y);
        var dot = new Path.Circle(point, radius);

        if((Math.random() < probabilityDestination) && (col != Math.floor(cols/2)) && (row != Math.floor(rows/2))){
            //this should be the destination
            dot.fillColor = 'blue';
            numDestinations++;

            /*dot.onMouseDown = function(event) {
                this.fillColor = 'green';
            }

            dot.onMouseDrag = function(event) {
                this.fillColor = 'green';
            }*/

            pointsDestination[i] = point;

        }else{
            //this is just a grid point
            dot.fillColor = fillColor;
        }

        pointGroup.addChild(dot);
        pointsGrid[i] = point;
    }
}

var textover = new PointText({ point: view.center, justification: 'center', fontSize: fontSize, fillColor: 'cyan'});
// var textover = new PointText({ position: view.center, content: 'Text', fillColor: 'black', fontFamily: 'Courier New', fontWeight: 'bold', fontSize: 25 });
var canvas = document.getElementById('dubasCanvas');
var context = canvas.getContext('2d');
// console.log(context);
// var textwidth = context.measureText(textover).width;
// console.log("textwidth", textwidth);
// console.log("rows", rows);
// console.log("cols", cols);
// console.log("xstart", xstart);
// console.log("ystart", ystart);
// textover.position.x = xstart + Math.floor(cols/2 - 1)*(xspacing + 10) - textwidth/2;
// textover.position.y = ystart + Math.floor(rows/2 - 1)*(yspacing + 10) - textwidth/10; //-=ystart;
textover.position.x = context.canvas.width/2;
textover.position.y = Math.floor(rows/2)*yspacing + ystart; //-=ystart;
// console.log("textover.position.x", textover.position.x);
// console.log("textover.position.y", textover.position.y);
textover.content = 'LEVEL ' +  level + ' DONE!'; //'GAME OVER!';
textover.opacity = 0;
// if(level > 100) {
//     textover.content = 'YOU PASSED 100 LEVELS!'; //'GAME OVER!';
//     textover.opacity = 1;
// }
//create the depo to be in the middle of the grid
var depox = Math.floor(cols/2)*xspacing + xstart;
var depoy = Math.floor(rows/2)*yspacing + ystart;

//var depoStart = new Point(150,150);
//var depoSize = new Size(75, 75);
//var depo = new Path.Rectangle(meterStart, meterSize);
//depo.strokeColor = 'red';

//var rectangle = new Rectangle(depox-xspacing/8, depoy-yspacing/8, xspacing/4, yspacing/4);
var rectangle = new Rectangle(depox-2*radius, depoy-2*radius, 4*radius, 4*radius);
var depo = null;

// LIMIT GAME TO 100 LEVELS
// if(level <= 100){
depo =new Path.Rectangle(rectangle);
depo.fillColor = 'cyan';
depo.name = 'depo';
depo.onMouseDown = function(event) {
    if(!gameStarted){
        this.fillColor = 'red';
        gameStarted = 1;
    }else if (!gameOver){
        //
        if(numDestinations <= 0){
            //we are in the end game stage
            for(var i = 0; i < suggestedPathPoints.length; i++){
                pathPoints.push(suggestedPathPoints[i]);
            }
            endGame();
        }
    }else{
        window.location.assign("/back");
    }
};
// }
//gridGroup.addChild(depo);

//add the depo to the suggested path
//suggestedPathPoints[0] = new Point(depox,depoy);
suggestedPathPoints.push(new Point(depox,depoy));

depo.bringToFront();

textover.onMouseDown = function(event) {
    if(gameOver){
        window.location.assign("/back");
    }
};

//animate stuff
function onFrame(event) {
    // Each frame, rotate the path by 3 degrees:
    depo.rotate(depoRotationSpeed);

    if(gameStarted && !gameOver){
        timeElapsed += event.delta;

        if(numDestinations > 0){
            text.content = 'POINTS LEFT: ' + numDestinations;
        }else{
            text.content = 'CLICK ON THE RECTANGLE!'
        }
        text1.content = 'TIME: ' + Number.parseFloat(timeElapsed).toFixed(2);
    }else{
        text.content = 'CLICK ON THE RECTANGLE!'
    }
    //updateSuggestedPath(event.point.x, event.point.y);
    if(gameOver){
        textover.bringToFront();
        if(textover.opacity < 1) {
            textover.opacity += 0.1;
        }else{
            textover.fillColor.hue += textOverColorHue;
        }
        depo.fillColor.hue += textOverColorHue;
    }

}

//go with the mouse and create path suggestions
function onMouseMove(event) {
 //   depo.rotate(3);
    if (gameStarted && !gameOver){
        //updateSuggestedPath(event.middlePoint.x, event.middlePoint.y);
        updateSuggestedPath(event.point.x, event.point.y);
        depo.bringToFront();
    }
}
