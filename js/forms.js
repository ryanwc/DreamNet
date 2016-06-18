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

            if (tagNameToGroup[inputTag]) {

                type = tagNameToGroup[inputTag];
            }
            else if (newtag == false){
                
                toggleDisplay($("#newtagquestion"));
                addAndRemoveClasses($("#tagnamemessage"), "valid", "invalid");
                $("#tagnamemessage").html("<br> Gathering information about the new '" + inputTag + "' dream tag... ");
                return;
            }
            else {

                type = $("input:radio[name=tagtype]:checked").val();
            }

            createAndAppendTagButton(inputTag, type);
            
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
}

function createAndAppendTagButton(tagname, type) {

    id = tagname+"Button";

    var removeTagButton = $("<button id=\""+id+"\" class=\"tag remove "+type+"\" value=\""+tagname+"|"+type+"\"><span class=\"dreamtag\">"+tagname+"</span> <span class=\"removetext\">(remove)</span></button>");

    removeTagButton.click(function() {

        $("#tagnamemessage").html("<br> Removed '" + type + ": " +  tagname + "' tag ");
        $(this).remove();
        $("#tagname").focus();
    });

    $("#tags").append(removeTagButton);
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

function validateDream() {

    console.log("validating");

    var date_dreamt = $("#datedreamt").val();
    console.log(date_dreamt);
    var lucidity = $("input:radio[name=lucidity]:checked").val();
    var lucid_reason = $("#lucidreasoninput").val();
    var lucid_length = $("#lucidlength").val();
    var control = $("#control").val();
    var enjoyability = $("#enjoyability").val();
    var title = $("#title").val();
    var description = $("#description").val();
    var tagsdiv = $(".dreamtag");
    var content = $("#content").val();

    var containsError = false;

    if (!validateDate(date_dreamt)) {

         containsError = true;
    }

    if (!validateLucidity(lucidity)) {

         containsError = true;
    }

    if (lucidity == "True") {

        var lucid_reason = $("#lucidreasoninput").val();
        var lucid_length = $("#lucidlength").val();

        if (!validateLucidReason(lucid_reason)) {

            containsError = true;
        }

        if (!validateLucidLength(lucid_length)) {

            containsError = true;
        }
    }

    if (!validateControl(control)) {

        containsError = true;
    }

    if (!validateEnjoyability(enjoyability)) {

        containsError = true;
    }

    if (!validateTitle(title)) {

        containsError = true;
    }

    if (!validateDescription(description)) {

        containsError = true;
    }


    if (!validateTagsAndSetHiddenVal(tagsdiv)) {

        containsError = true;
    }

    if (!validateContent(content)) {

        containsError = true;
    }

    if (containsError) {

        window.alert("One of the values you entered is in the wrong format or contains an error.  Please look for red text near each question for guidance, then revise and re-submit.");
        return false;
    }

    return true;
}

function validateDate(date) {

    if (date.length < 1) {

        return false;
    }

    if (!Date.parse(date)) {

        return false;
    }

    return true;
}

function validateLucidity(lucidity) {

    if (lucidity.length < 1) {

        return false;
    }

    if (lucidity != "False" && lucidity != "True") {

        return false;
    }

    return true;
}

function validateLucidReason(lucid_reason) {

    if (lucid_reason.length < 1) {

        return false;
    }

    if (lucid_reason == "-1") {

        return false;
    }

    if (lucid_reason != "0" && lucid_reason != "1" && lucid_reason != "2" &&
        lucid_reason != "3" && lucid_reason != "4") {

        return false;
    }

    if (lucid_reason == "4") {

        var somethingElse = $("#somethingelse").val();

        if (!validateSomethingElse(somethingElse)) {

            return false;
        }
    }

    return true;
}

function validateSomethingElse(somethingElse) {

    if (somethingElse.length < 1) {

        return false;
    } 

    if (somethingElse.length < 300) {

        return false;
    }

    return true;
}

function validateLucidLength(lucid_length) {


    if (lucid_length.length < 1) {

        return false;
    }

    if (lucid_length == "-1") {

        return false;
    }

    if (lucid_length != "0" && lucid_length != "1" && lucid_length != "2") {

        return false;
    }

    return true;
}

function validateControl(control) {


    if (control.length < 1) {

        return false;
    }

    if (control != "0" && control != "1" && control != "2" && control != "3" && 
        control != "4" && control != "5" && control != "6" && control != "7" && 
        control != "8" && control != "9" && control != "10") {

        return false;
    }

    return true;
}

// could be same function as validateControl
// but then could generalize that further to "validate slider"
// that takes val and ranges and steps
// like "for choice in range; step++; {if val return true} if complete return false"
function validateEnjoyability(enjoyability) {

    if (enjoyability.length < 1) {

        return false;
    }

    if (enjoyability != "0" && enjoyability != "1" && enjoyability != "2" && 
        enjoyability != "3" && enjoyability != "4" && enjoyability != "5" && 
        enjoyability != "6" && enjoyability != "7" && enjoyability != "8" && 
        enjoyability != "9" && enjoyability != "10") {

        return false;
    }

    return true;
}

function validateTitle(title) {

    if (title.length < 1) {

        return false;
    }

    if (title.length > 50) {

        return false;
    }

    return true;
}

function validateDescription(description) {

    if (description.length < 1) {

        return false;
    }

    if (description.length > 300) {

        return false;
    }

    return true;
}

function validateTagsAndSetHiddenVal(tagsdiv) {

    $("#dreamtags").val("");

    tagsdiv.each(function() {

        tagtext = $(this).html();

        if (tagtext.length < 1) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("<br> There is an empty tag. Remove it and try again. ");
            return false;       
        }

        if (tagtext.length > 50) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("<br> Tag '"+tagtext+"' is too long. Remove it and try again. ");
            return false;
        }

        if (tagtext.match(/[1234567890~!@#\$\+=%\^&\*\(\)<>,\.\/\?;:\[\]\{\}\|_\\]/)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("<br> Tag '"+tagtext+"' contains an illegal character. Try using only letters, spaces, hyphens, and apostrophes. ");
            return false;
        }

        if (tagtext.match(/  /)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("<br> Tag '"+tagtext+"' cannot contain more than one space in a row. Remove it and try again. ");
            return false;
        }

        if (tagtext.match(/''/)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("<br> Tag '"+tagtext+"' cannot contain more than one apostrophe in a row. Remove it and try again. ");
            return false;
        }

        if (tagtext.match(/--/)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("<br> Tag '"+tagtext+"' cannot contain more than one hypen in a row. Remove it and try again. ");
            return false;
        }

        $("#dreamtags").val() = $("#dreamtags").val() + $(this).val() + ",";
    });
  
    return true;
}

function validateContent(content) {

    if (content.length < 1) {

        return false;
    }

    if (content.length > 50000) {

        return false;
    }

    return true;
}

