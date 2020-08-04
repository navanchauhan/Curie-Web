var animation = bodymovin.loadAnimation({
    container: document.getElementById('discovery'),
        
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: "static/js/Discovery.json"
        
    // Make sure your path has the same filename as your animated     SVG's JSON file //
    })