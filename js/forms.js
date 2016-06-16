function readyTags(tagNameToGroup, tagGroupToName) {

    // set up the tag area
    $("#add").click(function() {

        var newtag = false;

        // if the #newtagquestion is displayed, the user already tried to enter a tag, but
        // it wasn't in our system yet, so prompted them to tell us more about the tag,
        // then click "add" again.
        // if this condition is false, it might be set to true in the code below if it is a tag
        // we do not have in the system.
        if (!$("#newtagquestion").hasClass("displaynone")) {

            newtag = true;
            toggleDisplay($("#newtagquestion"));
        }
        // keep rest of validation in case user tries to insert weird stuff when newtag=true

        var inputTag = $("#tagname").val().toLowerCase();
        var dreamTags = $(".dreamtag");

        if (inputTag.length > 0) {

            // to try to accomodate other languages, do not do something like "[^a-zA-Z ]"
            if (inputTag.match(/[1234567890~!@#\$\+=%\^&\*\(\)<>,\.\/\?;:\[\]\{\}\|_\\]/)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("<br> Tag name contains an illegal character. Try using only letters, spaces, hyphens, and apostrophes. ");
                return;
            }

            if (inputTag.match(/  /)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("<br> Tag name cannot contain more than one space in a row. ");
                return;
            }

            if (inputTag.match(/''/)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("<br> Tag name cannot contain more than one apostrophe in a row. ");
                return;
            }

            if (inputTag.match(/--/)) {

                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("<br> Tag name cannot contain more than one hypen in a row. ");
                return;
            }

            var type;

            // should verify on backend to that no tags repeated
            var alreadyHave = false;
            dreamTags.each(function() {

                if ($(this).html() == inputTag) {

                    alreadyHave = true;
                    return false;
                }
            });

            if (alreadyHave) {
                addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
                $("#tagnamemessage").html("<br> You already added that tag. ");
                return;
            }

            console.log("wait why");

            if (tagNameToGroup[inputTag]) {

                type = tagNameToGroup[inputTag];
            }
            else if (newtag == false){
                
                toggleDisplay($("#newtagquestion"));
                return;
            }
            else {

                type = $("#tagtype").val();
            }

            var id = inputTag+"Button";

            var removeTagButton = $("<button id=\""+id+"\" class=\"tag remove "+type+"\" value=\""+inputTag+"|"+type+"\"><span class=\"dreamtag\">"+inputTag+"</span> <span class=\"removetext\">(remove)</span></button>");
            
            removeTagButton.click(function() {


                $("#tagnamemessage").html("<br> Removed '" + type + ": " +  inputTag + "' tag ");
                $(this).remove();
                $("#tagname").focus();
            });

            // ensure only clicking the button can remove it
            removeTagButton.keyup(function(event) {
                
                if (event.keyCode == 13) {

                    event.preventDefault();
                    console.log("culprit up");
                }
            });
            removeTagButton.keydown(function(event) {

                if (event.keyCode == 13) {

                    event.preventDefault();
                    console.log("culprit down");
                }
            });
            removeTagButton.keypress(function(event) {

                if (event.keyCode == 13) {
                    event.preventDefault();
                    console.log("culprit press");
                }
            });
            
            $("#tags").append(removeTagButton);
            addAndRemoveClasses($("#tagnamemessage"), "valid", "invalid");
            $("#tagnamemessage").html("<br> Added the '" + type + ": " + inputTag + "' tag ");
            $("#tagname").val("");
            $("#tagname").focus();
        }


    });

    // add tag with pressing enter
    document.getElementById("tagname").addEventListener("keyup", function(event) {
        
        if (event.keyCode == 13) {

            event.preventDefault();
            document.getElementById("add").click();
            console.log("culprit up add");
        }
    });
    document.getElementById("tagname").addEventListener("keydown", function(event) {
        
        if (event.keyCode == 13) {

            event.preventDefault();
            console.log("culprit down add");
        }
    });
    document.getElementById("tagname").addEventListener("keypress", function(event) {
        
        if (event.keyCode == 13) {

            event.preventDefault();
        }
    });
}

function toggleDisplay(element) {

    if (element.hasClass("displaynone")) {

        element.removeClass("displaynone");
    }
    else {

        element.addClass("displaynone");
    }
}

function toggleVisible(element) {

    if (!element.hasClass("visible")) {

        element.addClass("visible");
    }
    else {

        element.removeClass("visible");
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


function getTags(){

    $.ajax({
        type: "POST",
        url: "/tags/JSON",
        dataType: 'json',
        success: function (data, status) {

            alert(data);
        }
    });
};


