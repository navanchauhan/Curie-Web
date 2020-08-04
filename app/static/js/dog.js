var animation = bodymovin.loadAnimation({
    container: document.getElementById('dog'),
        
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: "static/js/Dog.json"
        
    // Make sure your path has the same filename as your animated     SVG's JSON file //
    })