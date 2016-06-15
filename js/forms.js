$(document).ready(function() {

    // set up the tag area
    $("#add").click(function() {

        // do more validation here -- only alphabetic, hyphen, spaces
        // only one hyphen in a row, only one space in a row, must have alphabetic
        // must start and end with alphabetic
        var inputTag = $("#tagname").val().toLowerCase();

        if (inputTag.length > 0) {

            // to try to accomodate other languages, do not do something like "[^a-zA-Z ]"
            if (inputTag.match(/[1234567890~!@#\$\+=%\^&\*\(\)<>,\.\/\?;:[]\{\}\|_]/)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("Tag name contains an illegal character. Try using only letters, spaces, hyphens, and apostrophes.");
                return;
            }

            if (inputTag.match(/  /)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("Tag name cannot contain more than one space in a row.");
                return;
            }

            if (inputTag.match(/''/)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("Tag name cannot contain more than one apostrophe in a row.");
                return;
            }

            if (inputTag.match(/--/)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("Tag name cannot contain more than one hypen in a row.");
                return;
            }

            var id = "tag" + $("#tags").length;
            var type = $("#tagtype").val();
            var removeTagButton = $("<button id=\""+id+"\" class=\"tag remove "+type+"\" value=\""+inputTag+" "+type+"\">"+inputTag+" <span class=\"removetext\">(remove)</span></button>");
            
            removeTagButton.click(function() {

              $(this).remove();
            });
            
            $("#tags").append(removeTagButton);
            addAndRemoveClasses($("#tagnamemessage"), "valid", "invalid");
            $("#tagnamemessage").html("Added tag " + tagname )
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

function addAndRemoveClasses(element, classToAdd, classToRemove) {

    if (element.hasClass(classToRemove)) {

        element.removeClass(classToRemove);
    }

    if (!element.hasClass(classToAdd)) {

        element.addClass(classToAdd);
    }
}


/*
function checkTag(inputTag){

    $.ajax({
        type: "POST",
        url: "/vote/",
        dataType: 'json',
        data: JSON.stringify({ "storyKey": storyKey})
    })
    .done(function( data ) {

        alert( "Vote Cast!!! Count is : " + data['story']['vote_count'] );
        $('.voteCount').text(data['story']['vote_count']);

    });
};
*/


