var __db = (function(){

	var client = undefined,
		firstInstance = true,
		people = [];


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

		// return;

		jQuery.ajax({
			type : "GET",
			url : "/position/",
			data : {
				lat : coordinates.latitude,
				lon : coordinates.longitude
			}, success : function(res){

				console.log(res);
				console.log("Position recognised");

				getStatus();

			}, error : function(err){
				//We can't connect for some reason. Let's assume there's no signal from the device
				console.error(err);

			}
		});

	}

	function addEvents(){

		document.getElementById('begin').addEventListener('click', function(){

			console.log("You clicked!");

			// startGeo();

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

					    people = [];

					    var teamTable = datastore.getTable('team');
					    var records = teamTable.query();

					    for(var f = 0; f < records.length; f += 1){

					    	var name = records[0].get('display_name'),
					    		id  = records[0].get('user_id'),
					    		lat = records[0].get('lat'),
					    		lon = records[0].get('lon');

					    	people.push({
					    		display_name : name,
					    		user_id : id,
					    		latitude : lat,
					    		longitude : lon
					    	});

					    }

					    console.log(people);

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
						//getStatus();
						startGeo();					}

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