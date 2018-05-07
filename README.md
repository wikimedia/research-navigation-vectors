# Wikipedia Navigation Vectors
Generating Wikipedia article embeddings using Word2vec and reading
sessions. See [wiki page](https://meta.wikimedia.org/wiki/Research:Wikipedia_Navigation_Vectors)
for more details.


## How to
1. Clone this repository into stat1005:
   `git clone --recurse-submodules https://github.com/wikimedia/research-navigation-vectors && cd research-navigation-vectors`
2. Install requirements (see `research-wmf-utils/README.md` for additional dependencies):
   `pip install -r requirements.txt && pip install -r submodules/research-wmf-utils/requirements.txt`
3. Compile `convertvec` and `word2vec`:
   `cd submodules/convertvec && make && cd ../word2vec/ && make && cd ../../src`
4. Change `config.ini` to your liking.
5. Generate vectors:
   `python run.py --get_requests --get_sessions --get_vectors --start 2018-04-01 --stop 2018-04-30 --release 2018_04_01_2018_04_30 --langs wikidata --dims 100`
