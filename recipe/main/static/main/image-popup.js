$(document).ready(function() {

  $("#recipe-img").on('click', function() {
    w2popup.open({
      title: `${document.querySelector("#recipe-title").innerHTML}`,
      body: '<div class="w2ui-centered"><img src="' + $(this).attr('src') + '"></img></div>',
      width: Math.max(this.width, 1200),
      height: Math.max(this.height, 1000)
    });
  });

});