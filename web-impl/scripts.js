const curTemp = document.getElementById("curTemp");

function updateStatus() {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
      if (xhr.readyState == 4 && xhr.status == 200) {
          var data = JSON.parse(xhr.responseText);
          curTemp.innerHTML = data.curTemp;       
      }
  };
  xhr.open("GET", "/status", true);
  xhr.send();
}

setInterval(updateStatus, 1000); // Refresh every 1 seconds