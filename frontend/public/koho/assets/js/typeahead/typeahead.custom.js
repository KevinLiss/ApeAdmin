(function($) {
  var substringMatcher = function(strs) {
    return function findMatches(q, cb) {
      var matches, substringRegex;
      matches = [];
      substrRegex = new RegExp(q, 'i');
      $.each(strs, function(i, str) {
        if (substrRegex.test(str)) {
          matches.push(str);
        }
      });
      cb(matches);
    };
  };
  var states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
    'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii',
    'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
    'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
    'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
    'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
  ];
  $('#the-basics .typeahead').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
      },
      {
        name: 'states',
        source: substringMatcher(states)
      });
  var states = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: states
  });
  $('#bloodhound .typeahead').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
      },
      {
        name: 'states',
        source: states
      });
  var countries = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '../assets/js/typeahead/data/countries.json'
  });
  $('#prefetch .typeahead').typeahead(null, {
    name: 'countries',
    source: countries
  });
  var bestPictures = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: './../assets/js/typeahead/data/films/post_1960.json',
    remote: {
      url: '../assets/js/typeahead/data/films/queries/%QUERY.json',
      wildcard: '%QUERY'
    }
  });
  $('#remote .typeahead').typeahead(null, {
    name: 'best-pictures',
    display: 'value',
    source: bestPictures
  });
  var nflTeams = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('team'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    identify: function(obj) { return obj.team; },
    prefetch: '../assets/js/typeahead/data/nfl.json'
  });
  function nflTeamsWithDefaults(q, sync) {
    if (q === '') {
      sync(nflTeams.get('Detroit Lions', 'Green Bay Packers', 'Chicago Bears'));
    }
    else {
      nflTeams.search(q, sync);
    }
  }
  $('#default-suggestions .typeahead').typeahead({
        minLength: 0,
        highlight: true
      },
      {
        name: 'nfl-teams',
        display: 'team',
        source: nflTeamsWithDefaults
      });
  $('#custom-templates .typeahead').typeahead(null, {
    name: 'best-pictures',
    display: 'value',
    source: bestPictures,
    templates: {
      empty: [
        '<div class="empty-message">',
        'unable to find any Best Picture winners that match the current query',
        '</div>'
      ].join('\n'),
      suggestion: Handlebars.compile('<div><span>{{value}}</span> – {{year}}</div>')
    }
  });
  var nbaTeams = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('team'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '../assets/js/typeahead/data/nba.json'
  });
  var nhlTeams = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('team'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '../assets/js/typeahead/data/nhl.json'
  });
  $('#multiple-datasets .typeahead').typeahead({
        highlight: true
      },
      {
        name: 'nba-teams',
        display: 'team',
        source: nbaTeams,
        templates: {
          header: '<h3 class="league-name">NBA Teams</h3>'
        }
      },
      {
        name: 'nhl-teams',
        display: 'team',
        source: nhlTeams,
        templates: {
          header: '<h3 class="league-name">NHL Teams</h3>'
        }
      });
  $('#scrollable-dropdown-menu .typeahead').typeahead(null, {
    name: 'countries',
    limit: 10,
    source: countries
  });
  var arabicPhrases = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: [
      "India",
      "USA",
      "Australia",
      "UEA",
      "China"
    ]
  });
  $('#rtl-support .typeahead').typeahead({
        hint: false
      },
      {
        name: 'arabic-phrases',
        source: arabicPhrases
      });
})(jQuery);