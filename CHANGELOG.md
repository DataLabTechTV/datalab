# CHANGELOG


## v0.5.0 (2025-08-05)

### Bug Fixes

- Any positive ESI is now considered competition, and is separate from intensity
  ([`25844f1`](https://github.com/DataLabTechTV/datalab/commit/25844f1433dc64148ebad3a6002968741175987e))

- Log file relative path to cwd failed when not directly contained using Path
  ([`e4f5b62`](https://github.com/DataLabTechTV/datalab/commit/e4f5b62468d240731e52f4066113eb55d96f321a))

### Chores

- Commit notebook generated during video recording
  ([`454d0dd`](https://github.com/DataLabTechTV/datalab/commit/454d0dd0b2eccf1bf2c1cbea43996a3c925d45a3))

- **deps**: Add adjustText to optionally fix rendering of overlapping node labels
  ([`36cbc33`](https://github.com/DataLabTechTV/datalab/commit/36cbc33dbbae6c8c73f29ff0f69ad3bd0de8ae72))

- **deps**: Add geopandas to plot maps
  ([`62d5ef1`](https://github.com/DataLabTechTV/datalab/commit/62d5ef1f54e970da0fa614a06f24e6363dc30d35))

- **deps**: Add jupyterlab, matplotlib, and networkx for graph data science
  ([`e29c08f`](https://github.com/DataLabTechTV/datalab/commit/e29c08fcf80f8ea6cb1a2b08732a1e1d8ca28d99))

- **deps**: Remove unneeded adjustText and add scipy back as a requirement for networkx layout
  computation
  ([`76ef5d4`](https://github.com/DataLabTechTV/datalab/commit/76ef5d40e64250da468c49327e90a5d67b96ec5c))

### Features

- Add CLI support for computing the CON score
  ([`8c94f6e`](https://github.com/DataLabTechTV/datalab/commit/8c94f6eebdda87a6233c467127ce72812eaffefc))

- Add edge arrows and node colors per label
  ([`ed56184`](https://github.com/DataLabTechTV/datalab/commit/ed561842696538ee51cc590b250dbee07f0588e6))

- Add graph analytics module, starting with a CON score
  ([`ff1f926`](https://github.com/DataLabTechTV/datalab/commit/ff1f92632e8f9073d29f1e51b89a93b797dd4bdc))

- Add graph transparency and improve labels
  ([`02dc859`](https://github.com/DataLabTechTV/datalab/commit/02dc859889c94beb7e810d953f7c083f3836f275))

- Add scale to arrow placement, add optional visualization weight
  ([`9190d2c`](https://github.com/DataLabTechTV/datalab/commit/9190d2ca25e86e19ace553f496d26fca0a53ee6d))

- Compare communities and components, study economical pressure
  ([`afceea8`](https://github.com/DataLabTechTV/datalab/commit/afceea8378a8d72bd62016b982f23ff293edba96))

- Competiton network analysis, including community and weak component analysis
  ([`62e54fd`](https://github.com/DataLabTechTV/datalab/commit/62e54fd56fa17cd3ada215401135456f9a106c9c))

- Create a basic graph theme matching DLT
  ([`3210fa5`](https://github.com/DataLabTechTV/datalab/commit/3210fa585450707b323dcf5ce9d69a44cfe9c2f7))

- Dominating and weaker economy individual analysis
  ([`986a2d6`](https://github.com/DataLabTechTV/datalab/commit/986a2d6a7c877468ce9ab7e38de54e68d9514e7b))

- Edge direction now based on common exports, from highest to lowest total amound
  ([`77325bd`](https://github.com/DataLabTechTV/datalab/commit/77325bdfa781f5a79fa122cc5d441cbb920cf09d))

- Improve graph plotting and add map plotting
  ([`266dfca`](https://github.com/DataLabTechTV/datalab/commit/266dfcaf682188ff16b8da01391c2dbcc245c893))

- Networkx graph plot helper to use with notebooks
  ([`a36b6c9`](https://github.com/DataLabTechTV/datalab/commit/a36b6c9eb482b095b62e91c162ee51ec25fb38b9))

- Revisted the whole notebook, restructuring and adding depth where needed
  ([`6a3dcb1`](https://github.com/DataLabTechTV/datalab/commit/6a3dcb1c05b3219645136bf8e654b44116fd133c))

- Script to easily convert Jupyter Notebooks to markdown
  ([`4b0c792`](https://github.com/DataLabTechTV/datalab/commit/4b0c792ae6ae56d030e814bf05bd3f08159a53e8))

- Set label w/ prop per node type and render label wo/ overlapping
  ([`8c0b6fb`](https://github.com/DataLabTechTV/datalab/commit/8c0b6fba1d2700a65346b878b1610ffa4e89d4a9))

- Setup notebook for graph data science
  ([`1d96e63`](https://github.com/DataLabTechTV/datalab/commit/1d96e63f79f68889701dbc4efefd08649f31d28b))

- Support for loading Parquet into DuckLake from Python
  ([`4035f63`](https://github.com/DataLabTechTV/datalab/commit/4035f6335698b3aef193c7b72275e9d58d9f9e4e))

- Trade alignment analysis
  ([`80d5ef1`](https://github.com/DataLabTechTV/datalab/commit/80d5ef1f702119f6d0e298d662c41bde4832172c))

- Trade alignment analysis (cont)
  ([`da6e848`](https://github.com/DataLabTechTV/datalab/commit/da6e848dff30ed7ef706fcaabbe951eb5dc09da4))

### Refactoring

- Different score reset strategy
  ([`d4d7d9d`](https://github.com/DataLabTechTV/datalab/commit/d4d7d9da4675ac86c47bb253764fef0840429683))

- No longer setting flags for dominating and weaker
  ([`d8013c4`](https://github.com/DataLabTechTV/datalab/commit/d8013c41c48645e1748649277a8b77a774641845))

- Remove unused import
  ([`65defb1`](https://github.com/DataLabTechTV/datalab/commit/65defb1d203a3a5e557a891c31ccc2dad8b826c6))

- Replace os.path ops with Path ops
  ([`84c73a9`](https://github.com/DataLabTechTV/datalab/commit/84c73a9de6fea587c95558aa84414d0c913d9c8a))

- Use kuzu extension instead of kz
  ([`d815cef`](https://github.com/DataLabTechTV/datalab/commit/d815cefe683c93636ddb4f931fefcc30c84b7b48))

- Use ref instead of hardcoded FQN
  ([`ba6de1a`](https://github.com/DataLabTechTV/datalab/commit/ba6de1afb81c635c0ca6d99edddde588588a373b))


## v0.4.0 (2025-07-16)

### Bug Fixes

- Add missing schema configs for new econ comp models
  ([`c4daafb`](https://github.com/DataLabTechTV/datalab/commit/c4daafbd574b0435041878fd210ae3951d94e1bc))

- Edges needed to be defined based on node_id, which required these changes
  ([`398ba70`](https://github.com/DataLabTechTV/datalab/commit/398ba70234661c77d32886269abd81cffc6366b6))

- Remove inexistent property
  ([`918f23a`](https://github.com/DataLabTechTV/datalab/commit/918f23ac5e2d901e448b51bc2d37456091eba3b2))

- Remove not null tests where they were not required
  ([`43efc61`](https://github.com/DataLabTechTV/datalab/commit/43efc6158b4c3789d00a409a690f9f1ce5b71d7c))

- Remove product parent relationship, as there is no multi-level data here
  ([`2d26651`](https://github.com/DataLabTechTV/datalab/commit/2d26651d7ccfca977887ca040ecf2c6d8d5dc30d))

- Remove repeated country pairs in reverse order
  ([`1f2f867`](https://github.com/DataLabTechTV/datalab/commit/1f2f8676223ac381204f58e65aa37457a0bc4eed))

- Required aggregation per country and product, disregarding partner
  ([`635dc72`](https://github.com/DataLabTechTV/datalab/commit/635dc729b0a38e345d34250decce67da378393c0))

- Types and missing null strings
  ([`40a79d7`](https://github.com/DataLabTechTV/datalab/commit/40a79d7bc851a17f06329c06a63220ce27059e19))

### Chores

- Add cypher script to compute music_taste graph stats
  ([`7a0a48d`](https://github.com/DataLabTechTV/datalab/commit/7a0a48de97fadc5a3963ec608005f55c785e9545))

- Add env var for econ comp graph db
  ([`3e34e80`](https://github.com/DataLabTechTV/datalab/commit/3e34e8023a15969250faae133805f02112e0b681))

- Configs for analytics mart
  ([`40dee56`](https://github.com/DataLabTechTV/datalab/commit/40dee562661fcdbdaaa7223e9dcfca4524b761a3))

- Re-enable requests-cache with streaming
  ([`62c7dff`](https://github.com/DataLabTechTV/datalab/commit/62c7dffe4aaa1d8c0d761bff3272fff98c5943c1))

- Rename KuzuDBs to match new single-file format
  ([`0e797ae`](https://github.com/DataLabTechTV/datalab/commit/0e797aeb5cc37b77421a0d1924cfec6b12e5a245))

- Simplify music taste graph stats script
  ([`5b964fb`](https://github.com/DataLabTechTV/datalab/commit/5b964fb926a5ef56aba139bb9649c1c8f7710442))

- Upgrade explorer script to work with kuzu 0.11.0
  ([`36f6cf7`](https://github.com/DataLabTechTV/datalab/commit/36f6cf77e5a24098058185dc194a60a363f00b51))

- **deps**: Add humanize to print byte sizes in human-readable format
  ([`6238484`](https://github.com/DataLabTechTV/datalab/commit/62384843681b5cf1a104a97c9e6acfc2d03a3343))

- **deps**: Add requests cache dep
  ([`b7c5fd5`](https://github.com/DataLabTechTV/datalab/commit/b7c5fd5f89e3c80ea4e46aeed3909721f787291d))

- **deps**: Add tqdm dep for tracking download progress
  ([`5e2ba51`](https://github.com/DataLabTechTV/datalab/commit/5e2ba51b9b37658f33f2ced693359cca5cb765f3))

- **deps**: Bump up kuzu to 0.11.0
  ([`74f2f4f`](https://github.com/DataLabTechTV/datalab/commit/74f2f4f171d45653138a666137e1a34487efef65))

- **deps**: Bump up version inside uv.lock
  ([`7124ff4`](https://github.com/DataLabTechTV/datalab/commit/7124ff4b0087f8cc49dfa47833e344b8e37ce4d9))

### Documentation

- Fill-in the missing schema models for analytics, and econ_comp nodes and edges
  ([`aa65fcd`](https://github.com/DataLabTechTV/datalab/commit/aa65fcda2420ef7e4c35e08f9ad4a049d411003c))

### Features

- Add model selection CLI option to test cmd
  ([`499bac0`](https://github.com/DataLabTechTV/datalab/commit/499bac02bcd0f1eb6e405ae1ffe0ba0f884b390c))

- Aggregated view for 2020-2023 trade covering recent years
  ([`c579742`](https://github.com/DataLabTechTV/datalab/commit/c579742c9d9fe6d2c22f1c74b12239f763bfd411))

- Cli command to expunge/clean cache
  ([`f412b51`](https://github.com/DataLabTechTV/datalab/commit/f412b5161ee405217722290b334f7817625127ec))

- Complete dataset template for The Atlas of Economic Complexity
  ([`6e2cb9c`](https://github.com/DataLabTechTV/datalab/commit/6e2cb9ca6643512b09a8b3c8c5c82af566900851))

- Country and product nodes, product-country export and import edges, and product parent edges
  ([`cca6d5c`](https://github.com/DataLabTechTV/datalab/commit/cca6d5c1b631bfd57a684d0dfdc73a4874bef1aa))

- Country-country ESI calculation
  ([`0ca0346`](https://github.com/DataLabTechTV/datalab/commit/0ca03462e6c1396bc207caec28bddb0584c6a225))

- Datacite working downloader
  ([`bf09fb1`](https://github.com/DataLabTechTV/datalab/commit/bf09fb16a6ca7b980fe2b5f806e4216e690fbda4))

- Ingest country classification data
  ([`09c3ac7`](https://github.com/DataLabTechTV/datalab/commit/09c3ac7c5fa28acf994fe7712c78af41acdf6be6))

- Logic changed to account for the last 3 years in data instead of a fixed range
  ([`8599498`](https://github.com/DataLabTechTV/datalab/commit/85994988af3ae3c3283b3cba2e9247b83d020bf4))

- Move cache to shared level and add expunge function and requests cache
  ([`805511f`](https://github.com/DataLabTechTV/datalab/commit/805511f336bb7230ec7d7472e5949c337cdebcc0))

- Rename 2020-2023 to latest 3y and add schema for country-country metrics
  ([`af044f8`](https://github.com/DataLabTechTV/datalab/commit/af044f875b1509c2aea9e8f5d344ae9b691aca70))

- Select top 5% ESI country-country relations for edges
  ([`3356e4f`](https://github.com/DataLabTechTV/datalab/commit/3356e4f0095f90e5a92141fbc67428b27c16fc7f))

- Skip cache for downloads and display progress bar
  ([`039e08a`](https://github.com/DataLabTechTV/datalab/commit/039e08abc2658784e18bd5a6d54d53bd921bbeaf))

- Split ingestion into multiple modules and add dataset templates
  ([`8e3c6b8`](https://github.com/DataLabTechTV/datalab/commit/8e3c6b8be6708b03448f394b457294f550e39fa5))

- Stage transformations for TAoEC
  ([`6e082e3`](https://github.com/DataLabTechTV/datalab/commit/6e082e3bcb71fb68f5ef7ce329b9fd7b88182c65))

- Support for cache usage statistic printing
  ([`436391b`](https://github.com/DataLabTechTV/datalab/commit/436391b6dacc32bc6a4abcb5dc8f435b7b767645))

- Support for loading econ_comp graph
  ([`93396df`](https://github.com/DataLabTechTV/datalab/commit/93396dfd465d52e3efd879442c2bc74e2ac0fb3b))

### Performance Improvements

- Increase chunk size and make sure temp files are cleaned even when the script is stopped
  ([`39943df`](https://github.com/DataLabTechTV/datalab/commit/39943dfdbe596640b639250daf3dad674de01030))

### Refactoring

- Log debug message containing produced context
  ([`5917a15`](https://github.com/DataLabTechTV/datalab/commit/5917a150cb831aa485e495fb131232f7f5598c94))

- Rename context to entities when referring to entity nodes
  ([`ff6e0df`](https://github.com/DataLabTechTV/datalab/commit/ff6e0df4fdea9eb37f004a8dbab5ff890bb2f56e))

### Testing

- Ensure ESI is within a 0..1 range
  ([`d1ef5ce`](https://github.com/DataLabTechTV/datalab/commit/d1ef5ceeaac7e38b1a4d5b1b3283b07ee267a134))


## v0.3.0 (2025-07-08)

### Bug Fixes

- Add error control to the GraphRAG chain
  ([`4f015ca`](https://github.com/DataLabTechTV/datalab/commit/4f015ca309974f1623a36a5b2dfd09d6c86a5484))

### Chores

- **deps**: Add colorama to color error messages
  ([`389a8a1`](https://github.com/DataLabTechTV/datalab/commit/389a8a1399d6dfdfeefe8038b85322f5eeb22384))

### Features

- Graph rag CLI options for interactive and direct querying
  ([`8f54d81`](https://github.com/DataLabTechTV/datalab/commit/8f54d812d1e17196da01aac9c2d7e0dc1bc9e9f9))

### Refactoring

- Remove unused import
  ([`c5bfb82`](https://github.com/DataLabTechTV/datalab/commit/c5bfb825ccdea4166f4952d2fa6c8642c817008c))


## v0.2.0 (2025-07-04)

### Bug Fixes

- Correct logic for deleting vector index if exists
  ([`516b677`](https://github.com/DataLabTechTV/datalab/commit/516b67790aaed0a1b2d6d2736d52a611d7c34375))

### Chores

- Add missing word in prompt
  ([`2001d8d`](https://github.com/DataLabTechTV/datalab/commit/2001d8d76e28d788266a2b65b0d219d078e10496))

- Container names will now use the default naming schema
  ([`6d267b8`](https://github.com/DataLabTechTV/datalab/commit/6d267b873d5ce8fd07b61a3b0595cc4700f95603))

- Ensure predictable table indexing order
  ([`4547bd3`](https://github.com/DataLabTechTV/datalab/commit/4547bd31b9d6ba7c104ebc027a1ce57d163f16be))

- Graph retriever and context assembler class scaffolds
  ([`eae806d`](https://github.com/DataLabTechTV/datalab/commit/eae806d2cd5eba6e7a4384ac8c272b35ceca44a4))

- Make sure kuzudb-explorer is using a fixed image version (0.10.0 currently)
  ([`80c8aca`](https://github.com/DataLabTechTV/datalab/commit/80c8aca4f74034e69c7ca18b324289b2770a91b3))

- Path combination and scaffolding for hydrating
  ([`1c7db62`](https://github.com/DataLabTechTV/datalab/commit/1c7db625c3bd80604d67d4b9194e807b61db3314))

- Prefix log message is now debug-level
  ([`de7d708`](https://github.com/DataLabTechTV/datalab/commit/de7d708cb53280b8de149e5a3b6220e5456cd159))

- Print version from pyproject.toml via CLI argument
  ([`2fa5b86`](https://github.com/DataLabTechTV/datalab/commit/2fa5b86c8e5c5e9ae4d7d4c4a8cbee77d40bdf44))

- Remove unused semantic-release config
  ([`1692e14`](https://github.com/DataLabTechTV/datalab/commit/1692e1473e8cc5c0811a49f31555cf5ec87d37a6))

This option was set in the wrong location, so it did nothing. We don't need it.

- Replace default nomic-embed-text ollama model with phi4:latest
  ([`ee324f1`](https://github.com/DataLabTechTV/datalab/commit/ee324f1ef3b41716cabf2f5f67f4ddf9888e3772))

- Setup ollama service and add env var for default model install
  ([`4af078b`](https://github.com/DataLabTechTV/datalab/commit/4af078ba17bcffdbd23c392459f66271bab4a761))

- **deps**: Add ollama dependency
  ([`4d1608d`](https://github.com/DataLabTechTV/datalab/commit/4d1608dd05b638224773bcb91a2aadfda22e7f08))

- **deps**: Add pytest to dev deps and configure default CLI options
  ([`baabcd5`](https://github.com/DataLabTechTV/datalab/commit/baabcd5055887fd9b47f6d203eeaacf51923ce32))

- **deps**: Langchain with ollama support, and a prompt helper library
  ([`4565ec9`](https://github.com/DataLabTechTV/datalab/commit/4565ec9444ca3242f7166c2dcef4df3b69df6254))

- **deps**: Langchain-kuzu
  ([`eed603d`](https://github.com/DataLabTechTV/datalab/commit/eed603d6e331bf0bc3781c35e247bdc3fcb1a3e3))

- **deps**: More-itertools
  ([`ecb7f9c`](https://github.com/DataLabTechTV/datalab/commit/ecb7f9c6ce6df46a197630abd92b3e4023c32fb5))

### Continuous Integration

- Add missing version to semantic-version command
  ([`c6facd1`](https://github.com/DataLabTechTV/datalab/commit/c6facd16d251c97967d21c9668452dd980a93802))

- Fix call to semantic release using a function
  ([`d577a45`](https://github.com/DataLabTechTV/datalab/commit/d577a45625c46d0081242fdb911b8f1d09af742c))

- Fix changelog_file config location
  ([`b5bb8d7`](https://github.com/DataLabTechTV/datalab/commit/b5bb8d780084f955bdc234120a5f766bc685a4fc))

- Fix pyproject.toml version setting for semantic release
  ([`db96d22`](https://github.com/DataLabTechTV/datalab/commit/db96d2204984a9303a62fb58117e3ca856aec810))

- Remove redundant build option, already set on pyproject.toml
  ([`e8f6d6b`](https://github.com/DataLabTechTV/datalab/commit/e8f6d6baf47609fbd00bd5bcd2003c1e954be2d0))

### Documentation

- Add knn method info to clarify the max_distance param
  ([`0fdf01f`](https://github.com/DataLabTechTV/datalab/commit/0fdf01f37c85e99165ee2ddd465c816a2998eecd))

### Features

- Add file logging by default (and option to disable)
  ([`2f9a36e`](https://github.com/DataLabTechTV/datalab/commit/2f9a36e07a3fd895952aa9aa32c1790b4877b75e))

- Add final answer pipeline and improve interactive mode
  ([`58bff5a`](https://github.com/DataLabTechTV/datalab/commit/58bff5adb0285f43e83b117dcc668b3a6ec177c8))

- Basic prompt for graph RAG and langchain scaffolding
  ([`50173de`](https://github.com/DataLabTechTV/datalab/commit/50173de3fbee66e34e7a4c97ad9e0a53fc2b6a02))

- Combined knn step for context assembler
  ([`33b20ab`](https://github.com/DataLabTechTV/datalab/commit/33b20abcfd6983a6b8d5420cb63bad5ccf32f651))

- Context assembly based on ANN, paths to neighbors, and random walks from neighbors
  ([`9323352`](https://github.com/DataLabTechTV/datalab/commit/932335291cc4eb62d657db7a424320d9b219a8b7))

- Cypher friendly schema format
  ([`87f8171`](https://github.com/DataLabTechTV/datalab/commit/87f81711718ed77caeac1c2e89c7515f8a484c58))

- First working NER implementation based on langchain-kuzu
  ([`a743062`](https://github.com/DataLabTechTV/datalab/commit/a74306230e6f109ede1b26e0c1d6b62b7ed1c507))

- Graphrag is now a LangChain Runnable and components became methods
  ([`cd04d33`](https://github.com/DataLabTechTV/datalab/commit/cd04d33776debd768a882085119515483f639529))

- Knn query support
  ([`2bca4a0`](https://github.com/DataLabTechTV/datalab/commit/2bca4a090d3539977bc956420732b359d46cc041))

- Knn, shortest paths sampler and random walk computation for context assembler
  ([`22d4f0a`](https://github.com/DataLabTechTV/datalab/commit/22d4f0a4079d0820efa0cf52d9980dfc8817fce1))

- Kuzudb-explorer launcher script now handles different paths
  ([`4dc65a9`](https://github.com/DataLabTechTV/datalab/commit/4dc65a9406c9cf34aa82f0fb2e908bff48f31ad4))

- Lazy singleton S3 resource and bucket connection
  ([`63388a1`](https://github.com/DataLabTechTV/datalab/commit/63388a1d97dd254f45c4b253bca3c99339feb6b9))

- Ollama service with gemma3 and nomic-embed-text
  ([`83b68dd`](https://github.com/DataLabTechTV/datalab/commit/83b68dd5c23e767789c935e24cc55317a35e133d))

- Path hydration and bulk description
  ([`97ea465`](https://github.com/DataLabTechTV/datalab/commit/97ea465f721930afe64d09bb114e29d38ff1e92a))

- Return paths as interleavings of node_id and rel label
  ([`17b790a`](https://github.com/DataLabTechTV/datalab/commit/17b790ad7b5463af56ef1c409d60732fe861b7a5))

- Support for indexing embeddings
  ([`c687f81`](https://github.com/DataLabTechTV/datalab/commit/c687f81f4fbcec6aad30d3402881b2a4c62bef9d))

- **graph.ops**: Automatically add a custom embeddings column to all node tables
  ([`1900f21`](https://github.com/DataLabTechTV/datalab/commit/1900f2135b8a5be406cb38b3d4a06cbcd45fb7ce))

Closes #2

- **graph.ops**: Produce node schema with properties names and types
  ([`291d42f`](https://github.com/DataLabTechTV/datalab/commit/291d42f59914f296efffc8f54cc44df074a27e33))

### Performance Improvements

- Migrated from KuzuQAChain to a custom strategy still based on langchain-kuzu
  ([`ebce585`](https://github.com/DataLabTechTV/datalab/commit/ebce5853e1121e3fe7aba56be4107ca359828f45))

### Refactoring

- Change property match to WHERE cond and lower the temperature
  ([`f0f9198`](https://github.com/DataLabTechTV/datalab/commit/f0f919895c4079d0c88f998dbb657346666859d2))

### Testing

- Correct paths_df fixture and add missing exclude_props
  ([`c167b0c`](https://github.com/DataLabTechTV/datalab/commit/c167b0cb0dc318999d383ab2444f557487096aff))

- Invoke test for GraphRAG runnable
  ([`f724224`](https://github.com/DataLabTechTV/datalab/commit/f72422478f13505d5c9545dd1d3ec68f3346a79b))

- Move graph db check to global fixtures
  ([`d2963e3`](https://github.com/DataLabTechTV/datalab/commit/d2963e3b1027de909f64f497629004ac6a7514a3))

- Print final chain output
  ([`40f2d14`](https://github.com/DataLabTechTV/datalab/commit/40f2d14540167791e970607f6a5c06a9684278ff))

- Setup ops and paths_df to test path_descriptions()
  ([`3f3c160`](https://github.com/DataLabTechTV/datalab/commit/3f3c1602f239c9f142e3d54efd3fa991f52b5f17))

- Tests will only print logs to stderr and always use debug level
  ([`fafb3bf`](https://github.com/DataLabTechTV/datalab/commit/fafb3bfdbb854a3134b01bdb0fe1d7b47abd8611))


## v0.1.0 (2025-06-25)

### Bug Fixes

- Add node_id to all nodes
  ([`f927dcd`](https://github.com/DataLabTechTV/datalab/commit/f927dcd26b61fd50fd784a16cd1a6d983499b7f7))

- Batch should be column, not parameters
  ([`73eeb9e`](https://github.com/DataLabTechTV/datalab/commit/73eeb9effa01b51bd171be3ff7af2c682051d505))

- Condition for ignoring files during deletion
  ([`9da0e0f`](https://github.com/DataLabTechTV/datalab/commit/9da0e0f997dc63aae6251d433088c1cdf5094f2e))

The manifest.json was being deleted by mistake.

- Correct name for placeholder models
  ([`fa07609`](https://github.com/DataLabTechTV/datalab/commit/fa07609b4985d6279ffde955adfadbfef123cb5e))

feat: implement all missing edge models

- Ducklake integration using dev version for upcoming dbt-duckdb 1.4.1
  ([`effe0d7`](https://github.com/DataLabTechTV/datalab/commit/effe0d70b4ac93e2b533b740f3fd03c017ee9df5))

- Duplicate alias for source_id and target_id columns
  ([`d6b6790`](https://github.com/DataLabTechTV/datalab/commit/d6b679064d8306dad2462a2eed5787a82e9cfc67))

- Ensure tags are checked out
  ([`d833c89`](https://github.com/DataLabTechTV/datalab/commit/d833c89b015ced234f0de245f5a67093f613cc0d))

- Generate sequential node ID globally for all nodes
  ([`8d019ac`](https://github.com/DataLabTechTV/datalab/commit/8d019ac5402a472d606714318a6b56bbe6c932f2))

- Genre loading queries
  ([`abc6833`](https://github.com/DataLabTechTV/datalab/commit/abc683357df6d2cb47e0793b5b90d8246bf616d6))

refactor: reorganize models into stage and marts

feat: support for edge loading (untested)

- Genre nodes become a single table to ensure uniqueness
  ([`7ec7f03`](https://github.com/DataLabTechTV/datalab/commit/7ec7f03cc1a671eaba64f3bfa154a4a475e740ee))

- Incorrect S3 secret variable
  ([`6fa7394`](https://github.com/DataLabTechTV/datalab/commit/6fa739476c004d711a8dea3cc981c2d0626d2761))

- Missing description for playcount
  ([`c505c9c`](https://github.com/DataLabTechTV/datalab/commit/c505c9c6ce95315d89404c432ff26cff236f9601))

- Missing node ID dataset-based prefix
  ([`bfecf9f`](https://github.com/DataLabTechTV/datalab/commit/bfecf9f249186d4e6dcf1bc8f1ba65b82ea47606))

- Missing nodes prefix on ref table
  ([`58b04f5`](https://github.com/DataLabTechTV/datalab/commit/58b04f58c5eb99053090aa8fce423806c26e1d4c))

- Missing underscore after prefix
  ([`3a0d6d9`](https://github.com/DataLabTechTV/datalab/commit/3a0d6d97544f99c8b2d3d62e9a734b7490a0ced7))

- No longer defaulting to upstream dependencies
  ([`6d2d68a`](https://github.com/DataLabTechTV/datalab/commit/6d2d68aa9ad390fab108b2782c6fa4cadf6c6742))

- Regression introduced by removing key_parts
  ([`668a31c`](https://github.com/DataLabTechTV/datalab/commit/668a31cae84eab1680c029a045f60a24da142a44))

- Removed extra bracket in log message
  ([`782bcc9`](https://github.com/DataLabTechTV/datalab/commit/782bcc9cc0a16592c7405cf3ccd4e7be53678de6))

- Should be alias, not name
  ([`d03e079`](https://github.com/DataLabTechTV/datalab/commit/d03e07982e2a05a5adfe4b177a9c5172a461446f))

- Should be list of list, not list of tuple
  ([`c3b7419`](https://github.com/DataLabTechTV/datalab/commit/c3b7419c56298614548c8e56d41b1ee25740e15a))

- Sqlite prefix missing
  ([`78bae87`](https://github.com/DataLabTechTV/datalab/commit/78bae87dbab67470f93d4db0d3a5655169a02236))

- Switch to single table for genre nodes
  ([`6d5dd1f`](https://github.com/DataLabTechTV/datalab/commit/6d5dd1fdf7f38f5571a954054a703c2ae2317266))

- Update graph loading process based on new config schema
  ([`eebc677`](https://github.com/DataLabTechTV/datalab/commit/eebc677257feed5353c60e5b924ffdd6f17659d2))

- Update prune to use class prefix
  ([`49ca20f`](https://github.com/DataLabTechTV/datalab/commit/49ca20fdac51b33d29ed08737633fbcf0237f373))

- Using map instead of list per node embedding
  ([`e6f1caf`](https://github.com/DataLabTechTV/datalab/commit/e6f1cafc14fdb8811883471f1527a8efc6017ad3))

fix: add missing schema alter to add embedding property to all nodes

- Wrapper to copy from data mart via a temporary file
  ([`3cd0268`](https://github.com/DataLabTechTV/datalab/commit/3cd0268d3677f79dea02ecdf7caa3a6097369f3b))

- Wrong column name in schema
  ([`af2a693`](https://github.com/DataLabTechTV/datalab/commit/af2a693c217321d4128f29134709ca7484f0c555))

- Wrong filename case, should be RO, not ro
  ([`905a303`](https://github.com/DataLabTechTV/datalab/commit/905a303bf6c31f80ccce50e0109e7c3b314b4b99))

- Wrong model name in schema
  ([`588f3bc`](https://github.com/DataLabTechTV/datalab/commit/588f3bc36cdb1f6fdc45db15432d62e328a49e65))

- Wrong reference, missing schema prefix
  ([`701fb1d`](https://github.com/DataLabTechTV/datalab/commit/701fb1d832eb52aedae62394ded25745c7cd602a))

- Wrong variable order in log message
  ([`40cb055`](https://github.com/DataLabTechTV/datalab/commit/40cb055f586db954ec371faca1949006838b4867))

### Chores

- Add description and pandas dep
  ([`b7c40d0`](https://github.com/DataLabTechTV/datalab/commit/b7c40d0dc36dba15cffe805e849ef009a1f3e6ba))

- Add DUCKLAKE_PATH to .env
  ([`3ab2bee`](https://github.com/DataLabTechTV/datalab/commit/3ab2bee4c69f15c0325a4cff2dcfeb5e80f01bf3))

- Add kuzu as a dependency
  ([`f1e2a5c`](https://github.com/DataLabTechTV/datalab/commit/f1e2a5ce134d866411f04b469844e6c492c08873))

- Add S3 prefix for exports
  ([`88ee16c`](https://github.com/DataLabTechTV/datalab/commit/88ee16cd3636ba2d0b8d5e6d35fddc8f458abf26))

- Add solid background to diagram
  ([`7499f46`](https://github.com/DataLabTechTV/datalab/commit/7499f46d7924b78759f43519e28a72e501563df3))

- Add torch, torch-sparse, and torch-geometric deps
  ([`5ddd0f8`](https://github.com/DataLabTechTV/datalab/commit/5ddd0f8838121867ab6e785d1d61006d8801f0c6))

- Better schema name organization for graphs
  ([`948759a`](https://github.com/DataLabTechTV/datalab/commit/948759ae06c3cd55c23b298ebfff80840777f0d3))

- Click and minio deps
  ([`c6e450f`](https://github.com/DataLabTechTV/datalab/commit/c6e450f245e025055024d37153ba5cedaf9ba03b))

- Default to eu-west-1, as MinIO also defaulted to it
  ([`6afa282`](https://github.com/DataLabTechTV/datalab/commit/6afa28204728965393d7648072fd2a9a69deb620))

- Delete example models
  ([`7012b5b`](https://github.com/DataLabTechTV/datalab/commit/7012b5b64df856b25a179127662f7edf9eb91796))

- Fix version for python-semantic-release to match deps
  ([`3ff93d9`](https://github.com/DataLabTechTV/datalab/commit/3ff93d9867a267a863f5209ed91e2785a6fd9ca7))

- Github dark mode background color
  ([`ca97d44`](https://github.com/DataLabTechTV/datalab/commit/ca97d44005cca71a37733a2746c489f2faab3c34))

- Gitignore vscode directory
  ([`a2fcabd`](https://github.com/DataLabTechTV/datalab/commit/a2fcabd53521f9235d01f25e330563b891de291b))

- Initial log message for export
  ([`1207e93`](https://github.com/DataLabTechTV/datalab/commit/1207e9319ce21c5de5dc5956b866379268d4d065))

- Initial log string is now a welcome string
  ([`0edefc6`](https://github.com/DataLabTechTV/datalab/commit/0edefc6418c91991f6b5a37b0176f48e73a28059))

- Make sure we start from 0.1.0, not 1.0.0
  ([`cb2b7c5`](https://github.com/DataLabTechTV/datalab/commit/cb2b7c5e4515c2dcfd5c8fe3a88f4f9f6385ea04))

- Remove unused dep
  ([`ba09c90`](https://github.com/DataLabTechTV/datalab/commit/ba09c90ddcf6c21f5fde9da0f3870740f6ba36ea))

- Remove unused deps and update docs referring to them
  ([`7da0d24`](https://github.com/DataLabTechTV/datalab/commit/7da0d24b19a07ae25edc6337d4eb0d6f5345833c))

- Replace with official GHA for python-semantic-release
  ([`7301029`](https://github.com/DataLabTechTV/datalab/commit/7301029dc2b83755c278b2b86ab5893beff7aea7))

- Script to launch temporary docker container with KuzuDB Explorer for a database
  ([`52b617a`](https://github.com/DataLabTechTV/datalab/commit/52b617ab3fc4eb6179dd29d4d666896d83a6c7f4))

- Setup dltctl CLI tool (replaces Makefile)
  ([`405d800`](https://github.com/DataLabTechTV/datalab/commit/405d8009fb458839917156c3e2dc8ae6fc349d0f))

- Simplify node and edge schemas, using Gremlin-like notation
  ([`887dddc`](https://github.com/DataLabTechTV/datalab/commit/887dddc030de0d9e925cb1b27bf07eae4d2d7c47))

- Solid background in individual rectangles
  ([`8f68204`](https://github.com/DataLabTechTV/datalab/commit/8f6820495887a87969807cce6f4667b9fb05d3f9))

- Switch to a multi-database marts config
  ([`1cf615c`](https://github.com/DataLabTechTV/datalab/commit/1cf615c93a7b1e547472988b714ebddf9459c900))

- Temporarily removed
  ([`bd26438`](https://github.com/DataLabTechTV/datalab/commit/bd264383309094e20647beac16982c10ce4ad4a3))

Schema was outdated and was blocking dbt run.

- Update config to match multi-database marts
  ([`d47f96f`](https://github.com/DataLabTechTV/datalab/commit/d47f96fb161378f38637f45d6ca6a8bca29d6747))

- Won't use the extra command in favor of one entry point
  ([`698a3d1`](https://github.com/DataLabTechTV/datalab/commit/698a3d125aaa4d1f99cb27be18bc87083548bb75))

- **deps**: Move python-semantic-release to dev deps
  ([`9df3ed6`](https://github.com/DataLabTechTV/datalab/commit/9df3ed65d058c8ac13cd927c0b10767effc2e133))

### Documentation

- Add graph and shared
  ([`866b37c`](https://github.com/DataLabTechTV/datalab/commit/866b37c1577e4dd91d72cddb009a7fdea988b14a))

- Add specification for exports pruning
  ([`e42acbf`](https://github.com/DataLabTechTV/datalab/commit/e42acbf198efa382aad21125437ac9294ea0c7c4))

- Dependency management development instructions
  ([`2f9393f`](https://github.com/DataLabTechTV/datalab/commit/2f9393f3523a47fffeaaf9be72b7c657120789e4))

- Duckdb init script description
  ([`94b1959`](https://github.com/DataLabTechTV/datalab/commit/94b19595a1f18e5fc6ea84a0875a500149f49abd))

- End-to-end documentation
  ([`190ef1b`](https://github.com/DataLabTechTV/datalab/commit/190ef1bb5ed840de28090c3a9672a10ea49e7f15))

- Fix section links
  ([`e00a537`](https://github.com/DataLabTechTV/datalab/commit/e00a5374add7bf6abf6c35c1157659e7b5469183))

- Latest.json is now manifest.json
  ([`6cdb057`](https://github.com/DataLabTechTV/datalab/commit/6cdb057874f32fd7a0c166e7549ef1e7c0922076))

- Remove suffix from info boxes
  ([`170ebff`](https://github.com/DataLabTechTV/datalab/commit/170ebffa5c2c43b4709b5fdaa153c32e1fc0965d))

- Requirements, quick start, architecture diagram
  ([`8009821`](https://github.com/DataLabTechTV/datalab/commit/800982183defb20edd942f0e761010d177780212))

- Schemas for nodes and edges of the music graph
  ([`409b4cb`](https://github.com/DataLabTechTV/datalab/commit/409b4cb96ede819d48d745796f845834a9655843))

- Structured sections for README
  ([`5a6c128`](https://github.com/DataLabTechTV/datalab/commit/5a6c12876f697fb99a4af4d0265006f952706f9d))

- Update schema for the DSN and MSDSL datasets
  ([`9a56aaa`](https://github.com/DataLabTechTV/datalab/commit/9a56aaaa5d21419b57b0edff0b8dbcba5855bc9c))

- Update storage layout
  ([`f60d021`](https://github.com/DataLabTechTV/datalab/commit/f60d021df1b4a52cd91fcf34864d25e3845f276a))

- Update storage layout
  ([`1383bfd`](https://github.com/DataLabTechTV/datalab/commit/1383bfd5145c1ca70c5a452a1a4e03ad244fa409))

- Update storage layout and specification for the ingest command
  ([`b66cffe`](https://github.com/DataLabTechTV/datalab/commit/b66cffef16803f5c228d5e22802dbb33fe5febbf))

- Using generic dark background
  ([`85476f1`](https://github.com/DataLabTechTV/datalab/commit/85476f12b0d30f1f4ff742b3d43e8627ecb4dfb2))

### Features

- Add CLI args for read only and to reset
  ([`dbfefa8`](https://github.com/DataLabTechTV/datalab/commit/dbfefa81f9ccd9421f6e8cd5fc01fb6dac2d2b8a))

Container is now kept between sessions, unless explicitly reset.

- Backup restore can now specify source date
  ([`62a52af`](https://github.com/DataLabTechTV/datalab/commit/62a52af38fc4d05e8dda90662ed67732ec6387b9))

- Basic support for dbt run via dlctl transform
  ([`b3f6240`](https://github.com/DataLabTechTV/datalab/commit/b3f6240de443c714e199a474cd83172ded6415b3))

- Catalog backup and restore
  ([`cb87830`](https://github.com/DataLabTechTV/datalab/commit/cb878305704afd1af1719a5f9faa0e2a36f3883e))

refactor: prefix is now set when instancing Storage

feat: Storage can now upload/download files or a directory

- Create directories for DuckDB databases
  ([`3976b19`](https://github.com/DataLabTechTV/datalab/commit/3976b190fd4cb46e3500aa2302a8ee37aa3c64bb))

This way we can set the marts databases to be stored under local/marts/.

- Dbt debug option
  ([`f64313e`](https://github.com/DataLabTechTV/datalab/commit/f64313ee2e3626f85e20d2a42d83ea8a031f199d))

- Debug option controlling log level
  ([`9e5f030`](https://github.com/DataLabTechTV/datalab/commit/9e5f0304bc3f4c1c1d1cb2204a7977326fd15f94))

- Directory structure for a DuckLake lakehouse
  ([`87ed579`](https://github.com/DataLabTechTV/datalab/commit/87ed57917bf5d8f7643542ad858b11e8b696b72f))

- Dlctl tools generate-init-sql
  ([`c24ca39`](https://github.com/DataLabTechTV/datalab/commit/c24ca39aab1fa222d0e8054b2a5f0817c117f622))

This will output into local/init.sql. The scripts/init.example.sql or the gitignored
  scripts/init.sql are no longer used.

docs: add a help message to all commands

- Duckdb CLI init script to connect to the lakehouse
  ([`788691f`](https://github.com/DataLabTechTV/datalab/commit/788691f4fcba9409e940edade878072331b8c9fa))

- Error control for empty results
  ([`d5e1d65`](https://github.com/DataLabTechTV/datalab/commit/d5e1d654b25b7db7b51f874e22ba5bb5ebf96dbf))

- Exception capture for KuzuOps
  ([`6a2a498`](https://github.com/DataLabTechTV/datalab/commit/6a2a4981580945c66ab2ed16a0c9f4b4a4896ff8))

- Export scripts that output parquet
  ([`218bfeb`](https://github.com/DataLabTechTV/datalab/commit/218bfebfdd588bdd433b3e3f2c98bcd6a785fcd5))

- Frp node embedding over KuzuDB
  ([`68a7514`](https://github.com/DataLabTechTV/datalab/commit/68a7514e6929d40e9669cb2b737fb4f67e91272e))

- Improve backups listing
  ([`8c5284d`](https://github.com/DataLabTechTV/datalab/commit/8c5284dae6deff93de40e2570e1e6de23113ad29))

- Load all genres tables based on shared macro
  ([`ed8197b`](https://github.com/DataLabTechTV/datalab/commit/ed8197bdbea62e9638dd3cab682363d5c31e910e))

- Ls and prune for ingest and exports
  ([`e9a3505`](https://github.com/DataLabTechTV/datalab/commit/e9a3505c88861971c2bfe49c31d35977e0e0c958))

fix: add missing manifest to exports

fix: ignored file filtering

fix: add prefix logic to upload manifest

- Minio docker service
  ([`00f2dab`](https://github.com/DataLabTechTV/datalab/commit/00f2dab8764deabfdee43f979657d27a28d9a5b7))

- Node embedding computation and graph DB update
  ([`579b477`](https://github.com/DataLabTechTV/datalab/commit/579b4770c049a06983bb9ae80add7d3dc22fe093))

- Option to use latest export when loading a graph
  ([`3b00439`](https://github.com/DataLabTechTV/datalab/commit/3b004390cac238452b3dbdaec1c633d6a2cc3a56))

refactor: exports now stored using the same directory structure as marts

- Qol for CLI parameters and defaults, and logging
  ([`c6ee19b`](https://github.com/DataLabTechTV/datalab/commit/c6ee19ba65908069b06d22a89640dc5af53a3d7c))

- Quality of life for explorer startup and exit
  ([`4562ab6`](https://github.com/DataLabTechTV/datalab/commit/4562ab65721efdc48391d2a54ecdf4a7fb792a8b))

- Replace export scripts with a load method from the new graph package
  ([`8c356d6`](https://github.com/DataLabTechTV/datalab/commit/8c356d66d76c4e8cabca05ef6bacb15502d7445c))

- Replace load_dotenv with proper validation via environs
  ([`aacb1a3`](https://github.com/DataLabTechTV/datalab/commit/aacb1a3a7e26449553378e56824f54c91e92f68e))

refactor: centralize storage and environment variable loading into shared packages

refactor: improve function naming and arguments

feat: set placeholder upload as optional

refactor: rename lastest.json to manifest.json

feat: storage now implements an env var loader with latest file paths

- Schema name without the 'main_' prefix
  ([`37b0bff`](https://github.com/DataLabTechTV/datalab/commit/37b0bff909e6f20f38d12957b27c86cb9d71b291))

- Setup semantic releases
  ([`ef856fd`](https://github.com/DataLabTechTV/datalab/commit/ef856fd28a8d6820241431bb55d5fb2df731c225))

- Strip schema name from table name
  ([`fc83dfa`](https://github.com/DataLabTechTV/datalab/commit/fc83dfa3e9dd69d1ba63f012aeec372e1782ba19))

- Stubs for node computation embedding command
  ([`f220fc2`](https://github.com/DataLabTechTV/datalab/commit/f220fc2a81c5e81d465b26313d09c66eea19e251))

- Support file downloading from object storage
  ([`eff8a8b`](https://github.com/DataLabTechTV/datalab/commit/eff8a8b2e59b24bb854a0df78037134dac488c21))

- Support for kaggle and hugging face ingestion
  ([`39f8fb5`](https://github.com/DataLabTechTV/datalab/commit/39f8fb58e43a16ede7c6d4d23e0c4b449f5ffc24))

- Support for manual dataset ingestion
  ([`3b6c3d1`](https://github.com/DataLabTechTV/datalab/commit/3b6c3d18b4f848da7d2adeebef95af6ae873ebdc))

- Support for running a subset of models during transform
  ([`4986aee`](https://github.com/DataLabTechTV/datalab/commit/4986aeea0ab6b7eea4fc8c1e34d87c9a010721fb))

### Performance Improvements

- Switch to UNPIVOT strategy
  ([`51059e2`](https://github.com/DataLabTechTV/datalab/commit/51059e27b0dd3844e95f3af1e3160cfef4e7da1a))

### Refactoring

- Better naming scheme for graph schemas, and node and edge tables
  ([`1716d17`](https://github.com/DataLabTechTV/datalab/commit/1716d17a8a6dee7b222ef3c7e1244b2b3f663e8e))

- Cleanup file to avoid inline comments
  ([`498534d`](https://github.com/DataLabTechTV/datalab/commit/498534d5b52327653a708d684855b831d6f3bd83))

- Con is now conn
  ([`cc99988`](https://github.com/DataLabTechTV/datalab/commit/cc99988c570a81224ea50a0b1d3e7a38c787d2be))

- Embedding batch updates now handled directly by NodeEmbedder
  ([`5dc6e51`](https://github.com/DataLabTechTV/datalab/commit/5dc6e5148f042cb534bb71408d91f9fa55fee600))

- Genres/nodes and edges are now stored in the graphs mart
  ([`9963909`](https://github.com/DataLabTechTV/datalab/commit/9963909b1966daa10a4bd16baf76628559a9b637))

docs: schemas updated with node and edge information and basic testing

- Graph manager is now ops
  ([`c84dbf5`](https://github.com/DataLabTechTV/datalab/commit/c84dbf58cc323a2db0c40ae22a76d9b5c24e4057))

- Improved docs and better naming for DuckLake DBs
  ([`0b8097d`](https://github.com/DataLabTechTV/datalab/commit/0b8097dbb3fc2de935a10aea77f019b5fa5dfb46))

- Latest export is now default, but re-exporting can be forced
  ([`54324c3`](https://github.com/DataLabTechTV/datalab/commit/54324c3a917b9440946a4f5ecc6c7974b2131828))

- Log exception message without stack trace
  ([`1d52f40`](https://github.com/DataLabTechTV/datalab/commit/1d52f40e0a6302c6587830a1b8e47ffba820e846))

- Name source and target columns
  ([`b0c83fd`](https://github.com/DataLabTechTV/datalab/commit/b0c83fd31f8b1e3ac2ed1285799d49b5c8ddc203))

feat: cast node IDs to integer

- Nodes and edges directories to match graph DB loading format
  ([`86ef29e`](https://github.com/DataLabTechTV/datalab/commit/86ef29e0f78de3c0fd0c0bcaa4c35fd6e017c607))

feat: million song dataset, spotify and lastfm transformation

feat: improve deezer genres and edges mart table schemas

- Overall simplification of the explore graph script
  ([`94b0bb0`](https://github.com/DataLabTechTV/datalab/commit/94b0bb0d131c7ba0b82b08424e27262c2a7c90a4))

- Qol, log message in lower case after colon
  ([`76cccc8`](https://github.com/DataLabTechTV/datalab/commit/76cccc82f780b56653fa002c57bdd078fb492fb5))

- Qol, log message now includes epoch
  ([`51c96cd`](https://github.com/DataLabTechTV/datalab/commit/51c96cd334954ddc04a376ccace39dc5b6be4a39))

- Remove source from edges
  ([`ca15947`](https://github.com/DataLabTechTV/datalab/commit/ca159477c97fe52184d9554e98260b485c6384f6))

- Remove uneeded echos
  ([`a5f86a0`](https://github.com/DataLabTechTV/datalab/commit/a5f86a0bc9c7ba85d242b89366a4194f9df73466))

- Rename models to include a schema prefix
  ([`dd263ab`](https://github.com/DataLabTechTV/datalab/commit/dd263abfb30118c5308ad2abf9ed283ff1acea91))

feat: implement missing node models

- Rename music graph back to music_taste
  ([`d0d7a57`](https://github.com/DataLabTechTV/datalab/commit/d0d7a5741505ebfe856bf8faab3409a5599ddb5a))

- S3 access key and secret renamed to reflect common naming schema
  ([`d00a4c9`](https://github.com/DataLabTechTV/datalab/commit/d00a4c96295b6472730e3b9d45e1e75e7bad1329))

- Table materialization is now default
  ([`35dc856`](https://github.com/DataLabTechTV/datalab/commit/35dc856e59c933956e156a6358f8a9d1c0e06840))

- Taking advantage of parents accessor
  ([`1038678`](https://github.com/DataLabTechTV/datalab/commit/1038678f9742da018647ea87a3fcf61f924b52e1))

- Tools and utils moved to shared
  ([`3900df1`](https://github.com/DataLabTechTV/datalab/commit/3900df16c399a5a3c5ee9dd15c5ab88e215f465c))

feat: init SQL can now be returned as a string

fix: lakehouse relied on an init script that's no longer there

Using generate_init_sql to produce a string with the required SQL instead.

chore: uncommended code that didn't run due to KuzuDB bug

- Util is now templates for clarity
  ([`7518c06`](https://github.com/DataLabTechTV/datalab/commit/7518c06212831493d6303382d740654f9ee81064))

chore: groups no longer invokable without arguments

This had been added for better performance, but did nothing.

refactor: split export into standalone feature

Extracted from graph load and integrated into the existing export command (renamed from exports to
  export).

### Testing

- Column only contains positive integers
  ([`c4459fb`](https://github.com/DataLabTechTV/datalab/commit/c4459fbbbf1ca92010c8b8b63400a589bf44b0b7))

- List/array not null or empty
  ([`3ff573f`](https://github.com/DataLabTechTV/datalab/commit/3ff573f93d3bfc37b13d5c70569bf6317fb9ae36))

- Make sure node IDs are globally unique
  ([`5d9a1ff`](https://github.com/DataLabTechTV/datalab/commit/5d9a1ffaa550b19c3882c0919412349f8ab9528a))
