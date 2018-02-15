function hex2rgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
    ] : null;
}

function rgb2hex(rgb) {
    return '#' + ((1 << 24) + (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]).toString(16).slice(1);
}

function interpolateHex(color1, color2, factor) {
    var rgb1 = hex2rgb(color1),
        rgb2 = hex2rgb(color2);

    if (arguments.length < 3) { factor = 0.5 };

    var result = rgb1.slice();
    for (var i = 0; i < 3; i++) {
        result[i] = Math.round(result[i] + factor*(rgb2[i] - rgb1[i]));
    }

    return rgb2hex(result);
}

function generateColorMap(colors, steps, start, end) {
    var interval = (end - start) / steps,
        colorMap = {};

    for (i = 0; i < steps-1; i++) {
        var factor = (1 / steps) * i,
            maxTime = parseInt(start + (interval * i));
        colorMap[maxTime] = interpolateHex(colors.oldest, colors.newest, factor);
    }
    
    var endInterval = interval * (steps-1),
        endIntervalTime = parseInt(endInterval + start);
    colorMap[endIntervalTime] = colors.newest;
    return colorMap;
}

function getTimeBreaks(colorMap) {
    var keys = Object.keys(colorMap).sort();
    var timeBreaks = keys.map(function(k) {
        return parseInt(k);
    }).reverse();
    return timeBreaks;
}

function getColor(colorMap, timestamp) {
    var colorKey,
        timeBreaks = getTimeBreaks(colorMap);

    timeBreaks.some(function(value) {
        colorKey = value;
        return timestamp > value;
    });
    return colorMap[colorKey];
}