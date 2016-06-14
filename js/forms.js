$(document).ready(function() {

    // set up the tag area
    $("#add").click(function() {

      // do more validation here -- only alphabetic, hyphen, spaces
      // only one hyphen in a row, only one space in a row, must have alphabetic
      // must start and end with alphabetic

        if ($("#tagname").val().length > 0) {

            var id = "tag" + $("#tags").length;
            var tag = $("#tagname").val();
            var type = $("#tagtype").val();
            var removeTagButton = $("<button id=\""+id+"\" class=\"tag remove "+type+"\" value=\""+tag+" "+type+"\">"+tag+" <span class=\"removetext\">(remove)</span></button>");
            
            removeTagButton.click(function() {

              $(this).remove();
            });
            
            $("#tags").append(removeTagButton);
            $("#tagname").val("");
        }
    });

    // add tag with pressing enter
    document.getElementById("tagname").addEventListener("keyup", function(event) {
        
        if (event.keyCode == 13) {

            event.preventDefault();
            document.getElementById("add").click();
        }
    });
    document.getElementById("tagname").addEventListener("keydown", function(event) {
        
        if (event.keyCode == 13) {

            event.preventDefault();
        }
    });
    document.getElementById("tagname").addEventListener("keypress", function(event) {
        
        if (event.keyCode == 13) {

            event.preventDefault();
        }
    });
});

function toggleTagtipDisplay(tagtip) {

    if (!tagtip.hasClass("visible")) {

        tagtip.addClass("visible");
    }
    else {

        tagtip.removeClass("visible");
    }
}

function toggleLucidQuestions() {

    if ($("input:radio[name=lucidity]:checked").val() == "False") {

        $(".lucidity").each(function() {

            $(this).addClass("displaynone");
        });
    }
    else {

        $(".lucidity").each(function() {

            $(this).removeClass("displaynone");
        });
    }
}

function displaySomethingElse() {

    if ($("#lucidreasoninput").val() == "4") {

        $("#somethingelse").removeClass("displaynone");
    }
    else {

        if (!$("#somethingelse").hasClass("displaynone")) {

          $("#somethingelse").addClass("displaynone");
        }
    }
}
