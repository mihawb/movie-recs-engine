# Movie recommendations engine

Recommendation engine based on Gremlin graph database with Azure Cosmos DB, deployed as Flask REST API with Azure App Service.  
Movie similarity is based on:
* cosine similarity between each pair of plots, calculated with Hadoop Streaming
* number of similar actors starring
* number of similar genres (TMDB allows more than one)  
  
## Implementation details
Check out [Half-way report](https://github.com/mihawb/movie-recs-engine/blob/main/reports/halfway_report.pdf) to see detiled description of engine's inner workings.  
Check out [Final report](https://github.com/mihawb/movie-recs-engine/blob/main/reports/final_report.pdf) to see the engine in action.

### Miscellaneous usage instructions
How to connect to Azure Cosmos DB for Gremlin with Python or Java: [link](https://learn.microsoft.com/en-us/azure/cosmos-db/gremlin/quickstart-python)
  
How to add ssh key on Windows
```
cat $HOME/.ssh/id_ed25519.pub | ssh username@host "cat >> .ssh/authorized_keys"
```

### Gremlin graph database schema
![gremlin_relations](https://github.com/mihawb/movie-recs-engine/assets/46073943/5eddca31-ad01-4e66-9008-46ea821a6651)

