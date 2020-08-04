var animation = bodymovin.loadAnimation({
    container: document.getElementById('astronaut'),
        
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: "static/js/Astronaut.json"
        
    // Make sure your path has the same filename as your animated     SVG's JSON file //
    })