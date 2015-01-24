var __db = (function(){

	function startGeo(){

		navigator.geolocation.watchPosition(handleLocation, function(err){
			console.error(err);
			startGeo();
		},{
			enableHighAccuracy : true,
			maximumAge : 10000,
			timeout : 20000,
		});

	}

	function handleLocation(data){

		console.log(data);

		var coordinates = data.coords;

		return;

		jQuery.ajax({
			type : "GET",
			url : "/position/",
			data : {
				latitude : coords.latitude,
				longitude : coords.longitude
			}, success : function(){

				console.log("Position recognised");

			}, error : function(err){
				//We can't connect for some reason. Let's assume there's no signal from the device
				console.error(err);

			}
		});

	}

	function addEvents(){

		document.getElementById('begin').addEventListener('click', function(){

			console.log("You clicked!");

			startGeo();

		}, false);

	}

	function init(){
		
		if("geolocation" in navigator){

			console.log("Great, we can play");

			addEvents();

			//startGeo();

		} else { 

			alert("Sorry, you can't play Sacradash");

		}

	}

	return{
		init : init
	};

})();

(function(){
	__db.init();
})();