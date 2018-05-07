# Wikipedia Navigation Vectors
Generating Wikipedia article embeddings using Word2vec and reading
sessions. See [wiki page](https://meta.wikimedia.org/wiki/Research:Wikipedia_Navigation_Vectors)
for more details.


## How to
1. Clone this repository into stat1005:
   `git clone --recurse-submodules https://github.com/wikimedia/research-navigation-vectors`
2. Compile submodules:
   `cd research-navigation-vectors/submodules/convertvec && make && cd ../word2vec/ && make && cd ../../src`
3. Generate vectors:
   `python run.py --get_requests --get_sessions --get_vectors --start 2018-04-01 --stop 2018-04-30 --release 2018_04_01_2018_04_30 --langs wikidata --dims 100`
