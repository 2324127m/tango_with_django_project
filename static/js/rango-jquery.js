// $(document) selects the document object
// Then makes a call to ready() i.e. the complete page is loded
// Then function() will be executed.

// It is typical to wait until doc has finished loading before running JQuery functions
// other side code may begin executing before all HTML elements have been downloaded.

// $("#about-btn").click selects element with id about-btn
// then assigns to the click event the alertfunction
$(document).ready(function() {

    // .click requires function with an event
    $("#about-btn").click( function(event) {
        alert("You clicked the button using JQuery!");
    });

    // .hover requires two functions, one for on hover and one for off.
    $("p").hover( function() {
        // if we changed both the "this"'s to "p", it would change all para elements at same time
        $(this).css('color', 'red');
    },
    function() {
        $(this).css('color', 'blue');
    });

    $("#about-btn").click( function(event) {
        // get html from element with id msg
        msgstr = $("#msg").html();
        // append to it
        msgstr = msgstr + "ooo!!!";
        // then change it
        $("#msg").html(msgstr);
    });
});

