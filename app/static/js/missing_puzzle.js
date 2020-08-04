var animation = bodymovin.loadAnimation({
    container: document.getElementById('puzzle'),
        
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: "static/js/Puzzle.json"
        
    // Make sure your path has the same filename as your animated     SVG's JSON file //
    })