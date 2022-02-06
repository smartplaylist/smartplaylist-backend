# spotify-grabtrack

## Usage

1. `docker build -t sgt .`
1. `docker run -ti --rm  -v $(pwd)/src:/usr/src/app  --name app sgt`
1. `docker run -ti --rm  -v $(pwd)/src:/usr/src/app  --name app sgt sh --login`
