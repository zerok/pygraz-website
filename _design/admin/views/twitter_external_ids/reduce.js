function (key, values, rereduce) {
  var result = [];
  if (!rereduce) {
    for (var i = 0 ; i < values.length; i++) {
       result.push(""+values[i]);
    }
  } else {
    for (var i = 0 ; i < values.length; i++) {
       for(var j = 0; j < values[i].length; j++) {
          if (result.indexOf(values[i][j]) === -1) {
            result.push(values[i][j]);
          }
       }
    }
  }
  return result;
}
