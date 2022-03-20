import "./App.css";
import React from "react";
import TrackList from "./TrackList";
import Form from "./Form";
import Stats from "./Stats";

const HOST = `http://127.0.0.1:3000`;

class App extends React.Component {
    constructor(props) {
        super(props);

        this.handleFormChange = this.handleFormChange.bind(this);

        this.state = {
            totalResults: 0,
            totalTracks: 0,
            form: {
                query: "",
                genres: "",
                releaseDate: "2020-01-01",

                minTempo: 80,
                maxTempo: 210,
                showColumnTempo: "true",

                minPopularity: 0,
                maxPopularity: 100,
                showColumnPopularity: "true",

                minMainArtistPopularity: 1,
                maxMainArtistPopularity: 100,
                showColumnMainArtistPopularity: "true",

                minDanceability: 0,
                maxDanceability: 1000,
                showColumnDanceability: "true",

                minEnergy: 0,
                maxEnergy: 1000,
                showColumnEnergy: "true",

                minSpeechiness: 0,
                maxSpeechiness: 1000,
                showColumnSpeechiness: "true",

                minAcousticness: 0,
                maxAcousticness: 1000,
                showColumnAcousticness: "true",

                minInstrumentalness: 0,
                maxInstrumentalness: 1000,
                showColumnInstrumentalness: "true",

                minLiveness: 0,
                maxLiveness: 1000,
                showColumnLiveness: "true",

                minValence: 0,
                maxValence: 1000,
                showColumnValence: "true",

                explicit: "checked",
                key: "any",
            },
            tracks: [],
        };
    }

    fetchData() {
        const LIMIT = 100;

        let url = HOST;
        url += `/tracks`;
        url += `?select=spotify_id,all_artists,name,genres,release_date,tempo,popularity,danceability,energy,speechiness,acousticness,instrumentalness,liveness,valence,main_artist_popularity,key,preview_url`;
        url += `&order=release_date.desc,popularity.desc,spotify_id.asc`;
        url += `&limit=${LIMIT}`;
        url += `&tempo=gte.${this.state.form.minTempo}&tempo=lte.${this.state.form.maxTempo}`;
        url += `&popularity=gte.${this.state.form.minPopularity}&popularity=lte.${this.state.form.maxPopularity}`;
        url += `&main_artist_popularity=gte.${this.state.form.minMainArtistPopularity}&main_artist_popularity=lte.${this.state.form.maxMainArtistPopularity}`;
        url += `&danceability=gte.${this.state.form.minDanceability}&danceability=lte.${this.state.form.maxDanceability}`;
        url += `&energy=gte.${this.state.form.minEnergy}&energy=lte.${this.state.form.maxEnergy}`;
        url += `&speechiness=gte.${this.state.form.minSpeechiness}&speechiness=lte.${this.state.form.maxSpeechiness}`;
        url += `&acousticness=gte.${this.state.form.minAcousticness}&acousticness=lte.${this.state.form.maxAcousticness}`;
        url += `&instrumentalness=gte.${this.state.form.minInstrumentalness}&instrumentalness=lte.${this.state.form.maxInstrumentalness}`;
        url += `&liveness=gte.${this.state.form.minLiveness}&liveness=lte.${this.state.form.maxLiveness}`;
        url += `&valence=gte.${this.state.form.minValence}&valence=lte.${this.state.form.maxValence}`;
        url += `&or=(name.ilike.*${this.state.form.query}*,all_artists_string.ilike.*${this.state.form.query}*)`;
        // TODO: Split genres by space and do like=part1 or like=part2 or ...
        url += `&genres_string=ilike.*${this.state.form.genres}*`;
        url += `&release_date=gte.${this.state.form.releaseDate}`;
        if (this.state.form.key !== "any")
            url += `&key=eq.${this.state.form.key}`;

        fetch(url, {
            method: "GET",
            headers: { Prefer: "count=exact" },
        })
            .then((response) => {
                let count = response.headers.get("Content-Range");
                this.setState({ totalResults: count.split("/")[1] });
                return response.json();
            })
            .then((data) => {
                this.setState({ tracks: data });
            });
    }

    fetchTotalTracks() {
        let url = HOST;

        url += `/tracks?select=spotify_id`;
        url += `&limit=1`;
        url += `&energy=not.is.null`;

        fetch(url, {
            method: "GET",
            headers: { Prefer: "count=estimated" },
        }).then((response) => {
            let count = response.headers.get("Content-Range");
            this.setState({ totalTracks: count.split("/")[1] });
        });
    }

    // Run on first render
    componentDidMount() {
        document.getElementById("query").focus();
        this.fetchTotalTracks();
        this.fetchData();
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (this.state.form !== prevState.form) {
            this.fetchData();
        }
    }

    // Update state based on form's elements and their name
    handleFormChange(e) {
        this.setState((s) => ({
            form: {
                ...s.form,
                [e.target.name]: e.target.value,
            },
        }));
    }

    render() {
        return (
            <div className="App">
                <header className="App-header">
                    <h1>Spotify smart playlist generator</h1>
                </header>
                <div id="main">
                    <Stats
                        totalResults={this.state.totalResults}
                        totalTracks={this.state.totalTracks}
                    />
                    <Form
                        handler={this.handleFormChange}
                        values={this.state.form}
                    />
                    <TrackList
                        tracks={this.state.tracks}
                        values={this.state.form}
                    />
                </div>
            </div>
        );
    }
}

export default App;
