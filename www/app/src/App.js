import "./App.css";
import React, { useEffect, useState } from "react";
import TrackList from "./TrackList";
import Form from "./Form";

function App() {
    const [tracks, setTracks] = useState([]);

    const fetchData = (params) => {
        const host = `http://127.0.0.1:3000`;
        var url = "";

        url += host;
        url += `/tracks`;
        url += `?select=spotify_id,all_artists,name,genres,release_date,tempo,key,preview_url`;

        url += `&tempo=gt.${params["min-bpm"]}&tempo=lt.${params["max-bpm"]}`;
        url += `&or=(name.ilike.*${params["query"]}*,main_artist.ilike.*${params["query"]}*)`;
        url += `&genres_string=ilike.*${params["genre"]}*`;
        url += `&release_date=gte.${params["released"]}`;
        url += `&limit=100`;

        fetch(url)
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                setTracks(data);
            });
    };

    // Run on first render
    useEffect(() => {
        document.getElementById("query").focus();
        const initialValues = {
            query: "",
            genre: "",
            "min-bpm": 120,
            "max-bpm": 140,
            released: "2021-01-01",
        };

        fetchData(initialValues);
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <h1>Spotify smart playlist generator</h1>
            </header>
            <div id="main">
                <Form handler={fetchData} />
                <TrackList tracks={tracks} />
            </div>
        </div>
    );
}

export default App;
