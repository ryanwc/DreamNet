$(document).ready(function() {
    $("#add").click(function() {
      var id = "tag" + $("#tags").length;
      var tag = $("#tagname").val();
      var type = $("#tagtype").val();
      var removeTagButton = $("<button id=\""+id+"\" class=\"tag remove "+type+"\" value=\""+tag+" "+type+"\">"+tag+" <span class=\"removetext\">(remove)</span></button>");
      
      removeTagButton.click(function() { 
        $(this).remove();
      });
      
      $("#tags").append(removeTagButton);
    });
});