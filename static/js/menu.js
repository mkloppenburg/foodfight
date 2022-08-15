// Credits to: https://bootstrapious.com/p/bootstrap-sidebar
$(document).ready(function() {
    $("#sidebar").mCustomScrollbar({
        theme: "minimal"
    });
    // toggle the sidebar with an onclick
    $('#sidebarCollapse').on('click', function() {
        $('#sidebar, #content').toggleClass('active');
        $('.collapse.in').toggleClass('in');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });
});