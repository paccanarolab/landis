var PANEL_NORMAL_CLASS    = "panel";
var PANEL_COLLAPSED_CLASS = "panelcollapsed";
var PANEL_HEADING_TAG     = "h2";
var PANEL_CONTENT_CLASS   = "panelcontent";
var PANEL_COOKIE_NAME     = "panels";
var PANEL_ANIMATION_DELAY = 20; /*ms*/
var PANEL_ANIMATION_STEPS = 10;

function setUpPanels()
{
	loadSettings();
	// get all headings
	var headingTags = document.getElementsByTagName(PANEL_HEADING_TAG);
	
	// go through all tags
	for (var i=0; i<headingTags.length; i++)
	{
		var el = headingTags[i];
		
		// make sure it's the heading inside a panel
		if (el.parentNode.className != PANEL_NORMAL_CLASS && el.parentNode.className != PANEL_COLLAPSED_CLASS)
			continue;
		
		// get the text value of the tag
		var name = el.firstChild.nodeValue;
	    //collapse everything at the beginning.
        el.parentNode.className = PANEL_COLLAPSED_CLASS;
		
		// add the click behavor to headings
		el.onclick = function() 
		{
			var target    = this.parentNode;
			var name      = this.firstChild.nodeValue;
			var collapsed = (target.className == PANEL_COLLAPSED_CLASS);
			saveSettings(name, collapsed?"true":"false");
			animateTogglePanel(target, collapsed);
		};
	}
}

/**
 * Start the expand/collapse animation of the panel
 * @param panel reference to the panel div
 */
function animateTogglePanel(panel, expanding)
{
	// find the .panelcontent div
	var elements = panel.getElementsByTagName("div");
	var panelContent = null;
	for (var i=0; i<elements.length; i++)
	{
		if (elements[i].className == PANEL_CONTENT_CLASS)
		{
			panelContent = elements[i];
			break;
		}
	}
	
	// make sure the content is visible before getting its height
	panelContent.style.display = "block";
	
	// get the height of the content
	var contentHeight = panelContent.offsetHeight;
	
	// if panel is collapsed and expanding, we must start with 0 height
	if (expanding)
		panelContent.style.height = "0px";
	
	var stepHeight = contentHeight / PANEL_ANIMATION_STEPS;
	var direction = (!expanding ? -1 : 1);
	
	setTimeout(function(){animateStep(panelContent,1,stepHeight,direction)}, PANEL_ANIMATION_DELAY);
}

/**
 * Change the height of the target
 * @param panelContent	reference to the panel content to change height
 * @param iteration		current iteration; animation will be stopped when iteration reaches PANEL_ANIMATION_STEPS
 * @param stepHeight	height increment to be added/substracted in one step
 * @param direction		1 for expanding, -1 for collapsing
 */
function animateStep(panelContent, iteration, stepHeight, direction)
{
	if (iteration<PANEL_ANIMATION_STEPS)
	{
		panelContent.style.height = Math.round(((direction>0) ? iteration : 10 - iteration) * stepHeight) +"px";
		iteration++;
		setTimeout(function(){animateStep(panelContent,iteration,stepHeight,direction)}, PANEL_ANIMATION_DELAY);
	}
	else
	{
		// set class for the panel
		panelContent.parentNode.className = (direction<0) ? PANEL_COLLAPSED_CLASS : PANEL_NORMAL_CLASS;
		// clear inline styles
		panelContent.style.display = panelContent.style.height = "";
	}
}

// -----------------------------------------------------------------------------------------------
// Load-Save
// -----------------------------------------------------------------------------------------------
/**
 * Reads the "panels" cookie if exists, expects data formatted as key:value|key:value... puts in panelsStatus object
 */
function loadSettings()
{
	// prepare the object that will keep the panel statuses
    //we have never created the cookie, therefore, nothing is saved.
	panelsStatus = {};
	// find the cookie name
	var start = document.cookie.indexOf(PANEL_COOKIE_NAME + "=");
	if (start == -1) return;
	
	// starting point of the value
	start += PANEL_COOKIE_NAME.length+1;
	
	// find end point of the value
	var end = document.cookie.indexOf(";", start);
	if (end == -1) end = document.cookie.length;
	
	// get the value, split into key:value pairs
	var cookieValue = unescape(document.cookie.substring(start, end));
	var panelsData = cookieValue.split("|");
	
	// split each key:value pair and put in object
	for (var i=0; i< panelsData.length; i++)
	{
		var pair = panelsData[i].split(":");
		panelsStatus[pair[0]] = pair[1];
	}
}

function expandAll()
{
	for (var key in panelsStatus)
		saveSettings(key, "true");
		
	setUpPanels();
}

function collapseAll()
{
	for (var key in panelsStatus)
		saveSettings(key, "false");
		
	setUpPanels();
}

