document.addEventListener('DOMContentLoaded', function() {
  var movieContainer = document.getElementById('movie-container');

  function fetchMoviePosterUrl(movieTitle, callback) {
    const apiKey = 'c5f6d4cd65047ebc960cf91daa622c4c';

    // Extract title by removing the year and any trailing whitespace
    const titleOnly = movieTitle.replace(/\(\d{4}\)\s*$/, '').trim();

    const queryUrl = `https://api.themoviedb.org/3/search/movie?api_key=${apiKey}&query=${encodeURIComponent(titleOnly)}`;

    fetch(queryUrl)
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0 && data.results[0].poster_path) {
                const posterPath = data.results[0].poster_path;
                const posterUrl = `https://image.tmdb.org/t/p/w500${posterPath}`;
                callback(posterUrl);
            } else {
                callback('/static/placeholder.jpg'); // Default placeholder if no poster is found
            }
        })
        .catch(error => {
            console.error('Error fetching poster from TMDb:', error);
            callback('/static/placeholder.jpg'); // Default placeholder in case of error
        });
    }


    function createMovieCard(movie) {
        var card = document.createElement('div');
        card.className = 'movie-card';
    
        var image = document.createElement('img');
        image.className = 'movie-image';
    
        fetchMoviePosterUrl(movie.title, function(posterUrl) {
            image.src = posterUrl !== 'default_poster_url' ? posterUrl : '/static/placeholder.jpg';
        });
    
        var info = document.createElement('div');
        info.className = 'movie-info';
    
        var titleLink = document.createElement('a');
        titleLink.href = `https://www.google.com/search?q=${encodeURIComponent(movie.title)}`; // Google search link
        titleLink.target = '_blank'; // Open in a new tab
        titleLink.className = 'movie-title-link';
        titleLink.innerHTML = movie.title;
    
        var rating = document.createElement('div');
        rating.className = 'movie-rating';
        rating.innerHTML = movie.rating;
    
        var details = document.createElement('div');
        details.className = 'movie-details';
        details.innerHTML = movie.details;
    
        info.appendChild(titleLink);
        info.appendChild(rating);
        info.appendChild(details);
        card.appendChild(image);
        card.appendChild(info);
    
        return card;
    }
    

    function createSimpleMovieCard(movie) {
        var card = document.createElement('div');
        card.className = 'simple-movie-card'; // Different class for different styling
    
        var image = document.createElement('img');
        image.className = 'movie-image';
    
        fetchMoviePosterUrl(movie.title, function(posterUrl) {
            image.src = posterUrl !== 'default_poster_url' ? posterUrl : '/static/placeholder.jpg';
        });
    
        var info = document.createElement('div');
        info.className = 'movie-info';
    
        var title = document.createElement('div');
        title.className = 'movie-title';
        title.innerHTML = movie.title;
    
        var details = document.createElement('div');
        details.className = 'movie-details';
        details.innerHTML = 'Genre: ' + movie.genre; // Display genre
    
        info.appendChild(title);
        info.appendChild(details); // Only append title and details (genre)
    
        card.appendChild(image);
        card.appendChild(info);
    
        return card;
    }
    

    function showModal(chosenMovie, recommendedMovies) {
        var modal = document.createElement('div');
        modal.className = 'modal';
    
        var modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
    
        // Close button
        var closeBtn = document.createElement('span');
        closeBtn.className = 'close';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        };
        modalContent.appendChild(closeBtn);
    
        // Display the chosen movie
        var chosenMovieElem = createSimpleMovieCard(chosenMovie); // Use createMovieCard for chosen movie
        modalContent.appendChild(chosenMovieElem);
    
        // Separator
        var separator = document.createElement('hr');
        modalContent.appendChild(separator);
    
        // Display recommended movies
        var recommendationsContainer = document.createElement('div');
        recommendationsContainer.className = 'recommendations-container';

        recommendedMovies.forEach(movie => {
            var movieCard = createSimpleMovieCard({ 
                title: movie.title, 
                genre: movie.genre // Assuming genre is a property of the movie object
            });
            recommendationsContainer.appendChild(movieCard);
        });

        modalContent.appendChild(recommendationsContainer);
        modal.appendChild(modalContent);
        document.body.appendChild(modal);
        modal.style.display = 'block';
    }
    
    // Fetch fan favorite movies from Flask and create movie cards
    fetch('/fan-favorites')
        .then(response => response.json())
        .then(movies => {
            movies.forEach(movie => {
                var movieCard = createMovieCard({ 
                    title: movie.title, 
                    rating: '★★★★★', 
                    details: 'Genre: ' + movie.genre // Correctly accessing the genre property
                });
                movieContainer.appendChild(movieCard);
            });
        });


    document.getElementById('search-button').addEventListener('click', function() {
        var movieTitle = document.getElementById('search-input').value;
        if (movieTitle.length > 2) {
            fetch('/recommend?title=' + encodeURIComponent(movieTitle))
                .then(response => response.json())
                .then(data => {
                    showModal(data.chosenMovie, data.recommendations);
                });
        }
    });

    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            var movieTitle = e.target.value;
            if (movieTitle.length > 2) {
                fetch('/recommend?title=' + encodeURIComponent(movieTitle))
                    .then(response => response.json())
                    .then(data => {
                        showModal(data.chosenMovie, data.recommendations);
                    });
            }
        }
    });
});
