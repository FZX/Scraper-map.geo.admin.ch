$(document).ready(function(){

    function post_address(callback) {
        $.ajax({
            url: "/check_address",
            method: "POST",
            data: {keyword: $("#search_text").val()},
            success: callback

        });
    }

    function update_data(data) {
        if (data.status === "success"){
            $("#panel-body").load("./ #table");
            $("#panel-footer").load("./ #footer-row");
            toggle_i_class($("#search"));
            $("#search_text").val("");
        }
    }

    function toggle_i_class(button) {
        if ($(button).find("i").hasClass("fa fa-search")) {
            $(button).find("i").removeClass("fa fa-search").addClass("fa fa-spinner fa-spin")
        }else{
            $(button).find("i").removeClass("fa fa-spinner fa-spin").addClass("fa fa-search")
        }

    }

    $("#search").on("click", function(e){
        e.preventDefault();
        if ($("#search_text").val().length > 0){
            console.log("I am here ");
            toggle_i_class(this);
            post_address(update_data); 
        }

    });

});
