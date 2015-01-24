var __db = (function(){

	function addEvents(){

		options = {
		    success: function(files) {
		    	console.log(files);

		    	var chosenFile = files[0].link;

		    	console.log(chosenFile);

		    	jQuery.ajax({
		    		type : "GET",
		    		url : "/chosen-one/" + chosenFile,

		    		success : function(res){

		    			console.log(res);

		    		},
		    		error : function(err){

		    			console.log(err);

		    		}
		    	});

		    },
		    cancel: function() {

		    },
		    linkType: "direct",
		    multiselect: false, // or true
		    extensions: ['.png', '.jpg', '.gif'],
		};

		var button = Dropbox.createChooseButton(options);

		document.getElementById("container").appendChild(button);


	}

	function init(){
		addEvents();
	}

	return{
		init : init
	};

})();

(function(){
	__db.init();
})();