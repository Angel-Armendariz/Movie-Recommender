document.addEventListener('DOMContentLoaded', function() {
    // Example data (replace with your Python data fetching)
    var movies = [
        { title: 'Joy Ride', rating: '★★★★☆', details: 'Genre: Comedy<br>Actors/Actresses: Sherry Cola, Stephanie Hsu, etc.' },
        { title: 'Eternal Shadows', rating: '★★★☆☆', details: 'Genre: Drama<br>Actors/Actresses: Chris Pine, Zoe Saldana, etc.' },
        { title: 'Beyond Horizons', rating: '★★★★★', details: 'Genre: Sci-Fi<br>Actors/Actresses: Tom Holland, Brie Larson, etc.' },
        { title: 'Crimson Tide', rating: '★★★☆☆', details: 'Genre: Action<br>Actors/Actresses: Denzel Washington, Gene Hackman, etc.' },
        { title: 'Whispering Corridors', rating: '★★★★☆', details: 'Genre: Horror<br>Actors/Actresses: Kim Seo-hyung, Choi Jung-yoon, etc.' }
      ];
      
  
    var movieContainer = document.getElementById('movie-container');
  
    // Function to create movie card
    function createMovieCard(movie) {
      var card = document.createElement('div');
      card.className = 'movie-card';
  
      var imagePlaceholder = document.createElement('div');
      imagePlaceholder.className = 'movie-image-placeholder';
      
      var info = document.createElement('div');
      info.className = 'movie-info';
  
      var title = document.createElement('div');
      title.className = 'movie-title';
      title.innerHTML = movie.title;
  
      var rating = document.createElement('div');
      rating.className = 'movie-rating';
      rating.innerHTML = movie.rating;
  
      var details = document.createElement('div');
      details.className = 'movie-details';
      details.innerHTML = movie.details;
  
      info.appendChild(title);
      info.appendChild(rating);
      info.appendChild(details);
  
      card.appendChild(imagePlaceholder);
      card.appendChild(info);
  
      // Event listener for clicking on a card
      card.addEventListener('click', function() {
        var detailsVisible = details.style.display === 'block';
        details.style.display = detailsVisible ? 'none' : 'block';
      });
  
      return card;
    }
  
    // Append movies to container
    movies.forEach(function(movie) {
      var movieCard = createMovieCard(movie);
      movieContainer.appendChild(movieCard);
    });
  
    // Search functionality
    document.getElementById('search-input').addEventListener('input', function(e) {
      var searchQuery = e.target.value.toLowerCase();
      document.querySelectorAll('.movie-card').forEach(function(card) {
        var title = card.querySelector('.movie-title').textContent.toLowerCase();
        card.style.display = title.includes(searchQuery) ? 'flex' : 'none';
      });
    });
  });
  