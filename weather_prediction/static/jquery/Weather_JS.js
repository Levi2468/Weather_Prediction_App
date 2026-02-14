$(document).ready(function () {

  /*Mode selection initial*/
  const mode = $("input[name='mode']:checked").val();
  if (mode==='manual'){
       $(".values").prop("readonly", false);
      $("#predict-btn").show();
      $("#reset-btn").show();
  }else{
       $(".values").prop("readonly", true);
       $("#predict-btn").hide();
      $("#reset-btn").hide();

  }
/* only show state map at first*/
  $(".district").hide();
  $("#state-map").addClass("hidden");
/* get and store selected district*/
  const savedState = $("#region").val();
  const savedDistrict = $("#location_name").val();

  if (savedState) {
    showStateMap(savedState);
  }

  if (savedState && savedDistrict) {
    $(`.district[data-state="${savedState}"]`).each(function () {
      if ($(this).text().trim() === savedDistrict) {
        $(this).addClass("selected").show();
      }
    });
  }

  /* ---------------- STATE CLICK(store the state name) ---------------- */
  $(".state").on("click", function () {
    const stateName = $(this).data("state");
    $("#region").val(stateName);
    showStateMap(stateName);
  });

  /* ---------------- DISTRICT CLICK(store district name and it respective lat and lon data ) ---------------- */
  $(".district").on("click", function () {

    $(".district").removeClass("selected");
    $(this).addClass("selected");

    const state = $(this).data("state");
    const district = $(this).text().trim();
    const lat = $(this).data("lat");
    const lon = $(this).data("lon");

    $("#region").val(state);
    $("#location_name").val(district);

    $("#selected-state").text(state);
    $("#selected-district").text(district);

    const mode = $("input[name='mode']:checked").val();
//if its in live mode fetch the lat and lon value automatically
    if (mode === "live" && lat && lon) {
      fetchRealtimeWeather(lat, lon, true);
    }
  });

  /* ---------------- MODE TOGGLE (live or manual)---------------- */
  $("input[name='mode']").on("change", function () {

    const isLive = $(this).val() === "live";
    $(".values").prop("readonly", isLive);

    if (isLive) {
      $("#predict-btn").hide();
      $("#reset-btn").hide();
      const lat = $(".district.selected").data("lat");
      const lon = $(".district.selected").data("lon");

      if (lat && lon) {
        fetchRealtimeWeather(lat, lon, true);
      }

    } else {//make the input readonly if mode== live
      $(".values").prop("readonly", false);
      $("#predict-btn").show();
      $("#reset-btn").show();
    }
  });

  /* ---------------- BACK TO INDIA (Go back to india map and hide the district map)---------------- */

  $("#back-to-india").on("click", function () {

    $("#state-map").addClass("hidden");
    $("#india-map").removeClass("hidden");

    $(".district").removeClass("selected").hide();
    $("#region").val("");
    $("#location_name").val("");
  });

//reset buttton
$("#reset-btn").on("click", function () {

  $(".values").each(function () {
    this.value = "";
    this.defaultValue = "";
  });

  $("#region").val("");
  $("#location_name").val("");
  $(".goback").text("")
  $(".district").removeClass("selected");

});


  /* ---------------- map image based on selection ---------------- */

  function showStateMap(stateName) {

    const imageName = stateName.toLowerCase().replaceAll(" ", "_");
    const imagePath = `/static/images/${imageName}.jpeg`;

    $("#state-img").attr("src", imagePath);

    $("#india-map").addClass("hidden");
    $("#state-map").removeClass("hidden");

    $(".district").hide();
    $(`.district[data-state="${stateName}"]`).show();
  }
//Get realtime weather info using weather api
  function fetchRealtimeWeather(lat, lon, autoPredict=false) {

    $.ajax({
      url: "/realtime-weather/",
      method: "GET",
      data: { lat: lat, lon: lon },

      success: function (data) {

        $("input[name='temperature']").val(data.temperature);
        $("input[name='feels_like_celsius']").val(data.feels_like_celsius);
        $("input[name='humidity']").val(data.humidity);
        $("input[name='cloud']").val(data.cloud);
        $("input[name='visibility']").val(data.visibility);
        $("input[name='uv']").val(data.uv);
        $("input[name='wind']").val(data.wind);
        $("input[name='gust']").val(data.gust);
        $("input[name='pressure']").val(data.pressure);
        $("input[name='precip']").val(data.precip);

        $("input[name='pm25']").val(data.pm25);
        $("input[name='pm10']").val(data.pm10);
        $("input[name='no2']").val(data.no2);
        $("input[name='so2']").val(data.so2);
        $("input[name='o3']").val(data.o3);
        $("input[name='co']").val(data.co);

        //  Hidden submit button get click automatically after the values get filled
        if (autoPredict) {
          $("#auto-submit").click();
        }
      },

      error: function () {
        alert("❌ Real-time weather data not available.");
      }
    });
  }

});
//AQI using javascript
document.addEventListener("DOMContentLoaded", function () {

    /* ------------------ USA AQI ------------------ */
    let usAQI = parseInt(document.getElementById("us-aqi-value").innerText);
    let usBar = document.getElementById("us-aqi-bar");
    let usInd = document.getElementById("us-aqi-indicator");

    if (!isNaN(usAQI)) {
        if (usAQI >= 1){
        let percent = (usAQI - 1) / 5 * 100;
        usInd.style.left = percent + "%";
        };
        let usLabel = "";
        if (usAQI === 1) usLabel = "Good";
        else if (usAQI === 2) usLabel = "Moderate";
        else if (usAQI === 3) usLabel = "Unhealthy for Sensitive Groups";
        else if (usAQI === 4) usLabel = "Unhealthy";
        else if (usAQI === 5) usLabel = "Very Unhealthy";
        else if (usAQI === 6) usLabel = "Hazardous";

        document.getElementById("us-aqi-label").innerText = usLabel;
    }

    /* ------------------ UK AQI ------------------ */
    let ukAQI = parseInt(document.getElementById("uk-aqi-value").innerText);
    let ukInd = document.getElementById("uk-aqi-indicator");

    if (!isNaN(ukAQI)) {
        if (ukAQI >=1){
        let percentUK = (ukAQI - 1) / 9 * 100;
        ukInd.style.left = percentUK + "%";
        };
        let ukLabel = "";
        if (ukAQI >=1 && ukAQI <= 3) ukLabel = "Low";
        else if (ukAQI >3 && ukAQI <= 6) ukLabel = "Moderate";
        else if (ukAQI >6 && ukAQI <= 8) ukLabel = "High";
        else if (ukAQI >8 && ukAQI <= 12) ukLabel = "Very High";
        else ukLabel="";

        document.getElementById("uk-aqi-label").innerText = ukLabel;
    }

});

