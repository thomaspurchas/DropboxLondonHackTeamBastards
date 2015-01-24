var __db = (function(){

	var client = undefined;

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

	function getStatus(){

		if(client === undefined){
			return false;
		} else {

			//
			console.log("Got here");

			jQuery.ajax({
				type : "GET",
				url : '/datastore_id/',
				success : function(res){

					console.log(res);

					var datastoreManager = client.getDatastoreManager();
					
					datastoreManager.openDatastore(res, function (error, datastore) {
					    // The datastore is now shared with this user.

					    console.log(datastore);

					});

				}, error : function(err){

					console.error(err);

				}
			});

		}

	}

	function init(){
		
		if("geolocation" in navigator){

			console.log("Great, we can play");

			addEvents();

			startGeo();

			jQuery.ajax({
				type : "GET",
				url : "/access_token/",
				success : function(res){

					console.log(res);
					client = new Dropbox.Client({key: "alb0kf2mp7ca1np", token : res});

					if(client.isAuthenticated() === true){
						getStatus();
					}

				}, error : function(err){

					console.error(err);

				}
			});

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