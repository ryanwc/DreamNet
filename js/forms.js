function readyTags(tagNameToGroup, tagGroupToName) {

    // set up the tag area
    $("#add").click(function() {

        var newtag = false;
        var needsIdentifier = false;

        // if the #newtagquestion is displayed, the user already tried to enter a tag, but
        // it wasn't in our system yet, so prompted them to tell us more about the tag,
        // then click "add" again.
        // if this condition is false, it might be set to true in the code below if it is a tag
        // we do not have in the system.
        if (!$("#newtagquestion").hasClass("displaynone")) {

            newtag = true;
            $("#chosentaggroup").html($("input:radio[name=tagtype]:checked").val());
            toggleDisplay($("#newtagquestion"));
        }

        if (!$("#tagidentifiers").hasClass("displaynone")) {

            needsIdentifier = true;
            $("#chosentagidentifier").html($("input:radio[name=tagidentifier]:checked").val());
            toggleDisplay($("#tagidentifiers"));
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

            var tagGroup;

            // if the tag name exists, assign the tag group
            // if not, check if we know about its group yet, and if not, ask about its group
            // if so, get the group already input
            if (tagNameToGroup[inputTag]) {

                tagGroup = tagNameToGroup[inputTag];
            }
            else if (newtag == false && $("#chosentaggroup").html() == "none") {
                
                toggleDisplay($("#newtagquestion"));
                $("#defaulttagtype").prop("checked", true);
                addAndRemoveClasses($("#tagnamemessage"), "valid", "invalid");
                $("#tagnamemessage").html("Gathering information about the new '" + inputTag + "' dream tag... ");
                return;
            }
            else {

                tagGroup = $("#chosentaggroup").html();
            }

            var identifier;

            // if it needs an identifier, ask for it
            if ( (tagGroup == "object" || tagGroup == "place" ||
                  tagGroup == "being" || tagGroup == "emotion") &&
                needsIdentifier == false) {

                toggleDisplay($("#tagidentifiers"));
                $("#defaulttagidentifier").prop("checked", true);
                $("#tagtobeidentified").html("'"+inputTag+"' "+tagGroup);
                addAndRemoveClasses($("#tagnamemessage"), "valid", "invalid");
                $("#tagnamemessage").html("Getting identifier for the '" + inputTag + "' dream tag... ");
                return;  
            }
            else {

                identifier = $("#chosentagidentifier").html();
            }

            // create the tag button and then reset everything
            createAndAppendTagButton(inputTag, tagGroup, identifier);
            
            $("#chosentaggroup").html("none");
            $("#chosentagidentifier").html("none");          
            addAndRemoveClasses($("#tagnamemessage"), "valid", "invalid");
            $("#tagnamemessage").html("Added the '" + tagGroup + ": " + inputTag + "' tag ");
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

    if ($("input:radio[name=lucidity]:checked").val() == "True") {

        toggleLucidQuestions();
    }
}

function createAndAppendTagButton(tagname, type, identifier) {

    var id = tagname+"Button";

    var identifierText;

    switch (identifier) {

        case "definite":
            identifierText = "(the)";
            break;
        case "indefinite":
            identifierText = "(a(n)/another's)";
            break;
        case "possesive":
            identifierText = "(my)";
            break;
        default:
            identifierText = "";
            identifier = "none";
            break;
    }

    var removeTagButton = $("<button id=\""+id+"\" class=\"tag tagbutton remove "+type+"\" value=\""+tagname+"|"+identifier+"@"+type+"\"><span class=\"dreamtag\">"+identifierText+" "+tagname+"</span> <span class=\"removetext\">(remove)</span></button>");

    removeTagButton.click(function() {

        $("#tagnamemessage").html("Removed '" + type + ": " +  tagname + "' tag ");
        $(this).remove();
        $("#tagname").focus();
    });

    $("#tags").append(removeTagButton);
}

function hide(element) {

    if (!element.hasClass("displaynone")) {

        element.addClass("displaynone");
    }
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

function toggleSomethingElse() {

    if ($("#lucidreason").val() == "something else") {

        $("#somethingelse").removeClass("displaynone");
    }
    else {

        if (!$("#somethingelse").hasClass("displaynone")) {

          $("#somethingelse").addClass("displaynone");
        }
    }
}

function toggleSpecificCheck() {

    if ($("input:radio[name=dreamsignbool]:checked").val() == "True") {

        addAndRemoveClasses($("#dreamsignquestion"), "", "displaynone");
        addAndRemoveClasses($("#realitycheckquestion"), "displaynone", "");
    }
    else if ($("input:radio[name=dreamsignbool]:checked").val() == "False") {

        addAndRemoveClasses($("#dreamsignquestion"), "displaynone", "");
        addAndRemoveClasses($("#realitycheckquestion"), "", "displaynone");
    }
}

function toggleOtherRealityCheck() {

    if ($("#realitycheck").val() == "4") {

        $("#otherrealitycheck").removeClass("displaynone");
    }
    else {

        if (!$("#otherrealitycheck").hasClass("displaynone")) {

          $("#otherrealitycheck").addClass("displaynone");
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

function validateUser(satisfactionAreas) {

    var username = $("#username").val();
    var password = $("#password").val();
    var verifyPassword = $("#verifypassword").val();
    var gender = $("#gender").val();
    var birthdate = $("#birthdate").val();
    var nationality = $("#nationality").val();
    var residence = $("#residence").val();
    var area = $("#area").val();
    var email = $("#email").val();
    var profession = $("#profession").val();
    var industry = $("#industry").val();
    var sector = $("#sector").val();
    var education_level = $("#education").val();
    var isParent = $("#isparent").val();
    var isCommitted = $("#iscommitted").val();

    // does not verify all that should be present are present, but verifies the ones that are
    var satisfaction_rating_input_divs = $(".ratingareaslider");
    var thisRating;
    satisfaction_rating_input_divs.each(function() {

        thisRating = $(this).val();

        //if (!validate)
    });


}

function validateDream() {

    var date_dreamt = $("#datedreamt").val();
    var lucidity = $("input:radio[name=lucidity]:checked").val();
    var lucid_reason = $("#lucidreason").val();
    var lucid_length = $("#lucidlength").val();
    var control = $("#control").val();
    var enjoyability = $("#enjoyability").val();
    var title = $("#title").val();
    var description = $("#description").val();
    var tagButtonClass = $(".tagbutton");
    var content = $("#content").val();

    var containsError = false;

    if (!validateDate(date_dreamt)) {

         containsError = true;
    }

    if (!validateLucidity(lucidity)) {

         containsError = true;
    }

    if (lucidity == "True") {

        var lucid_reason = $("#lucidreason").val();
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

    if (!validateTagsAndSetHiddenVal(tagButtonClass)) {

        containsError = true;
    }

    validateTagsAndSetHiddenVal(tagButtonClass)

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

    $("#datedreamtmessageprefix").html("<br>");

    if (date.length < 1) {

        addAndRemoveClasses($("#datedreamtmessage"), "invalid", "valid");
        $("#datedreamtmessage").html("Please enter the date you had the dream.");
        return false;
    }

    if (!Date.parse(date)) {

        addAndRemoveClasses($("#datedreamtmessage"), "invalid", "valid");
        $("#datedreamtmessage").html("Date dreamt is in wrong format.");
        return false;
    }

    addAndRemoveClasses($("#datedreamtmessage"), "valid", "invalid");
    $("#datedreamtmessage").html("Date dreamt OK.");
    return true;
}

function validateLucidity(lucidity) {

    $("#luciditymessageprefix").html("<br>");

    if (typeof lucidity == 'undefined') {

        addAndRemoveClasses($("#luciditymessage"), "invalid", "valid");
        $("#luciditymessage").html("Please indicate whether you were aware you were dreaming at any point during the dream.");
        return false;
    }

    if (lucidity.length < 1) {

        addAndRemoveClasses($("#luciditymessage"), "invalid", "valid");
        $("#luciditymessage").html("Please indicate whether you were aware you were dreaming at any point during the dream.");
        return false;
    }

    if (lucidity != "False" && lucidity != "True") {

        addAndRemoveClasses($("#luciditymessage"), "invalid", "valid");
        $("#luciditymessage").html("Please select either 'Yes' or 'No'.");
        return false;
    }

    addAndRemoveClasses($("#luciditymessage"), "valid", "invalid");
    $("#luciditymessage").html("Lucidity answer OK.");
    return true;
}

function validateLucidReason(lucid_reason) {

    $("#lucidreasonmessageprefix").html("<br>");

    if (lucid_reason.length < 1) {

        // HAS TWO BREAKS AFTER MESSAGE TO MAKE 'somethingelse' BOX NICELY SPACED IF IT'S THERE
        addAndRemoveClasses($("#lucidreasonmessage"), "invalid", "valid");
        $("#lucidreasonmessage").html("Please indicate how you became aware you were dreaming.<br><br>");
        return false;
    }

    if (lucid_reason == "-1") {

        addAndRemoveClasses($("#lucidreasonmessage"), "invalid", "valid");
        $("#lucidreasonmessage").html("<br>  Please indicate how you became aware you were dreaming. ");
        return false;
    }

    if (lucid_reason != "0" && lucid_reason != "1" && lucid_reason != "2" &&
        lucid_reason != "3" && lucid_reason != "4") {

        addAndRemoveClasses($("#lucidreasonmessage"), "invalid", "valid");
        $("#lucidreasonmessage").html("<br>  Please indicate how you became aware you were dreaming. ");
        return false;
    }

    if (lucid_reason == "4") {

        var somethingElse = $("#somethingelse").val();

        if (!validateSomethingElse(somethingElse)) {

            return false;
        }
    }

    addAndRemoveClasses($("#lucidreasonmessage"), "invalid", "valid");
    $("#lucidreasonmessage").html("<br>  Lucid reason OK. ");
    return true;
}

function validateSomethingElse(somethingElse) {

    $("#somethingelsemessageprefix").html("<br>");

    if (somethingElse.length < 1) {

        addAndRemoveClasses($("#somethingelsemessage"), "invalid", "valid");
        $("#somethingelsemessage").html("<br>  Please enter your own reason you became aware you were dreaming. ");
        return false;
    } 

    if (somethingElse.length > 300) {

        addAndRemoveClasses($("#somethingelsemessage"), "invalid", "valid");
        $("#somethingelsemessage").html("The reason you became aware you were dreaming is too long (max 300 chars).");
        return false;
    }

    addAndRemoveClasses($("#somethingelsemessage"), "valid", "invalid");
    $("#somethingelsemessage").html("Your reason for becoming aware you were dreaming is OK.");
    return true;
}

function validateLucidLength(lucid_length) {

    $("#lucidlengthmessageprefix").html("<br>");

    if (lucid_length.length < 1) {

        addAndRemoveClasses($("#lucidlengthmessage"), "invalid", "valid");
        $("#lucidlengthmessage").html("Please indicate how long you remained aware you were dreaming.");
        return false;
    }

    if (lucid_length == "-1") {

        addAndRemoveClasses($("#lucidlengthmessage"), "invalid", "valid");
        $("#lucidlengthmessage").html("Please indicate how long you remained aware you were dreaming.");
        return false;
    }

    if (lucid_length != "0" && lucid_length != "1" && lucid_length != "2") {

        addAndRemoveClasses($("#lucidlengthmessage"), "invalid", "valid");
        $("#lucidlengthmessage").html("Please indicate how long you remained aware you were dreaming.");
        return false;
    }

    addAndRemoveClasses($("#lucidlengthmessage"), "valid", "invalid");
    $("#lucidlengthmessage").html("Awareness length OK.");
    return true;
}

function validateControl(control) {

    if (control.length < 1) {

        addAndRemoveClasses($("#controlmessage"), "invalid", "valid");
        $("#controlmessage").html("Please indicate the level of control you felt over your actions and the 'narrative' of the dream.");
        return false;
    }

    if (control != "0" && control != "1" && control != "2" && control != "3" && 
        control != "4" && control != "5" && control != "6" && control != "7" && 
        control != "8" && control != "9" && control != "10") {

        addAndRemoveClasses($("#controlmessage"), "invalid", "valid");
        $("#controlmessage").html("Control level had an invalid value.  Please set control level using the slider.");
        return false;
    }

    addAndRemoveClasses($("#controlmessage"), "valid", "invalid");
    $("#controlmessage").html("Control level OK.");
    return true;
}

// could be same function as validateControl
// but then could generalize that further to "validate slider"
// that takes val and ranges and steps
// like "for choice in range; step++; {if val return true} if complete return false"
function validateEnjoyability(enjoyability) {

    if (enjoyability.length < 1) {

        addAndRemoveClasses($("#enjoyabilitymessage"), "invalid", "valid");
        $("#enjoyabilitymessage").html("<br>  Please rate how enjoyable the dream was. ");
        return false;
    }

    var rating = parseInt(enjoyability);

    // will return false if NaN
    if (rating < 0 || rating > 10) {

        addAndRemoveClasses($("#enjoyabilitymessage"), "invalid", "valid");
        $("#enjoyabilitymessage").html("Please rate how enjoyable the dream was.");
        return false;
    }

    addAndRemoveClasses($("#enjoyabilitymessage"), "valid", "invalid");
    $("#enjoyabilitymessage").html("Enjoyability OK.");
    return true;
}

function validateTitle(title) {

    $("#titlemessageprefix").html("<br>");

    if (title.length < 1) {

        addAndRemoveClasses($("#titlemessage"), "invalid", "valid");
        $("#titlemessage").html("Please enter a title for the dream.");
        return false;
    }

    if (title.length > 50) {

        addAndRemoveClasses($("#titlemessage"), "invalid", "valid");
        $("#titlemessage").html("Title is too long (max 50 chars).");
        return false;
    }

    addAndRemoveClasses($("#titlemessage"), "valid", "invalid");
    $("#titlemessage").html("Title OK.");
    return true;
}

function validateDescription(description) {

    $("#descriptionmessageprefix").html("<br>");

    if (description.length < 1) {

        addAndRemoveClasses($("#descriptionmessage"), "invalid", "valid");
        $("#descriptionmessage").html("Please enter a short description of the dream.");
        return false;
    }

    if (description.length > 300) {

        addAndRemoveClasses($("#descriptionmessage"), "invalid", "valid");
        $("#descriptionmessage").html("Dream description is too long (max 300 chars).");
        return false;
    }

    addAndRemoveClasses($("#descriptionmessage"), "valid", "invalid");
    $("#descriptionmessage").html("Description OK.");
    return true;
}

function validateTagsAndSetHiddenVal(tagButtonClass) {

    $("#dreamtags").val("");

    var hasTypeTag = false;

    $("#tagnamemessageprefix").html("<br>");

    tagButtonClass.each(function() {

        tagtext = $(this).find(".dreamtag").html();

        if (tagtext.length < 1) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("There is an empty tag. Remove it and try again.");
            return false;       
        }

        if (tagtext.length > 50) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("Tag '"+tagtext+"' is too long. Remove it and try again.");
            return false;
        }

        if (tagtext.match(/[1234567890~!@#\$\+=%\^&\*\(\)<>,\.\/\?;:\[\]\{\}\|_\\]/)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("Tag '"+tagtext+"' contains an illegal character. Try using only letters, spaces, hyphens, and apostrophes.");
            return false;
        }

        if (tagtext.match(/  /)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("Tag '"+tagtext+"' cannot contain more than one space in a row. Remove it and try again.");
            return false;
        }

        if (tagtext.match(/''/)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("Tag '"+tagtext+"' cannot contain more than one apostrophe in a row. Remove it and try again.");
            return false;
        }

        if (tagtext.match(/--/)) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("Tag '"+tagtext+"' cannot contain more than one hypen in a row. Remove it and try again.");
            return false;
        }

        if (!$(this).hasClass("type") && !$(this).hasClass("being") &&
            !$(this).hasClass("place") && !$(this).hasClass("object") &&
            !$(this).hasClass("emotion") && !$(this).hasClass("sensation")) {

            addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
            $("#tagnamemessage").html("Tag '"+tagtext+"'. Try removing and re-adding it.");
            return false;           
        }
        
        if ($(this).hasClass("type")) {

            hasTypeTag = true;
        }

        newval = $("#dreamtags").val() + $(this).val() + ",";
        $("#dreamtags").val(newval);
    });
  
    if (!hasTypeTag) {

        addAndRemoveClasses($("#tagnamemessage"), "invalid", "valid");
        $("#tagnamemessage").html("Please provide at least one 'type' tag.");
        return false;             
    }

    addAndRemoveClasses($("#tagnamemessage"), "valid", "invalid");
    $("#tagnamemessage").html("Dream tags OK.");
    return true;
}

function validateContent(content) {

    $("#contentmessageprefix").html("<br>");

    if (content.length < 1) {

        addAndRemoveClasses($("#contentmessage"), "invalid", "valid");
        $("#contentmessage").html("Please write an (as in-depth as possible) account of what happened during the dream.  This can be in whatever form you like, but it may be easiest to write the dream like a story.");
        return false;
    }

    if (content.length > 50000) {

        addAndRemoveClasses($("#contentmessage"), "invalid", "valid");
        $("#contentmessage").html("Dream narrative is too long (max 50,000 chars).");
        return false;
    }

    addAndRemoveClasses($("#contentmessage"), "valid", "invalid");
    $("#contentmessage").html("Dream narrative OK.");
    return true;
}

function resetMessage(inputName) {

    $("#"+inputName+"message").html("");
    $("#"+inputName+"messageprefix").html("");

    addAndRemoveClasses($("#"+inputName+"message"), "", "valid");
    addAndRemoveClasses($("#"+inputName+"message"), "", "invalid");
}

function toggleRealityCheckTags(tagNameToGroup) {

    var selectedMechanism = $("#mechanism").val();

    // have competing conditions with slow updates to DOM 
    // so set booleans instead of, e.g., testing hasClass
    var displayObjectList = false;
    var displayEndIdentifier = false;
    var displayFirstEnd = false;
    var displaySecondEnd = false;
    var displayIdentifier = false;
    var displayAllCheckList = false;
    var extraMechanismText = "";
    var extraTagText = "";

    // for fine grain control have different cases for each option
    switch (selectedMechanism) {
        // some cases do some of the same things
        case 'malfunction':
            displayObjectList = true;
            displayAllCheckList = false;
            displayIdentifier = false;
            displayEndIdentifier = true;
            displayFirstEnd = false;
            displaySecondEnd = true;
            extraMechanismText = "";
            break;
        case 'impossibility/oddity':
            displayObjectList = false;
            displayAllCheckList = true;
            displayIdentifier = true;
            displayEndIdentifier = false;
            displayFirstEnd = true;
            displaySecondEnd = false;
            extraMechanismText = " involving ";
            break;
        case 'presence':
            displayObjectList = false;
            displayAllCheckList = true;
            displayIdentifier = true;
            displayEndIdentifier = false;
            displayFirstEnd = true;
            displaySecondEnd = false; 
            extraMechanismText = "";
            break;
        case 'absence':
            displayObjectList = false;
            displayAllCheckList = true;
            displayIdentifier = true;
            displayEndIdentifier = false;
            displayFirstEnd = true;
            displaySecondEnd = false; 
            extraMechanismText = "";
            break;
        case '-1':
            displayObjectList = false;
            displayAllCheckList = false;
            displayIdentifier = false;
            displayEndIdentifier = false;
            displayFirstEnd = true;
            displaySecondEnd = false; 
            extraMechanismText = "";
            break;          
        default:
            displayObjectList = false;
            displayAllCheckList = false;
            displayIdentifier = false;
            displayEndIdentifier = false;
            displayFirstEnd = true;
            displaySecondEnd = false; 
            extraMechanismText = "";
            break;
    }

    // if did not choose 'malfunction'
    if (selectedMechanism == "presence" ||
        selectedMechanism == "absence" ||
        selectedMechanism == "impossibility/oddity") {

        var selectedPhenomenon = $("#allcheck").val();

        // have case for each option for fine grain control
        switch (tagNameToGroup[selectedPhenomenon]) {

            case 'type':
                displayIdentifier = false;
                displayEndIdentifier = false;
                displayFirstEnd = true;
                displaySecondEnd = false;
                extraTagText = " themes/activities";
                break;
            case 'place':
                extraTagText = "";
                break;
            case 'object':
                displayIdentifier = false;
                displayEndIdentifier = true;
                displayFirstEnd = false;
                displaySecondEnd = true;
                extraTagText = "";
                break;
            case 'being':
                extraTagText = "";
                break;
            case 'emotion':
                displayIdentifier = false;
                displayEndIdentifier = true;
                displayFirstEnd = false;
                displaySecondEnd = true;
                extraTagText = "";
                break;
            case 'sensation':
                displayIdentifier = false;
                displayEndIdentifier = false;
                displayFirstEnd = true;
                displaySecondEnd = false;
                extraTagText = " sensations";
                break;
            default:
                extraTagText = "";
                break;
        }
    }

    if (displayObjectList) {

        addAndRemoveClasses($("#objectmalfunction"), "", "displaynone");
    }
    else {

        addAndRemoveClasses($("#objectmalfunction"), "displaynone", "");
    }

    if (displayAllCheckList) {

        addAndRemoveClasses($("#allcheck"), "", "displaynone"); 
    }
    else {

        addAndRemoveClasses($("#allcheck"), "displaynone", ""); 
    }

    if (displayIdentifier) {

        addAndRemoveClasses($("#identifier"), "", "displaynone"); 
    }
    else {

        addAndRemoveClasses($("#identifier"), "displaynone", ""); 
    }

    if (displayEndIdentifier) {

        addAndRemoveClasses($("#endidentifier"), "", "displaynone"); 
    }
    else {

        addAndRemoveClasses($("#endidentifier"), "displaynone", ""); 
    }

    if (displayFirstEnd) {

        addAndRemoveClasses($("#firstend"), "", "displaynone"); 
    }
    else {

        addAndRemoveClasses($("#firstend"), "displaynone", ""); 
    }

    if (displaySecondEnd) {

        addAndRemoveClasses($("#secondend"), "", "displaynone"); 
    }
    else {

        addAndRemoveClasses($("#secondend"), "displaynone", ""); 
    }

    $("#extramechanismtext").html(extraMechanismText);  
    $("#extratagtext").html(extraTagText);
}

function togglePhenomenon(tagNameToGroup) {

    var selectedRCTag = $("#allcheck").val();

    switch (tagNameToGroup[selectedRCTag]) {

        case 'type':
            addAndRemoveClasses($("#identifier"), "displaynone", ""); 
            addAndRemoveClasses($("#endidentifier"), "displaynone", ""); 
            addAndRemoveClasses($("#firstend"), "", "displaynone"); 
            addAndRemoveClasses($("#secondend"), "displaynone", ""); 
            $("#extratagtext").html(" themes/activities");
            break;
        case 'emotion':
            addAndRemoveClasses($("#identifier"), "displaynone", ""); 
            addAndRemoveClasses($("#endidentifier"), "", "displaynone"); 
            addAndRemoveClasses($("#firstend"), "displaynone", ""); 
            addAndRemoveClasses($("#secondend"), "", "displaynone");
            $("#extratagtext").html("");
            break;
        case 'sensation':
            addAndRemoveClasses($("#identifier"), "displaynone", ""); 
            addAndRemoveClasses($("#endidentifier"), "displaynone", ""); 
            addAndRemoveClasses($("#firstend"), "", "displaynone"); 
            addAndRemoveClasses($("#secondend"), "displaynone", "");
            $("#extratagtext").html(" sensations");
            break;
        default:
            addAndRemoveClasses($("#identifier"), "", "displaynone"); 
            addAndRemoveClasses($("#endidentifier"), "displaynone", ""); 
            addAndRemoveClasses($("#firstend"), "", "displaynone"); 
            addAndRemoveClasses($("#secondend"), "displaynone", "");
            $("#extratagtext").html("");
            break;
    }
}

function toggleProfessionQuestions() {

    var profession = $("#profession").val();

    switch (profession) {

        case 'Student':
            addAndRemoveClasses($("#sectorquestion"), "", "displaynone");
            addAndRemoveClasses($("#industryquestion"), "displaynone", "");
            break;
        case 'Unemployed':
            addAndRemoveClasses($("#sectorquestion"), "displaynone", "");
            addAndRemoveClasses($("#industryquestion"), "displaynone", "");
            break;
        case 'Retired':
            addAndRemoveClasses($("#sectorquestion"), "displaynone", "");
            addAndRemoveClasses($("#industryquestion"), "displaynone", "");
            break;
        default:
            addAndRemoveClasses($("#sectorquestion"), "", "displaynone");
            addAndRemoveClasses($("#industryquestion"), "", "displaynone");
            break;
    }
}

function toggleSomethingSpecific() {

    var specificQs = $(".somethingspecificquestion");

    if ($("#lucidreason").val() == "reality check") {

        specificQs.each(function() {

            addAndRemoveClasses($(this), "", "displaynone");
        });
    }
    else {

        specificQs.each(function () {

            addAndRemoveClasses($(this), "displaynone", "");
        });

        // if there are any dream signs, make user select yes or no dream sign again
        if ($("#dreamsign").children("option").length > 1) {
         
            $("input:radio[name=dreamsignbool]:checked").prop("checked", false);
        }

        addAndRemoveClasses($("#dreamsignquestion"), "displaynone", "");
        addAndRemoveClasses($("#realitycheckquestion"), "displaynone", "");
    }
}

