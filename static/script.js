document.addEventListener('DOMContentLoaded', function() {
  var movieContainer = document.getElementById('movie-container');

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

      card.addEventListener('click', function() {
          var detailsVisible = details.style.display === 'block';
          details.style.display = detailsVisible ? 'none' : 'block';
      });

      return card;
  }

  function showModal(movies) {
      var modal = document.createElement('div');
      modal.className = 'modal';

      var modalContent = document.createElement('div');
      modalContent.className = 'modal-content';

      movies.forEach(movie => {
          var p = document.createElement('p');
          p.textContent = movie;
          modalContent.appendChild(p);
      });

      var closeBtn = document.createElement('span');
      closeBtn.className = 'close';
      closeBtn.innerHTML = '&times;';
      closeBtn.onclick = function() {
          modal.style.display = 'none';
      };

      modal.appendChild(modalContent);
      modalContent.appendChild(closeBtn);
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
                    showModal(data);
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
                        showModal(data);
                    });
            }
        }
    });
});
