import "./App.css";
import React, { useEffect, useState } from "react";

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

    const serializeFormsInputs = (form) => {
        var params = [];
        for (var i = 0; i < form.elements.length; i++) {
            var field = form.elements[i];
            // Is there a const list of HTML elements
            // to be used here, maybe browser sensitive?
            if ("INPUT" === field.tagName) {
                params[field.name] = field.value;
            }
        }
        return params;
    };

    const handleOnChange = () => {
        const form = document.getElementById("form");
        const params = serializeFormsInputs(form);
        fetchData(params);
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
                <form className="pure-form" id="form">
                    <fieldset>
                        <legend>Search for tracks</legend>
                        <label htmlFor="input">Artist or title</label>
                        <input
                            type="text"
                            id="query"
                            name="query"
                            onChange={handleOnChange}
                            label="Search track"
                        />
                        <label htmlFor="released">Released</label>
                        <input
                            type="date"
                            id="released"
                            name="released"
                            onChange={handleOnChange}
                            label="Released"
                        />
                        <label htmlFor="min-bpm">Min. BPM</label>
                        <input
                            type="number"
                            id="min-bpm"
                            name="min-bpm"
                            onChange={handleOnChange}
                            label="Min. BPM s"
                        />
                        <label htmlFor="max-bpm">Max. BPM</label>
                        <input
                            type="number"
                            id="max-bpm"
                            name="max-bpm"
                            onChange={handleOnChange}
                            label="Max. BPM s"
                        />
                        <label htmlFor="genre">Genre</label>
                        <input
                            type="text"
                            id="genre"
                            name="genre"
                            onChange={handleOnChange}
                            label="Genre"
                        />
                        <label htmlFor="explicit">
                            <input
                                type="checkbox"
                                id="explicit"
                                name="explicit"
                                onChange={handleOnChange}
                                label="Explicit"
                            />
                            Explicit
                        </label>
                        <button
                            type="submit"
                            name="submit"
                            className="pure-button pure-button-primary"
                        >
                            Search
                        </button>
                    </fieldset>
                </form>
                <div id="tracks">
                    <h2>Tracks</h2>

                    {tracks.length > 0 && (
                        <table className="pure-table pure-table-bordered pure-table-striped">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Play</th>
                                    {/* <th>Main artist</th> */}
                                    <th>Artists</th>
                                    <th>Title</th>
                                    <th>Genres</th>
                                    <th>Release date</th>
                                    <th>Tempo</th>
                                    <th>Key</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tracks.map((track, i) => (
                                    <tr key={track.spotify_id}>
                                        <td>{i + 1}</td>
                                        <td>
                                            <a href={track.preview_url}>PLAY</a>
                                        </td>
                                        {/* <td>{track.main_artist}</td> */}
                                        <td>
                                            {track.all_artists.map(
                                                (artist, i) => (
                                                    <span key={i}>
                                                        {i > 0 && ", "}
                                                        {artist}
                                                    </span>
                                                )
                                            )}
                                        </td>
                                        <td>{track.name}</td>
                                        <td>
                                            {track.genres.map((genre, i) => (
                                                <span key={i}>
                                                    {i > 0 && ", "}
                                                    {genre}
                                                </span>
                                            ))}
                                        </td>

                                        <td>{track.release_date}</td>
                                        <td>{track.tempo}</td>
                                        <td>{track.key}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;
