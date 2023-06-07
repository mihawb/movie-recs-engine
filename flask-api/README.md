# movie-rex API

### `/api/recommendations`
Takes a list of movie IDs and returns a list of recommendations' IDs.
Returns an empty list on a cold start (empty input).
Sample query: [`/api/recommendations?id=m238&id=m80`](https://movie-rex.azurewebsites.net/api/recommendations?id=m238&id=m80)
```
[
	"m15804",
	"m8422",
	"m25376",
	"m152742",
	"m6075",
	"m1280",
	"m678",
	"m8073",
	"m17057",
	"m3133"
]
```

### `/api/rexwithinfo`
Same business logic as above, with human-readable response format.
Sample query: [`/api/rexwithinfo?id=m238&id=m80`](https://movie-rex.azurewebsites.net/api/rexwithinfo?id=m238&id=m80)
```
[
	{
		"genres": [
			"Crime",
			"Drama",
			"Romance"
		],
		"id": "m15804",
		"release_date": "1991-07-27",
		"title": "A Brighter Summer Day"
	},
	{
		"genres": [
			"Crime",
			"Drama",
			"Romance"
		],
		"id": "m8422",
		"release_date": "1960-10-06",
		"title": "Rocco and His Brothers"
},
	...
]
```

### `/api/info`
Returns all vertex properties from Gremlin DB. Is vectorized.
Sample query: [`/api/info?id=m49051)`](https://movie-rex.azurewebsites.net/api/info?id=m49051)
```
[
	{
		"adult": false,
		"backdrop_path": "/xyXmtuvsoM5J3yNad0nvcetpBdY.jpg",
		"genre_ids": [
			12,
			14,
			28
		],
		"genres": [
			"Adventure",
			"Fantasy",
			"Action"
		],
		"id": "m49051",
		"label": "movie",
		"original_language": "en",
		"original_title": "The Hobbit: An Unexpected Journey",
		"pk": "pk",
		"popularity": 49.254,
		"poster_path": "/yHA9Fc37VmpUA5UncTxxo3rTGVA.jpg",
		"release_date": "2012-11-26",
		"title": "The Hobbit: An Unexpected Journey",
		"video": false,
		"vote_average": 7.3,
		"vote_count": 17028
	}
]
```

### `/api/random`
`count` defaults to `20`
Returns a list of movie objects, as seen in `/api/info`. Could be used as a starting point for a hypothetical external module or website.
Sample query: [`/api/random?count=13`](https://movie-rex.azurewebsites.net/api/random?count=13) (click and check out in browser)
