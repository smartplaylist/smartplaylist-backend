import "./App.css";
import React, { useEffect, useState } from "react";
import TrackList from "./TrackList";
import Form from "./Form";

const DEFAULT_RELEASED_MONTHS_AGO = 3;

class App extends React.Component {
    constructor(props) {
        super(props);

        this.handleFormChange = this.handleFormChange.bind(this);
        // this.fetchData = this.fetchData.bind(this);

        this.state = {
            form: {
                query: "",
                releaseDate: this.getDefaultRealeaseDate(),
                minTempo: "121",
                maxTempo: "139",
                genres: "",
                explicit: "checked",
                key: "any",
            },
            tracks: [],
        };
    }

    getDefaultRealeaseDate = () => {
        let released = new Date();
        released.setMonth(released.getMonth() - DEFAULT_RELEASED_MONTHS_AGO);
        return (
            released.getFullYear() +
            "-" +
            released.getMonth() +
            "-" +
            released.getDate()
        );
    };

    fetchData() {
        const HOST = `http://127.0.0.1:3000`;
        const LIMIT = 100;

        let url = HOST;
        url += `/tracks`;
        url += `?select=spotify_id,all_artists,name,genres,release_date,tempo,key,preview_url`;
        url += `&order=release_date.desc,spotify_id.asc`;
        url += `&limit=${LIMIT}`;
        url += `&tempo=gt.${this.state.form.minTempo}&tempo=lt.${this.state.form.maxTempo}`;
        url += `&or=(name.ilike.*${this.state.form.query}*,main_artist.ilike.*${this.state.form.query}*)`;
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
                    <TrackList tracks={this.state.tracks} />
                </div>
            </div>
        );
    }
}

export default App;
