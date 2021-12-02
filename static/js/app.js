$("#load").click(function() {
	$("#load").html("Loading ...");
	let date = $("#date").val();
	$.ajax({
		url: "/pictures",
		type: "get",
		data: {selected_date: date, count: 0},
		dataType: 'html',
		success: function(response) {
			$("#pictures").html(response);
			$("#load").html("Load pictures")
		},
		error: function(xhr) {
			console.log(xhr);
			$("#load").html("Error during load");
		}
	});
});

$("#copy").click(function() {
	$("#copy").html('Loading ...');
	$.ajax({
		url: "/copy",
		type: "get",
		success: function(response) {
			$("#copy").html('Copied successfully');
		},
		error: function(xhr) {
			$("#copy").html('Error during copy');
			console.log(xhr);
		}
	});
});

$("#pictures").on('click', '#load-pagination', function(){
	let count = $(this).attr('data-count')
	let date = $("#date").val();
	$.ajax({
		url:"/pictures",
		type: "get",
		data: {selected_date: date, count: count},
		dataType: 'html',
		success: function(response) {
			$("#load-pagination").remove();
			$("#pictures").append(response);
		},
		error: function(xhr) {
			$("#load-pagination").html('Error')
		}
	});	
});
