var animation = bodymovin.loadAnimation({
    container: document.getElementById('chemical'),
        
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: "static/js/Chemical.json"
        
    // Make sure your path has the same filename as your animated     SVG's JSON file //
    })