/**
 * Takes data from the panelsStatus object, formats as key:value|key:value... and puts in cookie valid for 365 days
 * @param key	key name to save
 * @paeam value	key value
 */
function saveSettings(key, value)
{
	// put the new value in the object
	panelsStatus[key] = value;
	
	// create an array that will keep the key:value pairs
	var panelsData = [];
	for (var key in panelsStatus)
		panelsData.push(key+":"+panelsStatus[key]);
		
	// set the cookie expiration date 1 year from now
	/*var today = new Date();
	var expirationDate = new Date(today.getTime() + 365 * 1000 * 60 * 60 * 24);
	// write the cookie
	document.cookie = PANEL_COOKIE_NAME + "=" + escape(panelsData.join("|")) + ";expires=" + expirationDate.toGMTString();*/
}

// -----------------------------------------------------------------------------------------------
// Register setUpPanels to be executed on load
if (window.addEventListener)
{
	// the "proper" way
	window.addEventListener("load", setUpPanels, false);
}
else 
if (window.attachEvent)
{
	// the IE way
	window.attachEvent("onload", setUpPanels);
}

$(document).ready(function() {
   $("#bgPopup").data("state",0);
});

//Recenter the popup on resize - Thanks @Dan Harvey [http://www.danharvey.com.au/]
$(window).resize(function() {
centerPopup();
});

$("#closeMessageBox").click(function() {
        disablePopup();  // function close pop up
    });

function loadPopup(){
    //loads popup only if it is disabled
    if($("#bgPopup").data("state")==0){
        centerPopup(); 
        $("#bgPopup").css({
            "opacity": "0.7"
        });
        $("#bgPopup").fadeIn("medium");
        $("#Popup").fadeIn("medium");
        $("#bgPopup").data("state",1);

        $("#closeMessageBox").hide();
        $("#Popup").html("");
        $("#Popup").html("<center> <img src=\"images/processing.gif\"/></center>");
        $("#Popup").append("Validating input. Please wait.");
    }
}

function disablePopup(){
    if ($("#bgPopup").data("state")==1){
        $("#bgPopup").fadeOut("medium");
        $("#Popup").fadeOut("medium");
        $("#bgPopup").data("state",0);
    }
}

function centerPopup(){
    var winw = $(window).width();
    var winh = $(window).height();
    var popw = $('#Popup').width();
    var poph = $('#Popup').height();
    $("#Popup").css({
        "position" : "fixed",
        "top" : winh/2-poph/2,
        "left" : winw/2 - popw/2

    });
    //IE6
    $("#bgPopup").css({
        "height": winh  
    });
}


function drawPlot(){

                var margin = {top: 12, right: 12, bottom: 18, left: 30},
                        width = 766 - margin.left - margin.right,
                        height = 380 - margin.top - margin.bottom;

                    var x = d3.scale.ordinal()
                        .rangeRoundBands([0, width], .1);

                    var y = d3.scale.linear()
                        .range([height, 0]);

                    var xAxis = d3.svg.axis()
                        .scale(x)
                        .orient("bottom");

                    var yAxis = d3.svg.axis()
                        .scale(y)
                        .orient("left");

                    var svg = d3.select("#svg_container").append("svg")
                        .attr("width", width + margin.left + margin.right)
                        .attr("height", height + margin.top + margin.bottom)
                        .append("g")
                        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                    d3.csv('/disimweb/static/files/histogram.csv', type, function(error, data) {
                      x.domain(data.map(function(d) { return d.bin; }));
                      y.domain([0, d3.max(data, function(d) { return d.frequency; })]);

                      svg.append("g")
                          .attr("class", "x axis")
                          .attr("transform", "translate(0," + height + ")")
                          .call(xAxis);

                      svg.append("g")
                          .attr("class", "y axis")
                          .call(yAxis)
                        .append("text")
                          .attr("transform", "rotate(-90)")
                          .attr("y", 6)
                          .attr("dy", ".71em")
                          .style("text-anchor", "end")
                          .text("Frequency");

                      svg.selectAll(".bar")
                          .data(data)
                          .enter().append("rect")
                          .attr("class", "bar")
                          .attr("x", function(d) { return x(d.bin); })
                          .attr("width", x.rangeBand())
                          .attr("y", function(d) { return y(d.frequency); })
                          .attr("height", function(d) { return height - y(d.frequency); })
                          .attr("fill", function(d) { return colorSelector(d.bin);});

                    });

                    function colorSelector(bin)
                    {
                        var value = $("#resultBox").val();
                        if (value - bin <= 0.1 && value - bin > 0)
                            return "rgb(255, 0, 0)";
                        return "steelblue";
                    }

                    function type(d) {
                      d.frequency = +d.frequency;
                      return d;
                    }
}
