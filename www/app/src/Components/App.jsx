import "./App.css";
import React, { useEffect, useState } from "react";
import TrackList from "./TrackList";
import Form from "./Form";

class App extends React.Component {
    constructor(props) {
        super(props);

        this.handleFormChange = this.handleFormChange.bind(this);
        // this.fetchData = this.fetchData.bind(this);

        this.state = {
            form: {
                query: "",
                genres: "",
                releaseDate: "2022-01-01",

                minTempo: 121,
                maxTempo: 139,
                showColumnTempo: true,

                minPopularity: 0,
                maxPopularity: 100,
                showColumnPopularity: true,

                minMainArtistPopularity: 18,
                maxMainArtistPopularity: 89,
                showColumnMainArtistPopularity: true,

                explicit: "checked",
                key: "any",
            },
            tracks: [],
        };
    }

    fetchData() {
        const HOST = `http://127.0.0.1:3000`;
        const LIMIT = 100;

        let url = HOST;
        url += `/tracks`;
        url += `?select=spotify_id,all_artists,name,genres,release_date,tempo,popularity,main_artist_popularity,key,preview_url`;
        url += `&order=release_date.desc,popularity.desc,spotify_id.asc`;
        url += `&limit=${LIMIT}`;
        url += `&tempo=gte.${this.state.form.minTempo}&tempo=lte.${this.state.form.maxTempo}`;
        url += `&popularity=gte.${this.state.form.minPopularity}&popularity=lte.${this.state.form.maxPopularity}`;
        url += `&main_artist_popularity=gte.${this.state.form.minMainArtistPopularity}&main_artist_popularity=lte.${this.state.form.maxMainArtistPopularity}`;
        url += `&or=(name.ilike.*${this.state.form.query}*,all_artists_string.ilike.*${this.state.form.query}*)`;
        // TODO: Split genres by space and do like=part1 or like=part2 or ...
        url += `&genres_string=ilike.*${this.state.form.genres}*`;
        url += `&release_date=gte.${this.state.form.releaseDate}`;
        if (this.state.form.key !== "any")
            url += `&key=eq.${this.state.form.key}`;

        fetch(url)
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                this.setState({ tracks: data });
            });
    }

    // Run on first render
    componentDidMount() {
        document.getElementById("query").focus();
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
