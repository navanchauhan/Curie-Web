var animation = bodymovin.loadAnimation({
    container: document.getElementById('growth'),
        
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: "static/js/Growth.json"
        
    // Make sure your path has the same filename as your animated     SVG's JSON file //
    })